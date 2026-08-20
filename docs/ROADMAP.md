# Roadmap de execução — Fases 0 a 6

> Baseado em `docs/PLANO-EVOLUCAO.md`. Sem segredos/tokens — este repositório é público.

## Decisões de abertura (responder antes de codar)

- [x] **Repositório público ou privado?** Público dá runner 4 vCPU/16 GB, minutos
      ilimitados de Actions e Releases públicos de graça; privado cai pela metade
      (2 vCPU/8 GB, 2.000 min/mês) e Releases não ficam públicos, o que quebra o
      requisito de URL pública do Instagram. Recomendação do plano: **público**, com
      todo segredo em GitHub Secrets — implica que legendas, produtos e pipeline ficam
      visíveis; avaliar se isso incomoda.
      > **DECIDIDO 19/08/2026: PUBLICO** — github.com/RenanComprovaFacil/vixeee-automacao
      > Como os tokens expostos NAO foram rotacionados (decisao do dono), todo push
      > passa antes por um portao de varredura de segredos, incluindo decodificacao
      > de base64.
- [ ] **Hospedagem do vídeo: GitHub Releases ou Cloudflare R2?** Releases evita cartão
      de crédito; R2 é mais robusto mas o domínio `r2.dev` é rate-limited/só-dev em
      produção (exige domínio custom) e provavelmente exige cartão no cadastro.
- [ ] **Vídeo: só o mp4 original da Shopee, ou também gerar vídeo a partir de imagem**
      para produtos sem vídeo? A segunda opção é bem mais trabalho.
- [ ] **Manter o funil "link na bio"** ou migrar o Instagram para link no primeiro
      comentário? A segunda opção exige App Review da Meta para o escopo
      `instagram_manage_comments`.
- [ ] **Migrar para IP reservado agora** (o endereço muda uma vez e nunca mais) ou
      continuar convivendo com o IP efêmero da VM?
- [ ] **Frequência final:** manter 1 post/dia às 19h, ou aproveitar a automação para
      2–3 janelas de publicação?

## Ordem recomendada

```
FASE 0  ──▶  FASE 1  ──▶  FASE 2  ──▶  FASE 3  ──▶  FASE 4  ──▶  FASE 5  ──▶  FASE 6
segurança    dados        captura      fábrica      publicar     medir      autonomia
   +         no repo      assistida    de mídia     em vídeo                (parcial)
fundação
```

**Fases 0 e 1 são inegociáveis e vêm primeiro** — sem repositório versionado e sem
segredos rotacionados/segregados, qualquer evolução só aumenta a dívida técnica.

**Se for para escolher uma única coisa para fazer primeiro** com retorno visível: a
**Fase 1**. Ela sozinha transforma a troca semanal de "editar 7 nós no n8n via túnel
SSH" em "um commit", e é pré-requisito de tudo o que vem depois.

---

## FASE 0 — Fundação e segurança

**Objetivo:** tirar o projeto de dentro do container Docker e parar de carregar
segredo em texto puro.

**Entregas**
- [x] Criar o repositório `vixeee-automacao` com a estrutura de pastas proposta
      (`.github/workflows/`, `captura/`, `dados/`, `midia/`, `workflow/`, `docs/`)
      > **FEITO 19/08/2026** — repo criado, `git init` e publicado em github.com/RenanComprovaFacil/vixeee-automacao (32 arquivos, 0 segredos)
- [x] Exportar o workflow `vixeeepub01` do container e commitar como
      `workflow/vixeee-publicador.json`
      > **FEITO 19/08/2026** — `workflow/vixeee-publicador.json` — 23 nos, id `vixeeepub01`; no `Config` sanitizado para `$env.*`
- [x] Commitar `gen_workflow.py`, `produtos_semana1.json` e os MDs de contexto,
      **renomeando** os arquivos cujos nomes estão trocados entre si
      > **FEITO 19/08/2026** — `gen_workflow.py` funcional (stub substituido), `produtos_semana1.json`, skill + scripts; `Repo exportado.md` -> `docs/HANDOFF-COWORK.md`
