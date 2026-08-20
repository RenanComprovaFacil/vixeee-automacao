#!/usr/bin/env python3
"""
testar_equivalencia_v3.py — prova que o workflow v3 (orientado a dados) publica
exatamente o mesmo conteudo que o v2 (nos estaticos) em cada dia da semana.

Simula, para os 7 dias, a expressao `produtos[$now.weekday - 1]` do v3 e compara
com o que o no `Dia N Dados` do v2 entrega.

Nao toca no servidor. Nao imprime credencial: so le os nos `Dia N Dados`, que
nao contem token.

USO
  python workflow/testar_equivalencia_v3.py <caminho-do-export-v2>

  O export do v2 sai da VM com:
    sudo docker exec n8n n8n export:workflow --id=vixeeepub01 --output=/home/node/wf_live.json
  Guarde-o FORA do repositorio (ele tem os tokens em texto puro).
"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DIAS = {1: "segunda", 2: "terca", 3: "quarta", 4: "quinta",
        5: "sexta", 6: "sabado", 7: "domingo"}

URL_ARTES = "https://raw.githubusercontent.com/RenanComprovaFacil/vixeee-artes/main"

# campos publicados que precisam bater
COMPARAR = ["image_url", "legenda_tg", "legenda_ig",
            "image_url_ig_post", "image_url_ig_story"]


def carregar_v2(caminho: Path) -> dict:
    """Extrai o conteudo dos nos `Dia N Dados` do export do v2."""
    d = json.loads(caminho.read_text(encoding="utf-8"))
    d = d[0] if isinstance(d, list) else d
    saida = {}
    for no in d["nodes"]:
        if no["name"].startswith("Dia ") and no["name"].endswith(" Dados"):
            dia = int(no["name"].split()[1])
            saida[dia] = {a["name"]: a["value"]
                          for a in no["parameters"]["assignments"]["assignments"]}
    return saida


def simular_v3(semana: dict, weekday: int) -> dict:
    """Reproduz em Python o que as expressoes do v3 resolvem para aquele dia."""
    p = semana["produtos"][weekday - 1]          # produtos[$now.weekday - 1]
    return {
        "image_url": p["image_url"],
        "legenda_tg": p["legenda_tg"],
        "legenda_ig": p["legenda_ig"],
        "image_url_ig_post": f"{URL_ARTES}/dia{weekday}_post.jpg",
        "image_url_ig_story": f"{URL_ARTES}/dia{weekday}_story.jpg",
    }


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)

    v2 = carregar_v2(Path(sys.argv[1]))
    semana = json.loads((RAIZ / "dados" / "semana.json").read_text(encoding="utf-8"))

    print("=" * 72)
    print("  EQUIVALENCIA v2 (nos estaticos) x v3 (orientado a dados)")
    print("=" * 72)

    total_div = 0
    for wd in range(1, 8):
        esperado = v2.get(wd, {})
        obtido = simular_v3(semana, wd)
        divs = [c for c in COMPARAR if esperado.get(c) != obtido.get(c)]

        nome = semana["produtos"][wd - 1]["nome"][:34]
        if divs:
            total_div += len(divs)
            print(f"\n  [X] dia {wd} ({DIAS[wd]:8}) {nome}")
            for c in divs:
                print(f"      ~ {c}")
                print(f"          v2: {str(esperado.get(c))[:88]}")
                print(f"          v3: {str(obtido.get(c))[:88]}")
        else:
            print(f"  [OK] dia {wd} ({DIAS[wd]:8}) {nome}")

    print("\n" + "=" * 72)
    if total_div == 0:
        print("  RESULTADO: EQUIVALENTES nos 7 dias e nos 5 campos publicados.")
        print("  O v3 publica exatamente o mesmo conteudo que o fluxo em producao.")
    else:
        print(f"  RESULTADO: {total_div} divergencia(s) — revisar antes de promover o v3.")
    print("=" * 72)
    return 1 if total_div else 0


if __name__ == "__main__":
    sys.exit(main())
