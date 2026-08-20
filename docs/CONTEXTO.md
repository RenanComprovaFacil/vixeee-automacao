# Contexto — Vixeee Que Barato

> Nenhum segredo/token/credencial neste arquivo. Este repositório é público.

## Objetivo

Renda extra passiva com links de afiliado (Shopee/Mercado Livre). O Instagram
**@vixeeequebarato** é a **vitrine**: publica a arte do produto (sem link clicável) e a
bio redireciona para o **Telegram** (e, no futuro, também WhatsApp), onde ficam os links
de afiliado clicáveis. Um workflow n8n publica sozinho, 24/7, numa VM Oracle gratuita —
sem intervenção manual no dia a dia.

- **Dono:** Renan
- **Fuso horário:** America/Sao_Paulo

## Marca

- **Nome:** Vixeee Que Barato
- **Instagram:** `@vixeeequebarato`
- **Nicho:** "achadinhos" (ofertas/descontos), tom divertido e descontraído
- **Regra de tom:** não usar o nome pessoal do dono em nenhuma peça publicada

**Paleta A — "Garimpo Quente":**

| Cor | Hex |
|---|---|
| Coral | `#FF5A5F` |
| Rosa | `#FF3E9A` |
| Amarelo | `#FFC93C` |
| Creme | `#FFF6EC` |
| Grafite | `#2B2B2B` |

- **Fonte:** Poppins
- **Logo:** um gatinho

## Funil

```
Instagram (arte, SEM link) → bio → Telegram → links de afiliado
```

No Instagram não é possível ter link clicável no post sem App Review da Meta — por isso
o link de afiliado vive no Telegram, e o Instagram funciona só como vitrine que puxa
tráfego para lá.

## Estado atual

**NO AR desde 19/08/2026.** Publica todo dia às 19h em três frentes:

- Instagram feed
- Instagram Stories
- Telegram

Rotação de **7 produtos**, um por dia da semana (dia1 = Segunda … dia7 = Domingo).

**Como funciona hoje (arquitetura atual do workflow n8n):**

1. Sete nós `Set` estáticos, um por dia da semana, com os dados do produto do dia embutidos.
2. Um nó `Config` injeta as credenciais.
3. Três ramos paralelos de publicação:
   - **Telegram** `sendPhoto` com a foto crua da Shopee.
   - **Instagram feed**: cria o container → espera 30s → publica, com retry.
   - **Instagram Stories**: mesmo fluxo do feed.

Também existe um **webhook manual de teste**, usado só para disparar uma publicação
avulsa fora do horário — ele sempre posta o produto do dia 1.

## Conteúdo da Semana 1 (já em uso)

11 links de afiliado Shopee no total: os 7 do Instagram/rotação diária + 4 extras
divulgados só no Telegram.

Os 7 produtos do Instagram, por dia, com o código do link curto
(formato completo `https://s.shopee.com.br/<código>`):

| Dia | Produto | Código do link |
|---|---|---|
| 1 (Seg) | Creatina | `1BLZIa17Jf` |
| 2 (Ter) | Papel de Parede | `6pzw37yAsH` |
| 3 (Qua) | Mini Processador | `8V8A291hge` |
| 4 (Qui) | Bomba de Ar | `80BtREU8te` |
| 5 (Sex) | Kit de Utensílios | `50YHrlnDfb` |
| 6 (Sáb) | Tênis de Carbono | `4fvRTAS9fq` |
| 7 (Dom) | Faca de Churrasco | `BT26uRHaU` |

**Artes:** 14 no total (post + story para cada um dos 7 dias), na Paleta A:
`diaN_post.jpg` (1080×1080) e `diaN_story.jpg` (1080×1920), hospedadas no repositório
público de artes.

## Critérios de garimpo (para as próximas semanas)

- Desconto ≥ 40%
- Comissão ≥ 12–15%
- Prova social alta (vendas/avaliações)
- Variedade de categoria
- Preço de impulso (< R$ 70)

## Shopee — situação da conta

Conta de afiliado **aprovada**. A API oficial (App ID + Secret) **não foi liberada** —
os links de afiliado saem manualmente do painel, via "Obter Link em Massa".

## Pendências / próximos passos

1. **Conferir timezone**: verificar se o post das "19h" está saindo às 19h de Brasília
   ou em UTC.
2. **Controle remoto pelo celular**: expor o webhook de disparo manual com Cloudflare
   Tunnel + header secreto.
3. **Telegram 3x/dia**: montar um segundo fluxo de publicação nos horários 10h/15h/20h.
4. **Mercado Livre**: importar os links assim que o Renan fornecer.
5. **Trocar os produtos da semana** — processo de curadoria/rotação semanal.
6. **Token do Instagram expira em ~11/10/2026** — precisa ser re-gerado antes disso.