- [~] **Rotacionar todas as credenciais expostas:** Page Token do Instagram, App
      Secret da Meta, bot token do Telegram
      > **DISPENSADO pelo Renan em 19/08/2026** — decisao consciente do dono. Consequencia registrada: o repo e publico e os tokens expostos seguem validos, entao qualquer falha de sanitizacao vira credencial viva. Mitigacao adotada: portao de varredura (inclusive base64) obrigatorio antes de todo push.
- [x] Migrar os segredos do nó `Config` para **Credentials do n8n** ou variáveis de
      ambiente do container — o JSON versionado passa a referenciar, nunca a conter
      o segredo
      > **FEITO 19/08/2026** — JSON versionado referencia `$env.IG_USER_ID / IG_TOKEN / TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID`. **Falta aplicar no container** — Bloco C.
- [x] `.gitignore` cobrindo `*.env`, `autenticacao*`, `runme*.txt`
      > **FEITO 19/08/2026** — reforcado com `SEGREDOS*.md`, `*.zip`, `wf.json`, `n8n_vixeee_v2.json`, `cookies.json`, `storageState.json`, `*.log`; cobertura testada com `git check-ignore`
- [x] Definir `GENERIC_TIMEZONE=America/Sao_Paulo` e `TZ` no container e **confirmar**
      se "19h" está saindo às 19h de Brasília (pendência aberta desde o início)
      > **RESOLVIDO 20/08/2026 (Bloco B)** — `GENERIC_TIMEZONE=America/Sao_Paulo`
      > ja estava definida no container: os gatilhos sempre dispararam as 19h de
      > Brasilia. Falso alarme. `TZ` segue indefinida (afeta so log/formatacao,
      > nao o agendamento) — acrescentar `-e TZ=America/Sao_Paulo` na proxima
      > recriacao e cosmetico. Ver `docs/INFRA.md`.
- [ ] **Mitigar o risco de reclaim por ociosidade** da Oracle: cron leve na VM que
      mantenha CPU/rede acima de 20% do percentil 95 (janela de 7 dias), ou aceitar o
      risco de forma consciente e documentada
- [ ] Auditar a conta Oracle: existe alguma instância A1? Foi afetada pelo corte de
      cota efetivo em 18/08 (4 OCPU/24 GB → 2 OCPU/12 GB)?

**Critério de aceite:** dá para clonar o repositório num PC zerado, entender o
projeto inteiro e reconstruir o workflow — e nenhum token aparece em `git log -p`.

**Riscos/Restrições**
- Rotacionar o token do Instagram derruba a publicação até o novo token ser
  instalado — fazer isso fora do horário do post.
- IP efêmero da Oracle não vira reservado mantendo o mesmo endereço: parar a
  instância antes de resolver isso troca o IP.

---

## FASE 1 — Dados como fonte da verdade

**Objetivo:** eliminar os 7 nós `Set` hardcoded. Trocar a semana de produtos passa a
ser um único commit.

**Entregas**
- [ ] Definir e congelar o schema do `semana.json` (produtos, dia da semana, preços,
      desconto, comissão, `image_url`, `video_url`, `affiliate_link`, legendas)
- [ ] Reescrever o `gen_workflow.py` para gerar um workflow que **lê os dados**, em
      vez de embuti-los nos nós
- [ ] Novo desenho do workflow: `Schedule` → `HTTP Request` (lê o `semana.json` cru
      do GitHub) → `Switch` pelo dia da semana → ramos de publicação
- [ ] Rodar em paralelo com o workflow atual por 1 semana, e só então desligar o
      antigo

**Critério de aceite:** trocar os 7 produtos da semana sem abrir o n8n e sem SSH.

**Riscos/Restrições**
- Restrição herdada do n8n desta VM (não violar): **não aceita nó Code** (o task
  runner Python não conecta), **não aceita array-literal nem ternário aninhado** em
  expressão, e `jsonBody` + `JSON.stringify` não funciona. Usar `sendQuery` +
  `queryParameters` e expressões simples `={{$json.campo}}`.
