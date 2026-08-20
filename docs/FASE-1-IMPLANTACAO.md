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

O arquivo versionado (`workflow/vixeee-publicador-v3.json`) referencia
`$env.IG_TOKEN` e companhia. Para isso funcionar, as variáveis precisam existir
**dentro do container** — o que exige recriá-lo (Bloco C).

**Mas dá para implantar a Fase 1 sem esperar o Bloco C.** Gere uma versão com os
valores embutidos, localmente, e importe essa:

```bash
export IG_USER_ID=...  IG_TOKEN=...  TELEGRAM_BOT_TOKEN=...
python workflow/gen_workflow_v3.py --credenciais literal --saida /tmp/v3-literal.json
```

> 🔴 O arquivo gerado nesse modo **contém as credenciais**. Gere fora do
> repositório (ex.: `/tmp`), use, e apague. Nunca commite.

| Caminho | Quando usar |
|---|---|
| **literal** | agora — implanta a Fase 1 sem mexer no container |
| **env** | depois do Bloco C, quando o container tiver as variáveis |

Isso **desacopla a Fase 1 do Bloco C**: nenhuma recriação de container é necessária
para colher o benefício.

---

## Passo a passo

### 1. Confirmar a versão do n8n (30 segundos)

```bash
sudo docker exec n8n n8n --version
```

Anote o resultado. Se der algum problema no import, é a primeira informação útil.

### 2. Gerar e enviar o arquivo

No PC, gere em modo `literal` (comando acima), e envie para a VM:

```powershell
scp -i "$env:USERPROFILE\.ssh\id_ed25519" /tmp/v3-literal.json ubuntu@<IP>:~/v3.json
```

### 3. Importar — sem ativar

```bash
sudo docker cp ~/v3.json n8n:/home/node/v3.json
sudo docker exec n8n n8n import:workflow --input=/home/node/v3.json
sudo docker exec n8n rm /home/node/v3.json
```

O v3 nasce com `active: false`. **Nada muda no que está publicando.**

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
   Se vierem vazios no modo `env`, esta instância bloqueia `$env` → use o modo
   `literal` ou crie Credentials na interface.

Pare aí. Não execute os nós de publicação.

### 5. Virar a chave (janela após 19h30)

```bash
sudo docker exec n8n n8n update:workflow --id=vixeeepub03 --active=true
sudo docker exec n8n n8n update:workflow --id=vixeeepub01 --active=false
sudo docker restart n8n
sleep 110
```

> O boot leva ~90–100 s nesta VM (`docs/RESTRICOES-N8N.md`, item 4).

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
