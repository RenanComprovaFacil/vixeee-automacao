# Fase 1 — Implantação do workflow v3 (orientado a dados)

> **O que muda:** trocar a semana de produtos deixa de ser "abrir túnel SSH, editar
> 7 nós, salvar" e passa a ser **um commit** no `dados/semana.json`.
>
> **Risco:** baixo. O v3 tem **id e caminho de webhook diferentes** do que está em
> produção — os dois convivem. O `vixeeepub01` continua publicando até você decidir
> virar a chave, e continua sendo o rollback.

---

## O que o v3 faz de diferente

| | v2 (em produção) | v3 (novo) |
|---|---|---|
| Nós | 23 | **12** |
| Origem dos dados | 7 nós `Set` estáticos | 1 `HTTP Request` lendo o GitHub |
| Trocar a semana | editar 7 nós via SSH | **1 commit** |
| Gatilhos | 7 (um por dia) | 1 (diário às 19h) |
| Tipos de nó | scheduleTrigger, webhook, set, httpRequest, wait | **os mesmos** — nenhum tipo novo |

### Como o produto do dia é escolhido

```
produtos[$now.weekday - 1]
```

`$now.weekday` (Luxon) devolve **1 = segunda … 7 = domingo**, já no fuso da
instância — `GENERIC_TIMEZONE=America/Sao_Paulo`, verificado em 20/08/2026. O campo
`dia` do `semana.json` usa a mesma convenção, então o índice bate direto.

> ⚠️ **Invariante:** `produtos` precisa estar **ordenado por `dia`, de 1 a 7**. O
> `gen_workflow_v3.py` valida isso e se recusa a gerar o arquivo se estiver fora de
> ordem — fora de ordem, o fluxo publicaria o produto errado.

### Equivalência já comprovada

`workflow/testar_equivalencia_v3.py` simula os 7 dias e compara com os nós estáticos
do fluxo vivo. Resultado em 20/08/2026: **equivalente nos 7 dias e nos 5 campos
publicados** (`image_url`, `legenda_tg`, `legenda_ig`, `image_url_ig_post`,
`image_url_ig_story`).

```bash
python workflow/testar_equivalencia_v3.py "<caminho do export do v2>"
```

---

## Decisão: como as credenciais entram

> ⚠️ **REVISADO em 20/08/2026, depois de testar na VM.** A versão anterior deste
> guia assumia que o workflow versionado poderia referenciar `$env.IG_TOKEN`.
> **Isso não funciona nesta instância** — ver `docs/RESTRICOES-N8N.md`, item 9:
>
> ```
> NodeOperationError: access to env vars denied
> ```
>
> No n8n 2.x, `N8N_BLOCK_ENV_ACCESS_IN_NODE` vem ligado por padrão.

Restam três caminhos:

| Caminho | Token fica no workflow? | Custo |
|---|---|---|
| **A. Liberar `$env` no container** | ❌ não | recriar o container (1 comando) |
| **B. `--credenciais literal`** | ✅ sim (como hoje) | nenhum |
| **C. Credentials nativas do n8n** | ❌ não | refatorar os 5 nós HTTP + cadastro manual na UI |

**Recomendado: A.** É o único que cumpre o objetivo original da Fase 0 — tirar o
token de dentro do workflow — sem refatorar o fluxo. E o container já foi
reiniciado várias vezes hoje sem incidente, então a operação é conhecida.

### Caminho A, passo a passo

**A1. Você cria o arquivo de variáveis na VM** (é o único passo com credencial —
os valores saem do seu `SEGREDOS.local.md`):

```bash
cat > ~/n8n.env <<'FIM'
IG_USER_ID=cole_aqui
IG_TOKEN=cole_aqui
TELEGRAM_BOT_TOKEN=cole_aqui
TELEGRAM_CHAT_ID=@vixeeequebarato
GENERIC_TIMEZONE=America/Sao_Paulo
TZ=America/Sao_Paulo
N8N_SECURE_COOKIE=false
N8N_BLOCK_ENV_ACCESS_IN_NODE=false
FIM
chmod 600 ~/n8n.env
```

**A2. Recriar o container lendo esse arquivo** (nenhum segredo aparece no comando):

```bash
sudo docker stop n8n && sudo docker rm n8n
sudo docker run -d --name n8n --restart unless-stopped \
  -p 127.0.0.1:5678:5678 \
  -v /home/ubuntu/n8n/data:/home/node/.n8n \
  --env-file /home/ubuntu/n8n.env \
  docker.n8n.io/n8nio/n8n
```

> Este comando já traz duas melhorias além das credenciais: `127.0.0.1` fecha a
> porta para fora (hoje ela está publicada em `0.0.0.0` — ver `INFRA.md`) e o `TZ`
> alinha o relógio do container com Brasília.
>
> ⚠️ O `-v` está com o caminho verificado por `docker inspect`. **Não altere** —
> é ele que preserva o banco do n8n.

**A3. Conferir que pegou:**