- Boot do container leva ~90–100s após restart.

---

## FASE 2 — Captura assistida

**Objetivo:** reduzir a curadoria semanal de horas para minutos, e passar a capturar
também a URL do vídeo.

**Entregas**
- [ ] Adaptar `generate_script.py` + `console_script.js` (herdados do BestPriceToday)
      para o fluxo Vixeee
- [ ] **Mudar a saída:** em vez de baixar o mp4 no navegador, gravar a `video_url` no
      JSON — a CDN de vídeo da Shopee é geralmente pública, só o endpoint
      `/api/v4/item/get` exige sessão logada
- [ ] Integrar à skill: a skill orquestra o painel de afiliados, o extrator enriquece
      os dados
- [ ] Saída final: um `semana.json` válido contra o schema definido na Fase 1
- [ ] Ajustar os critérios de garimpo já definidos: desconto ≥ 40%, comissão ≥
      12–15%, prova social alta, variedade de categoria, preço de impulso (< R$ 70)
- [ ] Corrigir o bug herdado do extrator: itens marcados como `'erro'` nunca são
      reprocessados (o retry por `'timeout'` é código morto)

**Critério de aceite:** uma execução produz `semana.json` completo — 7 produtos com
nome, preço, preço original, %OFF, `image_url`, `video_url` e `affiliate_link`.

**Riscos/Restrições**
- A Shopee pode mudar o `/api/v4/item/get` ou apertar o anti-bot.
- O extrator já tem sleep de 4,5–9s por produto — **não reduzir**.

---

## FASE 3 — Fábrica de mídia

**Objetivo:** gerar os vídeos 9:16 automaticamente, de graça, sem tocar na VM Oracle.

**Entregas**
- [ ] Workflow do GitHub Actions disparado por push em `semana.json`
- [ ] Step explícito de instalação do ffmpeg — **ele não vem pré-instalado** nas
      imagens Ubuntu 22.04/24.04 do runner
- [ ] Baixar o mp4 da CDN → `crop` para 9:16 → `scale` → `drawtext` com preço e %OFF
      → `-c:v libx264 -c:a aac -movflags +faststart`
- [ ] **Validar contra os limites de mídia** antes de publicar: duração 3–60s
      (Stories) e ≤ 15 min (Reels); tamanho ≤ 100 MB (Stories) / ≤ 300 MB (Reels) /
      ≤ 20 MB (Telegram por URL); máx. 1920px na horizontal
- [ ] Gerar também as artes estáticas (fallback para produto sem vídeo)
- [ ] Publicar a mídia na CDN escolhida (Fase 0 das decisões de abertura) e gravar
      `semana.lock.json` com as URLs finais
- [ ] Um step que commite algo periodicamente, para o `schedule:` do Actions **não
      ser desativado automaticamente aos 60 dias sem atividade**

**Critério de aceite:** push no `semana.json` → em poucos minutos, 7 vídeos
publicados com URL pública, todos passando na validação de specs.

**Riscos/Restrições**
- **Explicitamente descartado: o `generate_offer_video` do BestPriceToday.** Nunca
  rodou em produção (Pillow/gTTS/ffmpeg nem estão no `requirements.txt`), é caro em
  disco (400 MB–1 GB de `/tmp` por vídeo), tem emoji quebrado (fontes DejaVu sem
  emoji colorido) e "música de fundo" que é literalmente um tom senoidal de 220 Hz.
  Se precisar gerar vídeo a partir de imagem, fazer do zero com
  `ffmpeg -loop 1 -i img.png -vf drawtext`.
- Arquivo acima de 100 MB é bloqueio duro no Git (push inteiro rejeitado); aviso
  entre 50 e 100 MB.

---

## FASE 4 — Publicação evoluída

**Objetivo:** sair de foto estática para vídeo, nos três canais.

