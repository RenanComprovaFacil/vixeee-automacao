#!/usr/bin/env python3
"""
make_creatives.py — Gera as 14 artes da semana na Paleta A "Garimpo Quente".
Para cada produto (dia 1..N) gera:
  out/diaN_post.jpg   (1080x1080, feed)
  out/diaN_story.jpg  (1080x1920, story)

ENTRADA: semana.json com uma lista "produtos", cada um com:
  { "dia": 1, "nome": "...", "preco": "R$39,90", "de_preco": "R$75,28" (opcional),
    "desconto": "47%" (opcional), "image_url_shopee": "https://down-bs-br..." }

FOTO DO PRODUTO: a CDN da Shopee (down-bs-br.img.susercontent.com) bloqueia
download fora da sessão logada. Ordem de tentativa por dia:
  1) usa photos/diaN.jpg se existir (recomendado: capturado pelo navegador — ver
     references/coleta-shopee.md; Claude navega na URL da imagem, tira screenshot
     e recorta o quadrado central, salvando em photos/diaN.jpg).
  2) tenta baixar a image_url_shopee com header Referer (às vezes funciona).
  3) se nada der certo, usa um fundo neutro (a arte sai sem a foto — evitar).

USO:  python3 make_creatives.py semana.json [--photos ./photos] [--out ./out]
Requer: playwright (chromium já vem instalado no ambiente). Instale se faltar:
  pip install playwright --break-system-packages
"""
import sys, os, json, base64, argparse, urllib.request

PALETA = dict(coral="#FF5A5F", rosa="#FF3E9A", amarelo="#FFC93C", creme="#FFF6EC", grafite="#2B2B2B")

CSS = """
:root{--coral:#FF5A5F;--rosa:#FF3E9A;--amarelo:#FFC93C;--creme:#FFF6EC;--grafite:#2B2B2B}
*{margin:0;padding:0;box-sizing:border-box;font-family:'Poppins','Trebuchet MS','DejaVu Sans',sans-serif}
.badge-off{position:absolute;top:-18px;right:-18px;background:var(--coral);color:#fff;border-radius:50%;
 display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:800;
 box-shadow:0 8px 24px rgba(0,0,0,.18);transform:rotate(8deg)}
.badge-off .lbl{letter-spacing:2px}
.photo{background:#fff;border-radius:36px;box-shadow:0 18px 50px rgba(43,43,43,.16);overflow:hidden;position:relative}
.photo img{width:100%;height:100%;object-fit:cover}
.name{color:var(--grafite);font-weight:700;line-height:1.15;display:-webkit-box;-webkit-box-orient:vertical;overflow:hidden}
.pill{background:var(--amarelo);color:var(--grafite);font-weight:800;border-radius:999px;display:inline-flex;align-items:center;gap:12px}
.de{color:#9a9a9a;text-decoration:line-through;font-weight:600}.por{color:var(--rosa);font-weight:800}
.dot{position:absolute;border-radius:50%}
"""

def badge(pct):
    if not pct:
        return ""
    return ('<div class="badge-off" style="width:150px;height:150px">'
            f'<span class="pct" style="font-size:52px;line-height:1">{pct}</span>'
            '<span class="lbl" style="font-size:22px">OFF</span></div>')

def de_span(de, size):
    return f'<span class="de" style="font-size:{size}px">de {de}</span>' if de else ""

