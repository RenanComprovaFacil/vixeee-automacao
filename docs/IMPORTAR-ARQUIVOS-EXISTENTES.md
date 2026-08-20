# Importar arquivos que ainda estão no PC do Renan

Alguns ativos do projeto ainda **não estão neste repositório** porque vivem como
arquivos soltos / zips no computador do Renan (foram entregues no chat ao longo
da construção). Este documento mapeia **o que é cada um e onde ele entra** — é
parte da Fase 0.

> O Claude do Cowork exportou todo o contexto e o scaffold. O que falta são os
> **binários e os fontes** que só o Renan tem em mãos. Peça-os a ele (ou aponte
> o Claude Code para a pasta onde estão) e mova para os lugares abaixo.

## Backup técnico — `backup_tecnico_vixeee.zip`

| Arquivo dentro do zip | Onde colocar no repo | Observação |
|---|---|---|
| `n8n_vixeee_v2.json` (workflow atual) | `workflow/vixeee-publicador.json` | **Remover os segredos** do nó `Config` antes de commitar (ver `workflow/README.md`) |
| `gen_workflow.py` (gerador) | `workflow/gen_workflow.py` | Substitui o stub. Meta da Fase 1: reescrever para LER `dados/semana.json` |
| `produtos_semana1.json` | `dados/historico/produtos_semana1.json` | Fonte dos campos hoje `null` no `dados/semana.json` (item_id, preço, %OFF, image_url) |
| `runme_v2.txt` | **não versionar** | Contém comandos com token em texto puro → está no `.gitignore` |

## Artes do Instagram

| Zip | Onde | Observação |
|---|---|---|
| `artes_instagram_vixeee.zip` (14 artes: `diaN_post.jpg` + `diaN_story.jpg`) | já hospedadas no repo público **`vixeee-artes`** | Não precisam entrar aqui. Este repo só referencia as URLs `raw.githubusercontent.com/.../vixeee-artes/main/diaN_*.jpg` |
| `criativos_vixeee.zip` (PNGs-fonte + HTML dos criativos) | `midia/templates/` (opcional) | Útil como base para a Fase 3 (fábrica de mídia) |

## Extrator Shopee (projeto de terceiro)

O extrator maduro vem do repositório **BestPriceToday**, em
`tools/shopee_extract_mp4/` (`console_script.js` + `generate_script.py`). Reusar
adaptando para `captura/` (Fase 2) — ver `captura/SKILL.md`. **Não** portar o
resto do BestPriceToday (é um monolito FastAPI+Postgres que não cabe na VM).

## Checklist de importação (Fase 0)

- [ ] Recuperar `backup_tecnico_vixeee.zip` e distribuir os arquivos acima
- [ ] Exportar o workflow vivo da VM e limpar os segredos → `workflow/vixeee-publicador.json`
- [ ] Colocar `produtos_semana1.json` em `dados/historico/` e preencher o `dados/semana.json`
- [ ] Confirmar que `git status` mostra `runme*.txt`, `.env` e `SEGREDOS.local.md` como *ignored*