**Entregas**
- [ ] Instagram feed: migrar para **Reels** (`media_type=REELS` + `video_url`)
      mantendo o fluxo de 2 passos com espera e retry, que já está resolvido
- [ ] Instagram Stories: vídeo em vez de imagem (atenção: limite de **60s e 100 MB**)
- [ ] Telegram: `sendVideo` — decidir entre URL (20 MB) e upload (50 MB); guardar o
      `file_id` para reenvio sem limite
- [ ] Manter o polling de status do container do Instagram (erro 9007 já mitigado
      com espera de 30s + retry 5x/20s; se voltar, subir para 45–60s)
- [ ] *(Opcional)* Facebook com link no primeiro comentário e fixado — sequência de
      3 chamadas Graph: `POST /{page_id}/photos` → `POST /{post_id}/comments` →
      `POST /{comment_id}` com `pinned=true`. **Usar o `post_id`, não o `id`.** Só
      vale a pena se houver página do Facebook ativa.

**Critério de aceite:** uma semana inteira publicada em vídeo, sem intervenção.

**Riscos/Restrições**
- Publicação no Instagram: limite de 100 posts por janela móvel de 24h por conta.
- Container do Instagram não publicado em 24h expira; Meta recomenda consultar
  status 1x por minuto, por no máximo 5 min.

---

## FASE 5 — Medição

**Objetivo:** parar de publicar às cegas — hoje não há como saber qual post gerou
qual clique.

**Entregas**
- [ ] Webhook n8n `GET /r/:code` → grava clique em SQLite → responde 302 para o
      link Shopee
- [ ] Schema mínimo: `short_links(code, affiliate_url, product_title, price, source,
      clicks, created_at, last_clicked_at)` + `clicks(id, code, ip, user_agent,
      referrer, clicked_at)`
- [ ] **Um código de short link por canal** (`dia1-ig`, `dia1-tg`, `dia1-fb`) — é
      isso que permite comparar canais
- [ ] Usar **incremento atômico no SQLite** (`SET clicks = clicks + 1`), **não**
      read-modify-write — esse bug existe no projeto de origem (BestPriceToday)
- [ ] Relatório semanal simples no Telegram: cliques por produto e por canal

**Critério de aceite:** ao fim da semana, dá para responder "qual produto e qual
canal trouxeram mais clique".

**Riscos/Restrições**
- **Simplificação deliberada:** o BestPriceToday separa `/r/{code}` (redirect) de
  `/r/{code}/go` (registro) por causa de uma página intersticial que não existe
  aqui. Registrar e redirecionar no mesmo endpoint.

---

## FASE 6 — Autonomia (o "24/7 sem tocar")

**Objetivo:** captura rodando sozinha na nuvem. **Avaliação honesta: parcialmente
alcançável** — três obstáculos concretos: o endpoint `/api/v4/item/get` exige sessão
logada (headless também precisa dos cookies); Chromium headless quer 700 MB–1,5 GB
de RAM, o que não cabe na VM de 1 GB junto do n8n; e a sessão da Shopee expira, então
sempre haverá um relogin humano periódico. O GitHub Actions não serve para esta
etapa — IP de datacenter estrangeiro num painel brasileiro logado é convite para
bloqueio.

**Entregas** (alvo realista: "roda sozinho e te chama quando precisa de você")
- [ ] Migrar a captura para Playwright com `storageState` (cookies exportados uma
      vez do Chrome logado)
- [ ] Rodar em VM com RAM suficiente — hoje esbarra no corte de cota do Ampere A1 e
      na indisponibilidade prática de A1 em São Paulo
- [ ] Alerta no Telegram quando a sessão cair, em vez de descobrir por acaso
- [ ] Fallback: a skill manual de captura continua funcionando

**Riscos/Restrições**
- Acesso automatizado pode conflitar com os termos do programa de afiliados da
  Shopee. É conta própria e decisão do dono, mas não é risco zero — considerar
  antes de investir aqui.
