import json, sys, base64

GH_USER = sys.argv[1] if len(sys.argv) > 1 else "SEU_USUARIO"
REPO = "vixeee-artes"
BRANCH = "main"
def gh(fname): return f"https://raw.githubusercontent.com/{GH_USER}/{REPO}/{BRANCH}/{fname}"

# Credenciais — lidas do ambiente. NUNCA hardcode aqui (repo e publico).
# Defina antes de rodar:  export IG_USER_ID=... IG_TOKEN=... TELEGRAM_BOT_TOKEN=...
import os
IG_USER_ID = os.environ["IG_USER_ID"]
IG_TOKEN   = os.environ["IG_TOKEN"]
TG_TOKEN   = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID    = os.environ.get("TELEGRAM_CHAT_ID", "@vixeeequebarato")

# Produtos: (shopee_img, shopee_link, legenda_ig, legenda_tg)  — dia 1..7
prod = json.load(open("produtos_semana1.json"))["produtos"]
def L(d): return prod[d-1]["affiliate_link"]
def IMG(d): return prod[d-1]["image_url"]

leg_ig = {
1:"Vixeee 🙀 creatina PURA por menos de R$40?!\n300g que rendem o mês inteiro de treino 💪\n✅ 100% pura · +100 MIL já garantiram\nCorre que 47% OFF não dura 😳\n🔗 Link na bio!\n\n#achadinhos #creatina #shopeefinds #vixeeequebarato #treino",
2:"Vixeee 🙀 R$15 pra deixar a cozinha de RICO?!\nPapel mármore dourado, impermeável e aguenta calor 🔥\nCola, alisa e pronto — reforma sem obra ✨\n🔗 Link na bio!\n\n#decoracao #achadinhos #cozinha #shopeefinds #vixeeequebarato",
3:"Vixeee 🙀 chega de chorar cortando cebola!\nMini processador que tritura alho, carne e legumes em segundos ⚡\nCabe na palma da mão e por menos de R$30 👏\n🔗 Link na bio!\n\n#cozinha #gadget #achadinhos #shopeefinds #vixeeequebarato",
4:"Vixeee 🙀 calibrar pneu no posto foi a última vez!\nCompressor portátil 4 em 1 que também é powerbank e lanterna 🚗🔋\n65% OFF nesse coringa de porta-luvas 😮\n🔗 Link na bio!\n\n#carro #gadget #achadinhos #shopeefinds #vixeeequebarato",
5:"Vixeee 🙀 19 peças de silicone com cabo de madeira por R$29?!\nNão arranha a panela e ainda é lindo na bancada 😍\nKit completo que todo mundo pede emprestado 🍳\n🔗 Link na bio!\n\n#cozinha #achadinhos #utensilios #shopeefinds #vixeeequebarato",
6:"Vixeee 🙀 tênis com PLACA DE CARBONO por R$71?!\nO tipo que atleta paga fortuna, aqui saiu com 53% OFF 🏃‍♂️💨\nDo 33 ao 44, unissex.\n🔗 Link na bio!\n\n#corrida #tenis #achadinhos #shopeefinds #vixeeequebarato",
7:"Vixeee 🙀 faca de churrasco PROFISSIONAL e ainda personalizada ⚽🔥\nO presente certo pro cunhado que se acha o rei da brasa 😅\n🔗 Link na bio!\n\n#churrasco #presente #achadinhos #shopeefinds #vixeeequebarato",
}
leg_tg = {
1:f"💪 CREATINA PURA 300g — R$39,90 (47% OFF!)\n+100 MIL vendas. Some rápido!\n👉 {L(1)}",
2:f"✨ PAPEL PAREDE MÁRMORE (cozinha) — R$15,99 (54% OFF!)\nImpermeável e resiste ao calor. 50 MIL+ já compraram.\n👉 {L(2)}",
3:f"⚡ MINI PROCESSADOR ELÉTRICO 350ml — R$28,99 (52% OFF!)\nAlho, carne e legumes triturados em segundos.\n👉 {L(3)}",
4:f"🚗 BOMBA DE AR PORTÁTIL 4x1 (compressor + powerbank) — R$69,99 (65% OFF!)\nCalibra pneu, carrega celular e ilumina.\n👉 {L(4)}",
5:f"🍳 KIT 19 UTENSÍLIOS DE SILICONE (cabo de madeira) — R$29,98 (55% OFF!)\nNão arranha panela. Kit completo.\n👉 {L(5)}",
6:f"🏃 TÊNIS PLACA DE CARBONO (corrida) — R$71,62 (53% OFF!)\nUnissex 33–44. Leve e com retorno de energia.\n👉 {L(6)}",
7:f"🔥 FACA DE CHURRASCO PROFISSIONAL (personalizável) — R$57,00 (16% OFF!)\nPresente perfeito pra quem ama uma brasa.\n👉 {L(7)}",
}

