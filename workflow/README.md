# workflow/ — o fluxo n8n versionado

## Arquivos

| Arquivo | O que é |
|---|---|
| `vixeee-publicador.json` | **v2 — o que está em produção** (`vixeeepub01`, 23 nós). Cópia fiel do que roda na VM, comparada em 20/08/2026. Dados dos produtos embutidos em 7 nós `Set`. |
| `gen_workflow.py` | Gerador do v2. Mantido como referência histórica. |
| `vixeee-publicador-v3.json` | **v3 — Fase 1** (`vixeeepub03`, 12 nós). Lê `dados/semana.json` do GitHub. Ainda não promovido. |
| `gen_workflow_v3.py` | Gerador do v3. Valida o `semana.json` antes de emitir. |
| `testar_equivalencia_v3.py` | Prova que v3 e v2 publicam o mesmo conteúdo nos 7 dias. |

## Regra sobre credenciais

Os arquivos versionados **nunca** contêm token. O nó `Config` referencia
`$env.IG_USER_ID`, `$env.IG_TOKEN`, `$env.TELEGRAM_BOT_TOKEN` e
`$env.TELEGRAM_CHAT_ID`.

Para gerar uma versão com os valores embutidos (necessária enquanto o container
não tiver as variáveis de ambiente), use `--credenciais literal` e escreva o
arquivo **fora do repositório**. Ver `docs/FASE-1-IMPLANTACAO.md`.

## Antes de editar qualquer coisa

Leia `docs/RESTRICOES-N8N.md`. Resumo do que quebra este n8n: nó Code, expressões
com array-literal ou ternário aninhado, e `jsonBody` + `JSON.stringify`.

Os nomes `Config`, `IG feed container` e `IG story container` são referenciados
dentro de expressões de outros nós — renomear quebra o fluxo.
