#!/usr/bin/env python3
"""
gen_workflow_v3.py — gera o workflow n8n da FASE 1 (orientado a dados).

Diferenca para o v2 (`gen_workflow.py`, o que esta em producao):
  v2 -> 7 nos `Set` estaticos, um por dia, com produto/preco/legenda escritos
        dentro do proprio workflow. Trocar a semana = editar 7 nos via SSH.
  v3 -> 1 no `HTTP Request` le `dados/semana.json` cru do GitHub e uma expressao
        simples escolhe o produto do dia. Trocar a semana = 1 commit.

RESTRICOES RESPEITADAS (ver docs/RESTRICOES-N8N.md):
  1. Nenhum no Code.
  2. Expressoes simples. Sem array-literal, sem ternario. Só `sendQuery`.
  3. Nomes de no preservados: `Config`, `IG feed container`, `IG story container`
     sao referenciados por nome dentro de outras expressoes.
  5. As artes continuam hospedadas no GitHub (o IG exige URL publica).
  6. Espera de 30s + retry 5x/20s mantidos (mitigacao do erro 9007).

COMO A SELECAO DO DIA FUNCIONA
  `$now.weekday` (Luxon) devolve 1=segunda ... 7=domingo, ja no fuso da instancia
  (GENERIC_TIMEZONE=America/Sao_Paulo, verificado em 20/08/2026). O `dia` do
  semana.json usa a mesma convencao (dia1=segunda), entao:

      produtos[$now.weekday - 1]  ==  produto de hoje

  !! INVARIANTE: `produtos` PRECISA estar ordenado por `dia`, de 1 a 7.
     O gerador valida isso antes de emitir o arquivo.

USO
  python gen_workflow_v3.py                    # credenciais via $env (padrao)
  python gen_workflow_v3.py --credenciais literal   # embute os valores (NAO COMMITAR)
  python gen_workflow_v3.py --id vixeeepub02 --saida workflow/vixeee-publicador-v3.json
"""
import argparse
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

GH_USER = "RenanComprovaFacil"
REPO_DADOS = "vixeee-automacao"
REPO_ARTES = "vixeee-artes"
BRANCH = "main"

URL_SEMANA = f"https://raw.githubusercontent.com/{GH_USER}/{REPO_DADOS}/{BRANCH}/dados/semana.json"
URL_ARTES = f"https://raw.githubusercontent.com/{GH_USER}/{REPO_ARTES}/{BRANCH}"

# `produtos[$now.weekday - 1]` — o produto de hoje
HOJE = "$json.produtos[$now.weekday - 1]"


# --------------------------------------------------------------------------- #
#  Validacao da invariante
# --------------------------------------------------------------------------- #
def validar_semana(caminho: Path) -> dict:
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    produtos = dados.get("produtos", [])

    if len(produtos) != 7:
        sys.exit(f"ERRO: semana.json tem {len(produtos)} produtos, esperado 7.")

    dias = [p.get("dia") for p in produtos]
    if dias != [1, 2, 3, 4, 5, 6, 7]:
        sys.exit(
            "ERRO: `produtos` precisa estar ordenado por dia, de 1 a 7.\n"
            f"       encontrado: {dias}\n"
            "       O workflow seleciona por indice — fora de ordem, publica o produto errado."
        )

    faltando = []
    for p in produtos:
        for campo in ("image_url", "legenda_ig", "legenda_tg", "affiliate_link"):
            if not p.get(campo):
                faltando.append(f"dia {p['dia']}: {campo}")
    if faltando:
        sys.exit("ERRO: campos obrigatorios vazios:\n       " + "\n       ".join(faltando))

    print(f"[ok] semana.json valido — 7 produtos, ordenados, campos de publicacao preenchidos")
    return dados


# --------------------------------------------------------------------------- #
#  Credenciais
# --------------------------------------------------------------------------- #
def montar_credenciais(modo: str) -> list:
    if modo == "env":
        vals = {
            "igUserId": "={{$env.IG_USER_ID}}",
            "igToken": "={{$env.IG_TOKEN}}",
            "tgToken": "={{$env.TELEGRAM_BOT_TOKEN}}",
            "chatId": "={{$env.TELEGRAM_CHAT_ID}}",
        }
    else:  # literal — le do ambiente e embute. ARQUIVO GERADO NAO PODE SER COMMITADO.
        try:
            vals = {
                "igUserId": os.environ["IG_USER_ID"],
                "igToken": os.environ["IG_TOKEN"],
                "tgToken": os.environ["TELEGRAM_BOT_TOKEN"],
                "chatId": os.environ.get("TELEGRAM_CHAT_ID", "@vixeeequebarato"),
            }
        except KeyError as e:
            sys.exit(f"ERRO: variavel de ambiente {e} nao definida (modo literal).")
        print("[!!] MODO LITERAL: o arquivo gerado contem credenciais. NAO COMMITAR.")

    return [
        {"id": f"c{i}", "name": k, "value": v, "type": "string"}
        for i, (k, v) in enumerate(vals.items(), start=1)
    ]