```bash
sudo docker exec n8n printenv | grep -c "IG_TOKEN\|TELEGRAM_BOT_TOKEN"   # espera 2
sudo docker exec n8n date                                                # espera -03
```

---

## Passo a passo

### 1. Confirmar a versão do n8n (30 segundos)

```bash
sudo docker exec n8n n8n --version
```

Anote o resultado. Se der algum problema no import, é a primeira informação útil.

### 2. Enviar o arquivo do workflow

Seguindo o **caminho A**, o arquivo é o versionado — não tem segredo nenhum:

```powershell
scp -i "$env:USERPROFILE\.ssh\id_ed25519" workflow\vixeee-publicador-v3.json ubuntu@<IP>:~/v3.json
```

*(Se optar pelo caminho B, gere antes com `--credenciais literal` para um destino
fora do repositório e envie esse arquivo no lugar.)*

### 3. Importar — sem ativar

```bash
sudo docker cp ~/v3.json n8n:/home/node/v3.json
sudo docker exec n8n n8n import:workflow --input=/home/node/v3.json
sudo docker exec n8n rm /home/node/v3.json
```

O v3 nasce com `active: false`. **Nada muda no que está publicando.**

> ⚠️ **n8n 2.x versiona workflows.** Todo `import:workflow` zera o
> `activeVersionId` — reimportar um workflow ativo o derruba com
> `404 Active version not found`. A sequência obrigatória é sempre:
> **import → `update:workflow --active=true` → `docker restart` → esperar ~90 s.**
> Ver `docs/RESTRICOES-N8N.md`, item 11.

### 4. Testar SEM publicar ⚠️

> **NÃO dispare o webhook para testar.** `POST /webhook/vixeee-publicar-v3`
> **publica de verdade** no Instagram e no Telegram.

O teste seguro é na interface, pelo túnel:

```bash
ssh -L 5678:localhost:5678 ubuntu@<IP>
```

Depois, em `http://localhost:5678`, abra o workflow v3 e:

1. **Execute step** no nó `Buscar semana` → deve trazer o JSON com 7 produtos.
2. **Execute step** no nó `Produto de hoje` → confira se o produto é o do dia certo
   e se as duas URLs de arte apontam para `diaN_post.jpg` / `diaN_story.jpg`.
3. **Execute step** no nó `Config` → os 4 campos precisam vir **preenchidos**.
   Se der `access to env vars denied`, o passo A2 não foi feito (ou o
   `N8N_BLOCK_ENV_ACCESS_IN_NODE=false` não entrou no `~/n8n.env`).

Pare aí. Não execute os nós de publicação.

### 5. Virar a chave (fora da janela do post das 19h)

```bash
sudo docker exec n8n n8n update:workflow --id=vixeeepub03 --active=true
sudo docker exec n8n n8n update:workflow --id=vixeeepub01 --active=false
sudo docker restart n8n
```

Espere o boot completo (~90 s) e confirme que voltou ativo:

```bash
sudo docker logs --since 3m n8n 2>&1 | grep "Activated workflow"
```

> ⚠️ Não use `sleep` fixo para saber se subiu: o `/healthz` responde em ~35 s, mas o
> banco ainda devolve `503` e as rotas de webhook só registram depois
> (`docs/RESTRICOES-N8N.md`, item 14).

### 6. Confirmar no dia seguinte

Às 19h05, olhar o Instagram (feed + stories) e o Telegram. Três publicações = v3
aprovado.

### 7. Rollback (se algo falhar)

```bash
sudo docker exec n8n n8n update:workflow --id=vixeeepub01 --active=true
sudo docker exec n8n n8n update:workflow --id=vixeeepub03 --active=false
sudo docker restart n8n
```

O v2 nunca foi alterado — voltar é só reativar.

---

## Depois que o v3 estiver aprovado

Trocar a semana de produtos vira:

1. Editar `dados/semana.json` (ou gerar pela skill de captura, na Fase 2)
2. Subir as artes novas no `vixeee-artes` **com os mesmos nomes**
3. `git commit && git push`

Pronto. **Sem SSH, sem editar nó, sem reiniciar container.**

O `?cb={{$now.toMillis()}}` na URL quebra o cache do `raw.githubusercontent`
(TTL de ~5 min), então o commit vale já no disparo seguinte.

---

## Limitações conhecidas do v3

- **Falha silenciosa:** se o GitHub estiver fora do ar ou o `semana.json` estiver
  malformado, o fluxo simplesmente não publica e ninguém é avisado. Um alerta no
  Telegram resolve — fica para a Fase 5 (medição).
- **Sempre 7 produtos:** o desenho assume a semana cheia, um produto por dia.
- **Artes por convenção:** os nomes `diaN_post.jpg` / `diaN_story.jpg` são montados
  por expressão. Renomear as artes quebra o fluxo.
- **Publica no dia, não no produto:** se você quiser antecipar um produto, precisa
  reordenar o `semana.json` — não há como forçar um dia específico pelo webhook.
