---
name: vixeee-semana
description: >-
  Programa uma nova semana de posts do projeto "Vixeee Que Barato" (renda extra
  com afiliados Shopee) de ponta a ponta: garimpa produtos no painel de afiliados
  pelo navegador, coleta link de afiliado + foto + preço, escreve as legendas na
  voz da marca, gera as artes na Paleta A (feed 1080x1080 + stories 1080x1920),
  hospeda no GitHub e monta/atualiza o workflow n8n que publica sozinho no
  Instagram (feed + stories) e no Telegram. Use SEMPRE que o Renan pedir para
  programar, montar ou rodar a semana de posts, garimpar achadinhos, "nova
  semana", "programa os posts", "roda a rotina Vixeee" ou similar — mesmo que não
  cite n8n, GitHub ou "skill". Roda no projeto "Vixeee Que Barato — Afiliados".
compatibility: >-
  Requer: navegador do Renan logado no painel de afiliados da Shopee
  (ferramentas mcp__claude-in-chrome__*); Python com playwright (chromium já vem
  no ambiente); acesso ao projeto para ler credenciais (SEGREDOS.local.md).
  O deploy final no n8n é colado pelo Renan no SSH da VM dele.
---

# Vixeee — Programar a semana de posts

Esta skill reproduz, de forma repetível, o fluxo que já colocamos no ar: garimpar
achadinhos na Shopee → montar artes na paleta → hospedar → publicar sozinho no
Instagram (feed + stories) e Telegram via n8n. O objetivo do Renan é **chamar a
skill e deixar a semana programada**, com o mínimo de intervenção. Trabalhe de
forma autônoma; só pare nos 2 pontos que dependem fisicamente dele (marcados 🙋).

## Antes de começar (contexto e preparo)
1. **Leia o contexto do projeto** com `project_read`: `claude/retomar-n8n.md`
   (arquitetura + manutenção) e `SEGREDOS.local.md` (credenciais, IP da VM,
   repo GitHub das artes). Nunca escreva segredos dentro da skill — leia sempre do
   projeto. Se o token do IG estiver perto de expirar, avise.
2. **Confirme o navegador**: o Renan precisa estar **logado no painel de afiliados
   da Shopee** (`affiliate.shopee.com.br`) numa aba. Se as ferramentas
   `mcp__claude-in-chrome__*` não responderem, peça pra ele abrir/logar e seguir.
3. Trabalhe numa pasta de trabalho (ex.: `vixeee-work/`) com `photos/` e `out/`.

`scripts/` e `references/` desta skill trazem o detalhe de cada etapa — leia o
arquivo indicado no passo antes de executá-lo.

## Passo 1 — Garimpar 7 produtos (autônomo)
Siga `references/coleta-shopee.md`. Resumo: no painel de ofertas, **escolha ~7
produtos por critério** (desconto alto + comissão boa + prova social + **variedade
de categoria** na semana + preço de impulso). De cada um capture pela "parte
interna" da página (DOM, não screenshot): nome, preço, preço "de", % desconto, e o
**link de afiliado curto** (`s.shopee.com.br/...` via "Obter link"). Capture a
**foto** navegando na `image_url` do produto → screenshot → recorte quadrado →
salve em `photos/diaN.jpg` (N = 1..7). Guarde a `image_url` original (o Telegram
usa ela crua).

Vá montando o `semana.json` (schema no topo de `scripts/gen_workflow.py`):
`gh_user`, `gh_repo`, `credenciais` (do SEGREDOS.local.md) e `produtos[]` com
`dia, nome, preco, de_preco, desconto, image_url_shopee, affiliate_link`.

## Passo 2 — Escrever as legendas (autônomo)
Siga `references/legendas.md`. Para cada produto escreva `legenda_ig` (voz "Vixeee
🙀", termina em "🔗 Link na bio!", com hashtags — o link não é clicável no IG) e
`legenda_tg` (curta, com o `affiliate_link` clicável no fim). Varie os ganchos por
categoria. Nunca cite comissão/margem em post público. Preencha os dois campos de
cada produto no `semana.json`.

## Passo 3 — Gerar as artes na Paleta A
`python3 scripts/make_creatives.py semana.json --photos ./photos --out ./out`
Gera `out/diaN_post.jpg` (1080x1080) e `out/diaN_story.jpg` (1080x1920). **Abra 1–2
com o Read pra conferir** que a foto entrou e a paleta ficou certa (fundo creme no
post, gradiente coral→rosa no story, preço em rosa, "Link na bio"). Se a foto saiu
vazia, volte capturar pelo navegador (a CDN bloqueia download direto).

## Passo 4 — Hospedar as artes no GitHub (mesmos nomes de sempre)
As URLs raw precisam bater com as do workflow, então **mantenha os nomes**
`diaN_post.jpg` / `diaN_story.jpg`.
- **Auto (preferido, hands-off):** se houver um GitHub PAT no projeto, rode
  `GITHUB_TOKEN=... python3 scripts/upload_github.py --owner <owner> --repo <repo> --dir ./out`.
- **Manual (fallback):** zipe `out/`, entregue com SendUserFile e peça 🙋 pro Renan
  arrastar no repo (Add file → Upload files → Commit), mantendo os nomes.
Depois **valide** que respondem 200 antes de mexer no n8n:
`curl -sI https://raw.githubusercontent.com/<owner>/<repo>/main/dia1_post.jpg`.

## Passo 5 — Montar e subir o workflow n8n
`python3 scripts/gen_workflow.py semana.json` → gera `workflow_v2.json` e
`runme_v2.txt`. Detalhes e regras técnicas em `references/n8n-deploy.md`.
🙋 Entregue o `runme_v2.txt` com SendUserFile e peça pro Renan **colar a linha no
SSH** da VM dele (Claude não acessa o servidor). Ele espera ~100s e dispara o teste:
`curl -X POST http://localhost:5678/webhook/vixeee-publicar -d '{"dia":1}'` →
conferir logs (ver n8n-deploy.md). Vazio de erro = feed + story + Telegram OK. O
workflow sobe **ativo**, então a rotação da semana passa a rodar sozinha às 19h.
Como é post público, confirme com ele antes do disparo de teste.

## Passo 6 — Documentar
Atualize no projeto (`project_write`): salve o `semana.json` da semana e uma linha
em `claude/retomar-n8n.md` registrando a data e os 7 produtos que entraram. Entregue
um backup (`workflow_v2.json`, `semana.json`) com SendUserFile.

## Princípios
- **Autônomo por padrão**: o Renan escolheu não ter preview de aprovação — garimpe,
  crie e entregue o comando de subida direto. Só pare nos 🙋 (navegador logado,
  upload manual se não houver PAT, e o paste no SSH), que dependem dele.
- **Qualidade real**: preços/%/vendas sempre verdadeiros (do que foi coletado);
  variedade de categoria; legendas com a voz da marca; artes conferidas.
- **Segurança**: credenciais só do projeto; confirmar antes de publicar/disparar;
  não usar a chave SSH do Renan; não parar a instância Oracle.