# cron por dia da semana: dia1=Seg(1) ... dia6=Sab(6), dia7=Dom(0)
cron_dow = {1:"1",2:"2",3:"3",4:"4",5:"5",6:"6",7:"0"}

nodes = []
conns = {}

def add_conn(src, targets):
    conns[src] = {"main":[[{"node":t,"type":"main","index":0} for t in targets]]}

# ---- credenciais compartilhadas (Config) ----
config_node = {
  "parameters":{"includeOtherFields":True,"assignments":{"assignments":[
    {"id":"c1","name":"igUserId","value":IG_USER_ID,"type":"string"},
    {"id":"c2","name":"igToken","value":IG_TOKEN,"type":"string"},
    {"id":"c3","name":"tgToken","value":TG_TOKEN,"type":"string"},
    {"id":"c4","name":"chatId","value":CHAT_ID,"type":"string"},
  ]},"options":{}},
  "id":"config","name":"Config","type":"n8n-nodes-base.set","typeVersion":3.4,"position":[700,600]
}
nodes.append(config_node)

# ---- por dia: trigger + Dados ----
for d in range(1,8):
    y = 120 + (d-1)*130
    trig = {
      "parameters":{"rule":{"interval":[{"field":"cronExpression","expression":f"0 19 * * {cron_dow[d]}"}]}},
      "id":f"trig{d}","name":f"Agenda Dia {d}","type":"n8n-nodes-base.scheduleTrigger","typeVersion":1.1,"position":[200,y]
    }
    dados = {
      "parameters":{"includeOtherFields":False,"assignments":{"assignments":[
        {"id":f"d{d}1","name":"image_url","value":IMG(d),"type":"string"},
        {"id":f"d{d}2","name":"image_url_ig_post","value":gh(f"dia{d}_post.jpg"),"type":"string"},
        {"id":f"d{d}3","name":"image_url_ig_story","value":gh(f"dia{d}_story.jpg"),"type":"string"},
        {"id":f"d{d}4","name":"legenda_tg","value":leg_tg[d],"type":"string"},
        {"id":f"d{d}5","name":"legenda_ig","value":leg_ig[d],"type":"string"},
      ]},"options":{}},
      "id":f"dados{d}","name":f"Dia {d} Dados","type":"n8n-nodes-base.set","typeVersion":3.4,"position":[450,y]
    }
    nodes.append(trig); nodes.append(dados)
    add_conn(f"Agenda Dia {d}", [f"Dia {d} Dados"])
    add_conn(f"Dia {d} Dados", ["Config"])

# ---- Webhook (teste manual) -> Dia 1 Dados ----
wh = {
  "parameters":{"httpMethod":"POST","path":"vixeee-publicar","responseMode":"onReceived","options":{}},
  "id":"webhook-cowork","name":"Webhook Cowork","type":"n8n-nodes-base.webhook","typeVersion":2,"position":[200,1050],"webhookId":"vixeee-publicar"
}
nodes.append(wh)
add_conn("Webhook Cowork", ["Dia 1 Dados"])

# ---- Config -> Telegram + IG feed container + IG story container ----
add_conn("Config", ["Telegram sendPhoto","IG feed container","IG story container"])

