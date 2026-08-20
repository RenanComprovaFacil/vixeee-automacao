# Infra & Acesso — Vixeee Que Barato (SEM segredos)

> Valores sensíveis (IPs, senhas, tokens, chaves, contas) NÃO estão neste arquivo — ficam em `SEGREDOS.local.md` (arquivo local, no `.gitignore`, nunca commitado). Este repositório é PÚBLICO.

## VM Oracle Cloud (Always Free)

- Instância: `n8n-afiliados`
- Shape: `VM.Standard.E2.1.Micro` (**1/8 de OCPU** com burst / 1 GB RAM) — nao e 1 OCPU inteiro
- Região: `sa-saopaulo-1`
- IP público: `<ver SEGREDOS.local.md>` — é **EFÊMERO**: muda **somente** se a instância for **parada**. Um reboot mantém o mesmo IP.
- Regra: **NÃO PARAR a instância.**
- Conta Oracle: `<ver SEGREDOS.local.md>`
- "Run Command" (Oracle Cloud Agent) **não existe** nesta instância → toda manutenção do servidor é feita por SSH.

## Acesso SSH

```
ssh -i <caminho da chave — ver SEGREDOS.local.md> ubuntu@<IP — ver SEGREDOS.local.md>
```

A chave ed25519 mora no PC do Renan.

Túnel para abrir o n8n no navegador local:

```
ssh -L 5678:localhost:5678 ubuntu@<IP>
```

Depois acessar: http://localhost:5678

## Portas

| Porta | Status | Observação |
|---|---|---|
| 22 (SSH) | Restrita pela security list | Acesso administrativo |
| 80 / 443 | Abertas no IP público | Há algum proxy/web na frente, não identificado |
| 5678 (n8n) | Fechada no IP público | Acesso só por localhost via túnel SSH |

## n8n

- Roda em container Docker chamado `n8n` (imagem `docker.n8n.io/n8nio/n8n`).
- Dados em `~/n8n/data`.
- Política de restart: `--restart unless-stopped`.
- Login do n8n: e-mail/senha do Renan (ver `SEGREDOS.local.md`). Se perder o acesso, resetar com:
  ```
  docker exec -it n8n n8n user-management:reset
  ```
- Boot do container leva **~90–100 s** após `docker restart` (a VM de 1 GB é lenta) — esperar esse tempo antes de disparar qualquer webhook, senão o n8n responde 404.

## Deploy / redeploy do workflow (via SSH na VM)

```
docker cp arquivo.json n8n:/tmp/wf.json
docker exec n8n n8n import:workflow --input=/tmp/wf.json
docker exec n8n n8n update:workflow --id=vixeeepub01 --active=true
docker restart n8n            # esperar ~100 s (boot lento)
# testar:
curl -X POST http://localhost:5678/webhook/vixeee-publicar -H 'content-type: application/json' -d '{"dia":1}'
```

Ligar/desligar o workflow:

```
docker exec n8n n8n update:workflow --id=vixeeepub01 --active=false   # (ou --active=true)
docker restart n8n
```

Exportar o workflow atual para versionar (Fase 0):

```
docker exec n8n n8n export:workflow --id=vixeeepub01 --output=/tmp/wf.json && docker cp n8n:/tmp/wf.json ./
```

Antes de commitar, **remover todos os segredos** do JSON exportado.

## GitHub (hospedagem das artes do Instagram)

- Repositório público: `RenanComprovaFacil/vixeee-artes` (branch `main`)
- Arquivos na raiz: `dia1_post.jpg` … `dia7_story.jpg`
- Padrão de URL:
  - `https://raw.githubusercontent.com/RenanComprovaFacil/vixeee-artes/main/diaN_post.jpg`
  - `https://raw.githubusercontent.com/RenanComprovaFacil/vixeee-artes/main/diaN_story.jpg`
- Regra: ao trocar as artes, manter os **mesmos nomes de arquivo** (as URLs referenciadas pelo workflow não mudam).
- Isso não é segredo — repositório e nomes de arquivo são públicos por design.

## Riscos de infra (com mitigação)

1. **Reclaim por ociosidade** — a Oracle pode recuperar/deletar VMs Always Free quando, por 7 dias seguidos, a CPU no p95 fica abaixo de 20% e a rede abaixo de 20%. Uma VM que só posta 1x/dia fica abaixo desse limiar → é preciso gerar carga sintética leve OU aceitar o risco de forma documentada.
2. **IP efêmero** — não existe conversão de IP efêmero para reservado mantendo o mesmo endereço. Migrar para IP reservado exige criar um IP **novo** (o endereço muda uma vez nesse processo).
3. **Ampere A1** — a cota gratuita caiu para 2 OCPU / 12 GB e, na região `sa-saopaulo-1`, está praticamente indisponível ("Out of host capacity"). **Não contar** com A1 para este projeto.
4. **Token do Instagram expira em ~11/10/2026** — agendar alerta e re-gerar o token antes do vencimento (o procedimento de renovação fica junto do segredo, em `SEGREDOS.local.md`).

---

# Diagnóstico verificado em 20/08/2026 (Bloco B da Fase 0)

> Tudo abaixo foi medido no servidor, não presumido. Onde a documentação anterior
> estava errada, a correção está marcada com ❌→✅.

## Comando `docker run` real do container n8n