# --------------------------------------------------------------------------- #
#  Nos
# --------------------------------------------------------------------------- #
def no_set(id_, nome, pos, assignments, incluir_outros):
    return {
        "parameters": {
            "includeOtherFields": incluir_outros,
            "assignments": {"assignments": assignments},
            "options": {},
        },
        "id": id_, "name": nome, "type": "n8n-nodes-base.set",
        "typeVersion": 3.4, "position": pos,
    }


def no_http(id_, nome, pos, url, params, retry=False):
    n = {
        "parameters": {
            "method": "POST",
            "url": url,
            "sendQuery": True,
            "queryParameters": {
                "parameters": [{"name": k, "value": v} for k, v in params]
            },
            "options": {},
        },
        "id": id_, "name": nome, "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2, "position": pos,
    }
    if retry:
        n.update({"retryOnFail": True, "maxTries": 5, "waitBetweenTries": 20000})
    return n


def no_espera(id_, nome, pos, segundos=30):
    return {
        "parameters": {"resume": "timeInterval", "amount": segundos, "unit": "seconds"},
        "id": id_, "name": nome, "type": "n8n-nodes-base.wait",
        "typeVersion": 1.1, "position": pos, "webhookId": id_,
    }


def construir(wf_id: str, modo_cred: str) -> dict:
    nos = []

    # -- entradas -----------------------------------------------------------
    nos.append({
        "parameters": {"rule": {"interval": [
            {"field": "cronExpression", "expression": "0 19 * * *"}]}},
        "id": "agenda", "name": "Agenda 19h",
        "type": "n8n-nodes-base.scheduleTrigger",
        "typeVersion": 1.1, "position": [200, 300],
    })
    nos.append({
        "parameters": {"httpMethod": "POST", "path": "vixeee-publicar-v3",
                       "responseMode": "onReceived", "options": {}},
        "id": "webhook-teste", "name": "Webhook Teste",
        "type": "n8n-nodes-base.webhook",
        "typeVersion": 2, "position": [200, 500], "webhookId": "vixeee-publicar-v3",
    })

    # -- le os dados do GitHub ----------------------------------------------
    # `cb` quebra o cache do raw.githubusercontent (TTL de ~5 min), para que um
    # commit novo valha imediatamente no proximo disparo.
    nos.append({
        "parameters": {
            "url": f"={URL_SEMANA}?cb={{{{$now.toMillis()}}}}",
            # OBRIGATORIO: o raw.githubusercontent serve .json como
            # "text/plain; charset=utf-8". Sem forcar o formato, o n8n entrega
            # o corpo como STRING e `$json.produtos` vira undefined -> o fluxo
            # publica campos vazios, em silencio. Descoberto em 20/08/2026.
            "options": {"response": {"response": {"responseFormat": "json"}}},
        },
        "id": "buscar-semana", "name": "Buscar semana",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2, "position": [430, 400],
    })

    # -- escolhe o produto de hoje ------------------------------------------
    nos.append(no_set("produto-hoje", "Produto de hoje", [660, 400], [
        {"id": "p1", "name": "dia", "value": f"={{{{{HOJE}.dia}}}}", "type": "number"},
        {"id": "p2", "name": "nome", "value": f"={{{{{HOJE}.nome}}}}", "type": "string"},
        {"id": "p3", "name": "image_url", "value": f"={{{{{HOJE}.image_url}}}}", "type": "string"},
        {"id": "p4", "name": "legenda_tg", "value": f"={{{{{HOJE}.legenda_tg}}}}", "type": "string"},
        {"id": "p5", "name": "legenda_ig", "value": f"={{{{{HOJE}.legenda_ig}}}}", "type": "string"},
        # as artes seguem a convencao de nome diaN_post.jpg / diaN_story.jpg
        {"id": "p6", "name": "image_url_ig_post",
         "value": f"={URL_ARTES}/dia{{{{$now.weekday}}}}_post.jpg", "type": "string"},
        {"id": "p7", "name": "image_url_ig_story",
         "value": f"={URL_ARTES}/dia{{{{$now.weekday}}}}_story.jpg", "type": "string"},
    ], incluir_outros=False))

    # -- injeta credenciais --------------------------------------------------
    nos.append(no_set("config", "Config", [890, 400],
                      montar_credenciais(modo_cred), incluir_outros=True))

    # -- ramo Telegram -------------------------------------------------------
    nos.append(no_http(
        "telegram-sendphoto", "Telegram sendPhoto", [1140, 180],
        "=https://api.telegram.org/bot{{$json.tgToken}}/sendPhoto",
        [("chat_id", "={{$json.chatId}}"),
         ("photo", "={{$json.image_url}}"),
         ("caption", "={{$json.legenda_tg}}")]))

    # -- ramo IG feed --------------------------------------------------------
    nos.append(no_http(
        "ig-feed-container", "IG feed container", [1140, 400],
        "=https://graph.facebook.com/v21.0/{{$json.igUserId}}/media",
        [("image_url", "={{$json.image_url_ig_post}}"),
         ("caption", "={{$json.legenda_ig}}"),
         ("access_token", "={{$json.igToken}}")]))
    nos.append(no_espera("espera-feed", "Espera feed", [1370, 400]))
    nos.append(no_http(
        "ig-feed-publicar", "IG feed publicar", [1600, 400],
        "=https://graph.facebook.com/v21.0/{{$('Config').item.json.igUserId}}/media_publish",
        [("creation_id", "={{$('IG feed container').item.json.id}}"),
         ("access_token", "={{$('Config').item.json.igToken}}")], retry=True))

    # -- ramo IG story -------------------------------------------------------
    nos.append(no_http(
        "ig-story-container", "IG story container", [1140, 620],
        "=https://graph.facebook.com/v21.0/{{$json.igUserId}}/media",
        [("image_url", "={{$json.image_url_ig_story}}"),
         ("media_type", "STORIES"),
         ("access_token", "={{$json.igToken}}")]))
    nos.append(no_espera("espera-story", "Espera story", [1370, 620]))
    nos.append(no_http(
        "ig-story-publicar", "IG story publicar", [1600, 620],
        "=https://graph.facebook.com/v21.0/{{$('Config').item.json.igUserId}}/media_publish",
        [("creation_id", "={{$('IG story container').item.json.id}}"),
         ("access_token", "={{$('Config').item.json.igToken}}")], retry=True))

    def liga(origem, destinos):
        return {origem: {"main": [[{"node": d, "type": "main", "index": 0} for d in destinos]]}}

    conexoes = {}
    for o, d in [
        ("Agenda 19h", ["Buscar semana"]),
        ("Webhook Teste", ["Buscar semana"]),
        ("Buscar semana", ["Produto de hoje"]),
        ("Produto de hoje", ["Config"]),
        ("Config", ["Telegram sendPhoto", "IG feed container", "IG story container"]),
        ("IG feed container", ["Espera feed"]),
        ("Espera feed", ["IG feed publicar"]),
        ("IG story container", ["Espera story"]),
        ("Espera story", ["IG story publicar"]),
    ]:
        conexoes.update(liga(o, d))

    return {
        "id": wf_id,
        "name": "Vixeee Que Barato — Publicador v3 (orientado a dados)",
        "nodes": nos,
        "connections": conexoes,
        "active": False,          # sempre nasce desativado — ativar e decisao humana
        "settings": {"executionOrder": "v1"},
        "tags": [],
    }


# --------------------------------------------------------------------------- #
def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--id", default="vixeeepub03",
                    help="id do workflow (padrao: vixeeepub03 — nao colide com o vixeeepub01 em producao)")
    ap.add_argument("--credenciais", choices=["env", "literal"], default="env",
                    help="env = referencia $env.* (padrao, seguro para commit); literal = embute os valores")
    ap.add_argument("--saida", default="workflow/vixeee-publicador-v3.json")
    args = ap.parse_args()

    validar_semana(RAIZ / "dados" / "semana.json")

    wf = construir(args.id, args.credenciais)
    destino = RAIZ / args.saida
    destino.write_text(json.dumps(wf, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[ok] {destino.relative_to(RAIZ)} — {len(wf['nodes'])} nos, id={wf['id']}, active={wf['active']}")
    print(f"     credenciais: modo {args.credenciais}")
    tipos = sorted({n["type"].replace("n8n-nodes-base.", "") for n in wf["nodes"]})
    print(f"     tipos de no usados: {', '.join(tipos)}")
    print(f"     (todos ja comprovados no workflow em producao — nenhum tipo novo)")


if __name__ == "__main__":
    main()
