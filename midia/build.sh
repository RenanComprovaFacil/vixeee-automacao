#!/usr/bin/env bash
# STUB / Fase 3 — fabrica de midia (roda no GitHub Actions, NAO na VM).
# Baixa o mp4 da CDN da Shopee, corta pra 9:16, escreve preco/%OFF e exporta.
#
# ATENCAO: ffmpeg NAO vem pre-instalado no runner do GitHub Actions.
# O workflow .github/workflows/build-midia.yml precisa de um step
#   sudo apt-get update && sudo apt-get install -y ffmpeg
#
# Limites a validar ANTES de publicar (ver docs/PLANO-EVOLUCAO.md secao 1.7):
#   IG Reels  : 3 s – 15 min, <= 300 MB, max 1920 px horizontal
#   IG Stories: 3 s – 60 s,   <= 100 MB
#   Telegram sendVideo por URL: <= 20 MB (upload: <= 50 MB)
set -euo pipefail

IN="${1:?uso: build.sh <video_in.mp4> <preco> <off> <out.mp4>}"
PRECO="${2:?}"; OFF="${3:?}"; OUT="${4:?}"

# Esqueleto de referencia (ajustar fonte/posicao/estilo na Fase 3):
ffmpeg -y -i "$IN" \
  -vf "crop='min(iw,ih*9/16)':'min(ih,iw*16/9)',scale=1080:1920,\
drawtext=text='R\$ ${PRECO}':fontcolor=white:fontsize=64:x=(w-tw)/2:y=h-220,\
drawtext=text='${OFF}% OFF':fontcolor=white:fontsize=48:x=(w-tw)/2:y=h-140" \
  -c:v libx264 -pix_fmt yuv420p -c:a aac -movflags +faststart \
  "$OUT"
