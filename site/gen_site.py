#!/usr/bin/env python3
"""
gen_site.py — gera a pagina de bio (link-in-bio) a partir do dados/semana.json.

Por que existe: o funil hoje e Instagram -> bio -> Telegram -> Shopee (3 passos).
Com esta pagina vira Instagram -> pagina -> Shopee (2 passos), e o Telegram deixa
de ser obrigatorio no meio do caminho (continua no rodape, como canal proprio).

A pagina e ESTATICA: o HTML ja sai com os 7 produtos escritos dentro. Nao depende
de fetch, carrega instantaneo no navegador embutido do Instagram e funciona mesmo
com JavaScript desligado. O unico JS e um detalhe cosmetico (destacar o produto de
hoje), que degrada sem quebrar nada.

USO
    python site/gen_site.py            # gera ./index.html
    python site/gen_site.py --saida /tmp/preview.html

Publicacao: GitHub Pages servindo a raiz do repositorio.
"""
import argparse
import html
import json
from datetime import datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

# Paleta A — "Garimpo Quente" (docs/CONTEXTO.md)
CORAL, ROSA, AMARELO, CREME, GRAFITE = "#FF5A5F", "#FF3E9A", "#FFC93C", "#FFF6EC", "#2B2B2B"

# Enderecos vem do config.json — NUNCA escreva URL aqui dentro.
# Trocar de hospedagem deve ser uma edicao em UM arquivo, nao uma cacada.
_CFG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
ARTES = _CFG["base_artes"]
TELEGRAM = _CFG["telegram"]
INSTAGRAM = _CFG["instagram"]

DIAS = {1: "segunda", 2: "terça", 3: "quarta", 4: "quinta",
        5: "sexta", 6: "sábado", 7: "domingo"}


def brl(v):
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def card(p):
    dia = p["dia"]
    nome = html.escape(p["nome"])
    link = html.escape(p["affiliate_link"])
    img = html.escape(p.get("image_url") or "")
    fallback = f"{ARTES}/dia{dia}_post.jpg"

    desconto = ""
    if p.get("desconto_pct"):
        desconto = f'<span class="off">-{p["desconto_pct"]}%</span>'

    de = ""
    if p.get("preco_original") and p.get("preco") and p["preco_original"] > p["preco"]:
        de = f'<span class="de">{brl(p["preco_original"])}</span>'

    prova = []
    if p.get("vendas"):
        prova.append(f'{html.escape(str(p["vendas"]))} vendidos')
    if p.get("avaliacao"):
        prova.append(f'★ {p["avaliacao"]}')
    prova_html = f'<p class="prova">{" · ".join(prova)}</p>' if prova else ""

    return f'''      <article class="card" data-dia="{dia}">
        <div class="thumb">
          {desconto}
          <img src="{img}" alt="{nome}" loading="lazy"
               onerror="this.onerror=null;this.src='{fallback}'">
        </div>
        <div class="info">
          <span class="quando">{DIAS[dia]}</span>
          <h2>{nome}</h2>
          {prova_html}
          <p class="preco">{de}<strong>{brl(p["preco"]) if p.get("preco") else ""}</strong></p>
          <a class="cta" href="{link}" target="_blank" rel="noopener sponsored">Ver na Shopee</a>
        </div>
      </article>'''


def gerar(dados):
    produtos = sorted(dados["produtos"], key=lambda x: x["dia"])
    cards = "\n".join(card(p) for p in produtos)

    try:
        coleta = datetime.fromisoformat(dados["gerado_em"]).strftime("%d/%m/%Y")
    except Exception:
        coleta = dados.get("gerado_em", "")

    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Vixeee Que Barato — achadinhos da semana</title>
