# Coleta de produtos na Shopee (garimpo por critério + link + foto)

Objetivo: escolher ~7 produtos bons e capturar, de cada um: **nome, preço, preço "de", % de desconto, link de afiliado curto e a foto do produto**. Tudo pelo navegador do Renan, que precisa estar **logado no painel de afiliados** (`affiliate.shopee.com.br`). Use as ferramentas `mcp__claude-in-chrome__*` (navigate, read_page/get_page_text, find, javascript_tool, computer para screenshot).

## Critério de garimpo (o que faz um bom achadinho)
Priorize, nesta ordem de importância:
1. **Desconto alto** (≥ 40% chama atenção) e preço "de/por" visível.
2. **Comissão boa** (≥ 12–15% rende mais por venda).
3. **Prova social**: muitas vendas / avaliações altas (dá confiança).
4. **Variedade de categoria na semana**: não repetir nicho. Mire um mix tipo cozinha, casa, fitness, carro/gadget, ferramentas, moda/tênis, presente. Isso evita cansar o público e amplia o alcance.
5. **Preço "impulso"** (a maioria abaixo de R$70 converte melhor por impulso), com 1–2 âncoras um pouco mais caras ok.

Fonte boa de ofertas: no painel de afiliados, a área de **Ofertas / "Oferta de produto"** lista itens com preço, desconto e comissão já visíveis — ideal para comparar e escolher.

## Capturar o LINK de afiliado (curto)
Rota direta por produto (item_id aparece na URL do produto ou no painel):
`https://affiliate.shopee.com.br/offer/product_offer/<item_id>` → botão **"Obter link"** → um modal mostra o link curto `https://s.shopee.com.br/XXXX`. Leia o link do DOM/modal (não confie em screenshot). Há também **"Obter Link em Massa"** para gerar vários de uma vez.

Prefira ler valores pela "parte interna" da página (DOM via get_page_text / javascript_tool) em vez de screenshots — é mais confiável e não trava em páginas pesadas.

## Capturar a FOTO do produto (a pegadinha da CDN)
A imagem fica em `down-bs-br.img.susercontent.com/...webp`. **Essa CDN bloqueia hotlink/download fora da sessão logada** (baixar direto no servidor costuma falhar — `naturalWidth 0`). Método que funciona:
1. Numa aba, **navegue até a URL da imagem** (a própria `image_url` do produto). Como a aba está na sessão logada, a imagem carrega.
2. Tire um **screenshot** e **recorte o quadrado central** do produto (a arte usa `object-fit:cover`, então quadrado fica bem).
3. Salve em `photos/diaN.jpg` (N = posição do produto na semana, 1..7). O `make_creatives.py` embute essa foto na arte.

Guarde também a `image_url` original: o **Telegram** usa a foto crua da Shopee direto por URL (o servidor do Telegram consegue baixar, ao contrário do Meta em alguns casos — e no fluxo isso já é comprovadamente OK).

## Saída desta etapa
Monte o `semana.json` (ver README do gen_workflow) com, por produto: `dia`, `nome`, `preco`, `de_preco`, `desconto`, `image_url_shopee`, `affiliate_link`. E salve as fotos em `photos/diaN.jpg`. Os textos das legendas vêm depois (ver `legendas.md`).