Reconstruído a partir de `docker inspect`. **Esta é a informação que faltava** para
poder recriar o container com segurança — sem ela, recriar significaria perder o
banco do n8n (workflows + credentials).

```bash
sudo docker run -d --name n8n --restart unless-stopped \
  -p 127.0.0.1:5678:5678 \
  -v /home/ubuntu/n8n/data:/home/node/.n8n \
  -e GENERIC_TIMEZONE=America/Sao_Paulo \
  -e N8N_SECURE_COOKIE=false \
  docker.n8n.io/n8nio/n8n
```

| Item | Valor verificado |
|---|---|
| Imagem | `docker.n8n.io/n8nio/n8n` |
| Restart policy | `unless-stopped` |
| Volume (bind) | `/home/ubuntu/n8n/data` → `/home/node/.n8n` |
| Porta | `5678` |
| Env | `GENERIC_TIMEZONE=America/Sao_Paulo`, `N8N_SECURE_COOKIE=false` |
| Usuário dentro do container | `node` (sem permissão de escrita em `/tmp`) |

> ⚠️ O `-p` acima já vem **corrigido** para `127.0.0.1` — ver a seção de segurança.
> O container atual usa `-p 5678:5678` (bind em `0.0.0.0`).

## Fuso horário — pendência histórica RESOLVIDA ✅

- `GENERIC_TIMEZONE=America/Sao_Paulo` **está definida** → os gatilhos de agenda
  (`0 19 * * N`) disparam às **19h de São Paulo**. O agendamento sempre esteve certo.
- `TZ` **não** está definida → `date` dentro do container mostra UTC. Isso afeta
  apenas log e formatação de data dentro de nós, **não** o agendamento.
- Opcional (cosmético): acrescentar `-e TZ=America/Sao_Paulo` numa futura recriação,
  para o relógio do container bater com o horário de Brasília nos logs.

## ❌→✅ Correções à documentação anterior

| O que a doc dizia | O que foi medido |
|---|---|
| "n8n roda só em `localhost:5678`, porta fechada no IP público" | O Docker publica em **`0.0.0.0:5678`** (todas as interfaces). Quem bloqueia é o **Security List da Oracle**, não o Docker. |
| "Portas 80 e 443 abertas no IP público (algum proxy/web na frente)" | **Nenhuma das duas responde.** Não há proxy. |
| "Shape com 1 OCPU" | `E2.1.Micro` = **1/8 de OCPU** com burst. |

## 🔒 Segurança — camada única de proteção

A porta `5678` está publicada pelo Docker em todas as interfaces. Testado de fora em
20/08/2026: **não responde** — o Security List da Oracle bloqueia.

O risco é que essa é a **única** camada. Se a regra da Oracle for alterada, o n8n
fica exposto na internet em HTTP puro (com `N8N_SECURE_COOKIE=false`), e o workflow
em produção carrega os tokens do Instagram e do Telegram em texto puro.

**Correção recomendada** (aplicar na próxima recriação do container, Bloco C):
trocar `-p 5678:5678` por `-p 127.0.0.1:5678:5678`. Como o acesso já é feito por
túnel SSH, isso **não muda nada no uso**.

## Risco de reclaim por ociosidade — CONFIRMADO 🔴

Medido em 20/08/2026, com 7 dias e 19h de uptime:

| Critério Oracle (janela de 7 dias) | Gatilho | Medido | Situação |
|---|---|---|---|
| CPU (percentil 95) | < 20% | load `0.10 / 0.03 / 0.01` ≈ 10% | 🔴 abaixo |
| Rede | < 20% | 1,69 GB rx em 7,8 dias ≈ 2,5 KB/s (~0,04% de 50 Mbps) | 🔴 muito abaixo |
| Memória | só shapes A1 | — | n/a |

`crontab` do usuário: **vazio**. Nenhuma mitigação instalada.

**Pela regra escrita da Oracle, esta instância qualifica para recuperação.** Decisão
sobre instalar keep-alive ou aceitar o risco: ver `docs/ROADMAP.md`, Fase 0.

## Estado da máquina (20/08/2026)

- **Swap em uso: 541 MB** de 2 GB, memória em 57% — a VM já pagina para disco
  apenas com o n8n rodando. Confirma na prática a regra de **nunca renderizar vídeo
  aqui** (`CLAUDE.md`, regra de ouro 5).
- Disco: 19,1% de 44,96 GB — folgado.
- `*** System restart required ***`: há atualização de kernel pendente. **Reboot é
  seguro e mantém o IP** (somente *parar* a instância troca o endereço).
- Ubuntu 22.04.5 LTS, kernel 6.8.0-1054-oracle.

## Exportar o workflow do container — comando correto

O container roda como usuário `node`, que **não tem permissão de escrita em `/tmp`**
(`EACCES`). Exportar para o home do próprio usuário:

```bash
sudo docker exec n8n n8n export:workflow --id=vixeeepub01 --output=/home/node/wf_live.json
sudo docker cp n8n:/home/node/wf_live.json ~/wf_live.json
wc -c ~/wf_live.json && grep -c '"type":' ~/wf_live.json
```

> ⚠️ O arquivo exportado sai **com os tokens em texto puro**. Ao trazer para o PC,
> salvar **fora** da pasta do repositório (o `.gitignore` cobre `wf_live.json`, mas
> não conte apenas com isso).
