# Captura (Fase 2) — placeholder

Esta pasta hospeda a etapa de CAPTURA/curadoria semanal (ver `docs/ROADMAP.md`,
Fase 2). Hoje a curadoria e' feita pela skill "vixeee-semana" no navegador
logado do Renan; a meta e' fundi-la com o extrator Shopee do projeto de
terceiro BestPriceToday.

## O que entra aqui
- `gen_script.py`   — gera o `console_script.js` a partir do CSV de afiliados.
- `console_script.js` — script que se cola no console da Shopee (aba logada)
  para capturar dados do produto E a URL do mp4 (a CDN de video da Shopee e'
  publica; so' o endpoint /api/v4/item/get exige sessao logada).
- Saida esperada: um `dados/semana.json` valido contra `dados/semana.schema.json`.

## De onde vem o codigo-base
Extrator maduro do BestPriceToday: `tools/shopee_extract_mp4/`
(`console_script.js` + `generate_script.py`). Reusar adaptando — NAO baixar o
mp4 no navegador; apenas gravar a `video_url` no JSON.

## Cuidados herdados (corrigir ao adaptar)
- Manter o sleep de 4,5–9 s por produto (anti-bot). NAO reduzir.
- Bug do extrator original: itens marcados como 'erro' nunca sao reprocessados
  (o retry por 'timeout' e' codigo morto). Corrigir.
- O progresso e' salvo em localStorage (`shopee_dl_progress`) → da' pra fechar a
  aba e retomar.
