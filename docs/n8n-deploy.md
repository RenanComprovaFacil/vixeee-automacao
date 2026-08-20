# Deploy no n8n + regras técnicas desta VM

O workflow roda num container Docker `n8n` numa VM Oracle (1/8 OCPU / 1 GB RAM). Credenciais, IP e caminho da chave SSH ficam em `SEGREDOS.local.md` (gitignored) — nunca hardcode segredo em arquivo versionado.

## Subir/atualizar o workflow (o Renan cola no SSH dele)
O `gen_workflow.py` já produz `runme_v2.txt` — uma **linha única base64** que, no SSH da VM, importa + ativa + desliga o fluxo antigo + reinicia. Fluxo:
1. Renan abre o SSH: `ssh -i "<CAMINHO_DA_CHAVE_SSH>" ubuntu@<IP>` (caminho real em `SEGREDOS.local.md`).
2. Cola a linha do `runme_v2.txt` → aparece `INSTALANDO_espere_100s`.
3. **Espera ~100s** (boot lento; se disparar antes, dá 404).
4. Testa: `curl -X POST http://localhost:5678/webhook/vixeee-publicar -H 'content-type: application/json' -d '{"dia":1}'` e confere logs:
   `sleep 130; sudo docker logs --since 230s n8n 2>&1 | grep -iE "9007|Media ID|erro" | tail`.
   Vazio = feed + story + Telegram publicaram. ✅

Claude NÃO tem acesso ao SSH/servidor do Renan — sempre entregar o comando para ELE colar. Confirmar antes de qualquer disparo real (é post público).

## Regras técnicas que NÃO podem ser violadas (senão o fluxo quebra)
Descobertas na marra; o `gen_workflow.py` já respeita todas:
- **Nada de Code node** (o task runner Python não conecta nesta VM).
- Expressões: **sem array-literal, sem ternário aninhado**; `jsonBody`+`JSON.stringify` **não** funciona. Usar **`sendQuery` + queryParameters** e expressões simples `={{$json.campo}}`.
- Instagram é 2 passos (`/media` cria container → `/media_publish` publica). Precisa de **espera** entre eles (nó Wait 30s) + retry, senão dá erro **9007** ("mídia não está pronta"). Se voltar, subir a espera para 45–60s.
- IG exige **URL pública** da imagem (não aceita upload) → arte hospedada no GitHub. Telegram usa a foto crua da Shopee por URL.
- **Não parar a instância** Oracle (o IP muda; reboot mantém).

## Hospedar as artes (GitHub)
Repo público das artes (ver `SEGREDOS.local.md`, ex.: `RenanComprovaFacil/vixeee-artes`). Subir as 14 artes com os **mesmos nomes** `diaN_post.jpg` / `diaN_story.jpg` (as URLs raw não mudam):
- **Auto (hands-off):** `upload_github.py` com um GITHUB_TOKEN (PAT) guardado no projeto.
- **Manual:** entregar `out/` como zip; Renan arrasta no site do repo (Add file → Upload files → Commit), mantendo os nomes.
Sempre validar que as URLs raw respondem 200 antes de subir o workflow:
`curl -sI https://raw.githubusercontent.com/<owner>/<repo>/main/dia1_post.jpg`.
