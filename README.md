# Vixeee Que Barato — Automação

Fonte da verdade do projeto de renda extra por afiliados (Shopee/Mercado Livre)
da marca **@vixeeequebarato**. Um n8n publica sozinho, todo dia às 19h, no
Instagram (feed + stories) e no Telegram. **A automação já está no ar** — este
repositório existe para versionar o projeto, tirar os segredos do texto puro e
evoluir a arquitetura sem aumentar a dívida técnica.

> **Comece por `CLAUDE.md`.** Ele é o ponto de entrada e explica o acordo de
> time, o estado atual e a primeira ação recomendada.

## Mapa rápido

| Pasta / arquivo | O que é |
|---|---|
| `CLAUDE.md` | Ponto de entrada — leia primeiro |
| `docs/PLANO-EVOLUCAO.md` | O plano completo (espinha dorsal) |
| `docs/ROADMAP.md` | Fases 0–6 como checklists acionáveis |
| `docs/CONTEXTO.md` | Marca, tom, funil, conteúdo da Semana 1 |
| `docs/INFRA.md` | VM, n8n, deploy, acessos (sem segredos) |
| `docs/RESTRICOES-N8N.md` | Regras técnicas que não podem ser violadas |
| `docs/IMPORTAR-ARQUIVOS-EXISTENTES.md` | Arquivos que ainda estão no PC do Renan |
| `dados/semana.json` | Conteúdo da semana — trocar a semana = editar aqui |
| `dados/semana.schema.json` | Schema que valida o `semana.json` |
| `captura/` | Etapa de captura/curadoria (Fase 2) |
| `midia/` | Fábrica de mídia — ffmpeg no Actions (Fase 3) |
| `workflow/` | Workflow n8n versionado (Fase 0) |
| `.github/workflows/` | GitHub Actions (build de mídia + keep-alive) |
| `SEGREDOS.local.md` | Credenciais reais — **gitignored, nunca sobe** |

## Regras de ouro

1. Segredo real só em `SEGREDOS.local.md` (está no `.gitignore`). Nada de token
   em arquivo versionado.
2. **Rotacionar** os tokens que já foram expostos antes de tornar o repo
   público (ver `CLAUDE.md` e Fase 0 do roadmap).
3. Não parar a instância Oracle (o IP público é efêmero).
4. Não mexer no workflow sem ler `docs/RESTRICOES-N8N.md`.