def post_html(photo, pct, nome, de, por):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
 body{{width:1080px;height:1080px;background:var(--creme);position:relative;padding:64px 70px;display:flex;flex-direction:column}}
 .name{{-webkit-line-clamp:2}}</style></head><body>
 <div class="dot" style="width:220px;height:220px;background:var(--amarelo);opacity:.25;top:-60px;left:-60px"></div>
 <div class="dot" style="width:160px;height:160px;background:var(--rosa);opacity:.18;bottom:120px;right:-40px"></div>
 <div style="display:flex;align-items:center;gap:16px;z-index:2">
   <div style="width:56px;height:56px;border-radius:16px;background:var(--coral);display:flex;align-items:center;justify-content:center;font-size:30px">🙀</div>
   <div><div style="font-weight:800;color:var(--grafite);font-size:34px">Vixeee Que Barato</div>
   <div style="color:var(--rosa);font-weight:700;font-size:22px">@vixeeequebarato</div></div></div>
 <div style="flex:1;display:flex;align-items:center;justify-content:center;position:relative;z-index:2">
   <div style="position:relative"><div class="photo" style="width:560px;height:560px"><img src="{photo}"></div>{badge(pct)}</div></div>
 <div style="z-index:2"><div class="name" style="font-size:40px;margin-bottom:18px">{nome}</div>
   <div style="display:flex;align-items:flex-end;justify-content:space-between">
   <div style="display:flex;flex-direction:column;gap:4px">{de_span(de,36)}<span class="por" style="font-size:72px">{por}</span></div>
   <div class="pill" style="font-size:32px;padding:20px 34px">🔗 Link na bio</div></div></div>
 </body></html>"""

def story_html(photo, pct, nome, de, por):
    b = badge(pct).replace('width:150px;height:150px','width:190px;height:190px').replace('font-size:52px','font-size:64px')
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}
 body{{width:1080px;height:1920px;background:linear-gradient(160deg,var(--coral),var(--rosa));position:relative;padding:110px 80px;display:flex;flex-direction:column;align-items:center}}
 .name{{-webkit-line-clamp:3}}</style></head><body>
 <div class="dot" style="width:300px;height:300px;background:#fff;opacity:.10;top:-80px;right:-80px"></div>
 <div class="dot" style="width:220px;height:220px;background:var(--amarelo);opacity:.25;bottom:220px;left:-70px"></div>
 <div style="display:flex;flex-direction:column;align-items:center;gap:8px;color:#fff;z-index:2">
   <div style="font-size:44px;font-weight:800">Vixeee Que Barato 🙀</div>
   <div style="font-size:28px;font-weight:700;opacity:.95">@vixeeequebarato</div></div>
 <div style="margin-top:70px;position:relative;z-index:2"><div class="photo" style="width:720px;height:720px"><img src="{photo}"></div>{b}</div>
 <div style="margin-top:60px;text-align:center;color:#fff;z-index:2;width:100%">
   <div class="name" style="font-size:52px;color:#fff;margin-bottom:26px">{nome}</div>
   <div style="background:#fff;border-radius:28px;padding:30px 40px;display:inline-flex;flex-direction:column;gap:6px;box-shadow:0 12px 30px rgba(0,0,0,.2)">
   <div style="display:flex;flex-direction:column;gap:4px">{de_span(de,42)}<span class="por" style="font-size:84px">{por}</span></div></div></div>
 <div style="margin-top:auto;z-index:2;text-align:center">
   <div class="pill" style="font-size:46px;padding:30px 60px;box-shadow:0 12px 30px rgba(0,0,0,.2)">👆 Link na bio</div></div>
 </body></html>"""

def load_photo(dia, url, photos_dir):
    # 1) foto local capturada pelo navegador
    for ext in ("jpg","jpeg","png","webp"):
        p = os.path.join(photos_dir, f"dia{dia}.{ext}")
        if os.path.exists(p):
            mime = "png" if ext=="png" else ("webp" if ext=="webp" else "jpeg")
            return "data:image/%s;base64,%s" % (mime, base64.b64encode(open(p,"rb").read()).decode())
    # 2) tenta baixar com referer da Shopee
    if url:
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent":"Mozilla/5.0","Referer":"https://shopee.com.br/"})
            data = urllib.request.urlopen(req, timeout=15).read()
            if len(data) > 2000:
                mime = "webp" if url.endswith(".webp") else "jpeg"
                return "data:image/%s;base64,%s" % (mime, base64.b64encode(data).decode())
        except Exception as e:
            print(f"  [dia {dia}] download falhou ({e}); usando fundo neutro. Capture a foto pelo navegador!")
    # 3) fallback neutro
    return "data:image/svg+xml;base64," + base64.b64encode(
        b'<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"><rect width="10" height="10" fill="#eee"/></svg>').decode()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("semana")
    ap.add_argument("--photos", default="./photos")
    ap.add_argument("--out", default="./out")
    a = ap.parse_args()
    data = json.load(open(a.semana, encoding="utf-8"))
    os.makedirs(a.out, exist_ok=True)
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("Falta o playwright: pip install playwright --break-system-packages")

    prods = data["produtos"]
    with sync_playwright() as p:
        browser = p.chromium.launch(args=["--no-sandbox"])
        for prod in prods:
            dia = prod["dia"]
            photo = load_photo(dia, prod.get("image_url_shopee",""), a.photos)
            common = dict(photo=photo, pct=prod.get("desconto",""), nome=prod["nome"],
                          de=prod.get("de_preco",""), por=prod["preco"])
            for kind, html, w, h in [
                ("post", post_html(**common), 1080, 1080),
                ("story", story_html(**common), 1080, 1920)]:
                page = browser.new_page(viewport={"width":w,"height":h}, device_scale_factor=1)
                page.set_content(html, wait_until="networkidle")
                out = os.path.join(a.out, f"dia{dia}_{kind}.jpg")
                page.screenshot(path=out, type="jpeg", quality=90)
                page.close()
                print(f"  gerado {out}")
        browser.close()
    print(f"OK: artes em {a.out}")

if __name__ == "__main__":
    main()