# Telegram
nodes.append({
  "parameters":{"method":"POST","url":"=https://api.telegram.org/bot{{$json.tgToken}}/sendPhoto","sendQuery":True,
    "queryParameters":{"parameters":[
      {"name":"chat_id","value":"={{$json.chatId}}"},
      {"name":"photo","value":"={{$json.image_url}}"},
      {"name":"caption","value":"={{$json.legenda_tg}}"}]},"options":{}},
  "id":"telegram-sendphoto","name":"Telegram sendPhoto","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[950,350]})

# IG FEED container -> espera -> publicar
nodes.append({
  "parameters":{"method":"POST","url":"=https://graph.facebook.com/v21.0/{{$json.igUserId}}/media","sendQuery":True,
    "queryParameters":{"parameters":[
      {"name":"image_url","value":"={{$json.image_url_ig_post}}"},
      {"name":"caption","value":"={{$json.legenda_ig}}"},
      {"name":"access_token","value":"={{$json.igToken}}"}]},"options":{}},
  "id":"ig-feed-container","name":"IG feed container","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[950,600]})
nodes.append({
  "parameters":{"resume":"timeInterval","amount":30,"unit":"seconds"},
  "id":"espera-feed","name":"Espera feed","type":"n8n-nodes-base.wait","typeVersion":1.1,"position":[1180,600],"webhookId":"espera-feed"})
nodes.append({
  "parameters":{"method":"POST","url":"=https://graph.facebook.com/v21.0/{{$('Config').item.json.igUserId}}/media_publish","sendQuery":True,
    "queryParameters":{"parameters":[
      {"name":"creation_id","value":"={{$('IG feed container').item.json.id}}"},
      {"name":"access_token","value":"={{$('Config').item.json.igToken}}"}]},"options":{}},
  "id":"ig-feed-publicar","name":"IG feed publicar","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[1410,600],
  "retryOnFail":True,"maxTries":5,"waitBetweenTries":20000})

# IG STORY container -> espera -> publicar
nodes.append({
  "parameters":{"method":"POST","url":"=https://graph.facebook.com/v21.0/{{$json.igUserId}}/media","sendQuery":True,
    "queryParameters":{"parameters":[
      {"name":"image_url","value":"={{$json.image_url_ig_story}}"},
      {"name":"media_type","value":"STORIES"},
      {"name":"access_token","value":"={{$json.igToken}}"}]},"options":{}},
  "id":"ig-story-container","name":"IG story container","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[950,850]})
nodes.append({
  "parameters":{"resume":"timeInterval","amount":30,"unit":"seconds"},
  "id":"espera-story","name":"Espera story","type":"n8n-nodes-base.wait","typeVersion":1.1,"position":[1180,850],"webhookId":"espera-story"})
nodes.append({
  "parameters":{"method":"POST","url":"=https://graph.facebook.com/v21.0/{{$('Config').item.json.igUserId}}/media_publish","sendQuery":True,
    "queryParameters":{"parameters":[
      {"name":"creation_id","value":"={{$('IG story container').item.json.id}}"},
      {"name":"access_token","value":"={{$('Config').item.json.igToken}}"}]},"options":{}},
  "id":"ig-story-publicar","name":"IG story publicar","type":"n8n-nodes-base.httpRequest","typeVersion":4.2,"position":[1410,850],
  "retryOnFail":True,"maxTries":5,"waitBetweenTries":20000})

add_conn("IG feed container", ["Espera feed"])
add_conn("Espera feed", ["IG feed publicar"])
add_conn("IG story container", ["Espera story"])
add_conn("Espera story", ["IG story publicar"])

wf = {"id":"vixeeepub01","name":"Vixeee Que Barato — Publicador","nodes":nodes,
      "connections":conns,"active":False,"settings":{"executionOrder":"v1"},"tags":[]}

open("n8n_vixeee_v2.json","w").write(json.dumps(wf, ensure_ascii=False))
print("OK: n8n_vixeee_v2.json gerado — nós:", len(nodes))
print("Exemplo URL GitHub:", gh("dia1_post.jpg"))
