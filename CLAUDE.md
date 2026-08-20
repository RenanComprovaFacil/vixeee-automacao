# CLAUDE.md — Vixeee Que Barato

Este arquivo é o ponto de partida para qualquer Claude (ou humano) que abrir este repositório. Leia-o inteiro antes de tocar em código, workflow ou servidor.

## O que é o projeto

**Vixeee Que Barato** é um projeto de renda extra passiva com links de afiliado (Shopee/Mercado Livre). O Instagram **@vixeeequebarato** funciona como **vitrine**: a bio redireciona para o Telegram (e, futuramente, WhatsApp), onde ficam os links clicáveis das ofertas. Um **n8n** publica sozinho, 24/7, rodando numa VM Oracle Cloud gratuita.

- **Dono/decisor:** Renan.
- **Fuso horário:** America/Sao_Paulo.

## Acordo de time

Dois "Claudes" trabalham no mesmo time de desenvolvimento deste projeto:

1. **Claude do Cowork** — preparou e exportou este repositório a partir do contexto acumulado do projeto (decisões, conteúdo, estado da automação).
2. **Você, Claude Code** — executa localmente no PC do Renan: git, GitHub, SSH na VM, ffmpeg, edição de arquivos, etc.

**Renan é o dono.** Ele cola os segredos, roda os comandos SSH quando necessário e aprova qualquer ação irreversível — publicar fora do horário, apagar algo, reimportar workflow no n8n, mexer na configuração do servidor. **Sempre confirme com ele antes de ações irreversíveis.**

## Estado atual — já está no ar (19/08/2026)

A automação está completa e publicando sozinha. **Não estamos partindo do zero — estamos evoluindo algo que já funciona.**

- Workflow em produção: **"Vixeee Que Barato — Publicador"** (id `vixeeepub01`), **ATIVO** no n8n da VM Oracle.
- Todo dia às 19h publica em 3 lugares:
  - Instagram feed (arte na Paleta A, com "link na bio");
  - Instagram Stories (arte vertical 9:16);
  - Telegram @vixeeequebarato (foto crua da Shopee + link de afiliado).
- Rotação de 7 produtos: dia1 = Segunda … dia7 = Domingo.
- Workflow antigo **"MVP Afiliados"** (id `qYppjoQcUVmpws4x`) está **DESLIGADO**.

## Problema central que este repositório resolve

O projeto não estava versionado em lugar nenhum e havia segredos em texto puro espalhados (nós do n8n, anotações, etc.). Este repositório passa a ser a **fonte da verdade**. A primeira dor a matar (Fase 0/1) é: tirar o projeto de dentro do container/VM e parar de carregar segredo em texto puro.

## Arquitetura-alvo

Princípio-guia: **a VM de 1 GB nunca renderiza nada — ela só dispara HTTP.** O trabalho pesado sai da VM e vai para camadas gratuitas com mais recurso.

| Camada | Função |
|---|---|
| 1. Captura | No navegador logado do Renan (1x/semana), exige sessão Shopee ativa + IP residencial |
| 2. Repositório | Este repo no GitHub — fonte da verdade de dados, mídia e workflow |
| 3. Fábrica de mídia | GitHub Actions (4 vCPU / 16 GB grátis), roda ffmpeg para gerar as artes/vídeos |
| 4. CDN pública | GitHub Releases ou Cloudflare R2 — o Instagram exige URL pública para publicar |
| 5. Publicação | n8n na VM Oracle — só dispara HTTP, permanece leve |
| 6. Medição | Short link próprio (n8n + SQLite) para medir cliques |

Detalhe completo em [`docs/PLANO-EVOLUCAO.md`](docs/PLANO-EVOLUCAO.md), seção 2.

## Regras de ouro (não violar)

1. **Segredos reais só em `SEGREDOS.local.md`** (arquivo local, listado no `.gitignore`). Nunca commitar token, senha ou chave de API. Rodar `git log -p` no histórico não pode revelar segredo nenhum.
2. **Fase 0 exige rotacionar os tokens já expostos** em texto puro (Page Token do Instagram, App Secret da Meta, bot token do Telegram) antes de — ou ao — tornar o repositório público. Rotacione **fora do horário do post (19h)**: trocar o token derruba a publicação até reinstalar a credencial nova.
3. O n8n desta VM tem **restrições duras**: sem nó Code, só expressões simples. Leia [`docs/RESTRICOES-N8N.md`](docs/RESTRICOES-N8N.md) **antes** de mexer no workflow.
4. **Não pare a instância Oracle.** O IP público é efêmero e muda se a instância for parada; reboot mantém o IP.
5. **Não renderize vídeo na VM** (ela tem 1/8 de OCPU e 1 GB de RAM). Isso é trabalho do GitHub Actions.
6. **Não commite binários (`.mp4` etc.) direto no repositório** — incha o histórico do Git e há limite duro de 100 MB por arquivo.

## Mapa dos documentos

- [`docs/PLANO-EVOLUCAO.md`](docs/PLANO-EVOLUCAO.md) — o plano completo. **Leia primeiro**, é a espinha dorsal do projeto.
- `docs/ROADMAP.md` — Fases 0–6 como checklists acionáveis.
- `docs/CONTEXTO.md` — marca, tom de voz, funil, estado atual, conteúdo da Semana 1.
- `docs/INFRA.md` — VM, n8n, deploy, acessos (sem segredos).
- `docs/RESTRICOES-N8N.md` — regras técnicas que não podem ser violadas no workflow.
- `docs/IMPORTAR-ARQUIVOS-EXISTENTES.md` — arquivos que ainda estão soltos no PC do Renan (workflow JSON, `gen_workflow.py`, produtos, artes) e onde cada um entra no repositório.
- `dados/semana.json` — fonte da verdade do conteúdo. Trocar a semana de posts = editar este arquivo.
- `SEGREDOS.local.md` — credenciais reais (gitignored, nunca commitado).

## Primeira ação recomendada

1. Ler [`docs/PLANO-EVOLUCAO.md`](docs/PLANO-EVOLUCAO.md), depois `docs/ROADMAP.md`.
2. Antes de codar, responder com o Renan as **6 decisões de abertura** da seção 3 do plano:
   - repositório público vs. privado;
   - CDN via GitHub Releases vs. Cloudflare R2;
   - vídeo só reaproveitado da Shopee vs. gerado a partir de imagem;
   - link na bio vs. link no 1º comentário;
   - reservar IP fixo da VM agora ou depois;
   - frequência final de publicação.
3. Começar pela **Fase 0** (fundação e segurança) e **Fase 1** (dados como fonte da verdade) — são inegociáveis e vêm antes de qualquer outra evolução.

Se for para escolher uma única coisa de maior retorno agora: **Fase 1**. Ela transforma a troca semanal de "editar 7 nós no n8n via SSH" em "um commit".