<meta name="description" content="Os achadinhos da semana do @vixeeequebarato: {len(produtos)} ofertas garimpadas na Shopee, com link direto.">
<meta name="theme-color" content="{CORAL}">
<meta property="og:type" content="website">
<meta property="og:title" content="Vixeee Que Barato — achadinhos da semana">
<meta property="og:description" content="{len(produtos)} achadinhos garimpados na Shopee, com link direto.">
<meta property="og:image" content="{ARTES}/dia1_post.jpg">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🙀</text></svg>">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
  *,*::before,*::after {{ box-sizing: border-box; }}
  :root {{
    --coral: {CORAL}; --rosa: {ROSA}; --amarelo: {AMARELO};
    --creme: {CREME}; --grafite: {GRAFITE};
  }}
  body {{
    margin: 0; padding: 0 16px 48px;
    font-family: Poppins, system-ui, -apple-system, "Segoe UI", sans-serif;
    background: var(--creme); color: var(--grafite);
    -webkit-font-smoothing: antialiased;
  }}
  .wrap {{ max-width: 620px; margin: 0 auto; }}

  header {{ text-align: center; padding: 34px 0 26px; }}
  .gato {{
    width: 76px; height: 76px; margin: 0 auto 12px; border-radius: 22px;
    background: linear-gradient(135deg, var(--coral), var(--rosa));
    display: grid; place-items: center; font-size: 40px; line-height: 1;
    box-shadow: 0 8px 22px rgba(255,90,95,.32);
  }}
  h1 {{ margin: 0; font-size: 26px; font-weight: 800; letter-spacing: -.4px; }}
  .arroba {{
    margin: 4px 0 0; font-size: 14px; font-weight: 600; color: var(--rosa);
    text-decoration: none; display: inline-block;
  }}
  .tagline {{ margin: 14px auto 0; max-width: 34ch; font-size: 15px; line-height: 1.5; opacity: .78; }}

  /* Grade de 2 colunas ja no celular: da pra bater o olho em 4 produtos por tela,
     que e como o proprio Shopee mostra. O produto do dia ocupa a linha inteira. */
  .cards {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
  .card.hoje {{ grid-column: 1 / -1; }}
  @media (min-width: 560px) {{
    .cards {{ grid-template-columns: 1fr 1fr 1fr; gap: 16px; }}
    .card.hoje {{ grid-column: 1 / -1; }}
  }}

  .card {{
    background: #fff; border-radius: 16px; overflow: hidden;
    box-shadow: 0 2px 14px rgba(43,43,43,.09);
    display: flex; flex-direction: column;
    transition: transform .15s ease, box-shadow .15s ease;
  }}
  .card:hover {{ transform: translateY(-2px); box-shadow: 0 8px 24px rgba(43,43,43,.14); }}
  .card.hoje {{ outline: 3px solid var(--amarelo); outline-offset: -3px; }}
  .card.hoje .quando::after {{ content: " · hoje"; color: var(--coral); font-weight: 700; }}

  .thumb {{ position: relative; aspect-ratio: 1; background: #f4f4f6; }}
  .thumb img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
  .off {{
    position: absolute; top: 8px; right: 8px; z-index: 2;
    background: var(--coral); color: #fff; font-size: 11.5px; font-weight: 800;
    padding: 5px 9px; border-radius: 999px; box-shadow: 0 3px 10px rgba(0,0,0,.16);
  }}

  .info {{ padding: 11px 12px 12px; display: flex; flex-direction: column; flex: 1; }}
  .quando {{ font-size: 10px; font-weight: 700; text-transform: uppercase;
             letter-spacing: .5px; opacity: .5; }}
  h2 {{
    margin: 4px 0 0; font-size: 13px; font-weight: 600; line-height: 1.3;
    /* 2 linhas no maximo: mantem todos os cards da fileira do mesmo tamanho */
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
    overflow: hidden;
  }}
  .prova {{ margin: 6px 0 0; font-size: 11px; opacity: .62; }}
  .preco {{ margin: 9px 0 11px; display: flex; align-items: baseline; gap: 7px; flex-wrap: wrap; }}
  .de {{ font-size: 12px; opacity: .45; text-decoration: line-through; }}
  .preco strong {{ font-size: 19px; font-weight: 800; color: var(--rosa); }}

  .cta {{
    margin-top: auto; display: block; text-align: center; text-decoration: none;
    background: var(--amarelo); color: var(--grafite);
    font-weight: 700; font-size: 14px; padding: 12px 8px; border-radius: 12px;
  }}

  /* O produto do dia ganha destaque: imagem lado a lado e tipografia maior */
  .card.hoje {{ flex-direction: row; }}
  .card.hoje .thumb {{ width: 42%; flex-shrink: 0; }}
  .card.hoje .info {{ padding: 14px 16px; justify-content: center; }}
  .card.hoje h2 {{ font-size: 15px; -webkit-line-clamp: 3; }}
  .card.hoje .preco strong {{ font-size: 24px; }}
  .cta:active {{ transform: scale(.98); }}

  footer {{ margin-top: 34px; text-align: center; font-size: 13px; }}
  .tg {{
    display: inline-block; text-decoration: none; font-weight: 700;
    background: var(--grafite); color: var(--creme);
    padding: 13px 26px; border-radius: 999px;
  }}
  .aviso {{ margin: 22px auto 0; max-width: 40ch; font-size: 11.5px; line-height: 1.6; opacity: .55; }}
</style>
</head>
<body>
<div class="wrap">

  <header>
    <div class="gato">🙀</div>
    <h1>Vixeee Que Barato</h1>
    <a class="arroba" href="{INSTAGRAM}" target="_blank" rel="noopener">@vixeeequebarato</a>
    <p class="tagline">Os achadinhos da semana, tudo num lugar só.<br>É só clicar e correr pro abraço.</p>
  </header>

  <main>
    <div class="cards">
{cards}
    </div>
  </main>

  <footer>
    <a class="tg" href="{TELEGRAM}" target="_blank" rel="noopener">📢 Entrar no Telegram</a>
    <p class="aviso">
      Preços coletados em {coleta} — a Shopee pode alterar a qualquer momento.<br>
      Os links são de afiliado: você paga exatamente o mesmo preço e ajuda o canal.
    </p>
  </footer>

</div>
<script>
  // Cosmetico: destaca o produto do dia e joga ele pro topo.
  // Se o JS nao rodar, a pagina segue correta, so sem o destaque.
  (function () {{
    var d = new Date().getDay();          // 0=domingo .. 6=sabado
    var dia = d === 0 ? 7 : d;            // nossa convencao: 1=segunda .. 7=domingo
    var alvo = document.querySelector('.card[data-dia="' + dia + '"]');
    if (!alvo) return;
    alvo.classList.add('hoje');
    alvo.parentNode.prepend(alvo);
  }})();
</script>
</body>
</html>
'''


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--saida", default="index.html")
    args = ap.parse_args()

    dados = json.loads((RAIZ / "dados" / "semana.json").read_text(encoding="utf-8"))
    destino = Path(args.saida)
    if not destino.is_absolute():
        destino = RAIZ / destino

    destino.write_text(gerar(dados), encoding="utf-8")

    n = len(dados["produtos"])
    kb = destino.stat().st_size / 1024
    print(f"[ok] {destino.name} gerado — {n} produtos, {kb:.1f} KB, HTML estatico")
    print(f"     imagens: foto da Shopee, com a arte diaN_post.jpg como fallback")


if __name__ == "__main__":
    main()
