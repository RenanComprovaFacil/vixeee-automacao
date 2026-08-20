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
