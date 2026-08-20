# Restrições técnicas do n8n desta VM (não violar)

> Estas regras foram descobertas resolvendo travas reais do workflow. Ignorá-las causa retrabalho — releia antes de editar o fluxo.

1. **Nós Code FALHAM.** O task runner (`127.0.0.1:5679`) não conecta e/ou não há Python nesta VM. O workflow tem que ser construído **sem nenhum nó Code**.

2. **Expressões complexas quebram.** Array-literal e ternário aninhado dão erro; `jsonBody` combinado com `JSON.stringify` não é digerido corretamente pelo n8n aqui. Usar `sendQuery` + `queryParameters` e expressões simples do tipo `={{$json.campo}}`. Foi assim que os nós de Telegram e de Instagram passaram a funcionar de forma estável.

3. **Nomes de nó são referenciados fixos nas expressões dos publicadores do IG**, por exemplo `={{$('Config').item.json.igToken}}` e `={{$('IG feed container').item.json.id}}`. Renomear esses nós quebra o fluxo — se precisar renomear, atualizar todas as expressões que referenciam o nome antigo.

4. **Boot do container leva ~90–100 s** após `docker restart` (VM de 1 GB é lenta). Esperar esse tempo antes de disparar o webhook — senão a chamada retorna 404.

5. **O Instagram exige URL pública da imagem** — não aceita upload direto de bytes. Por isso as artes ficam hospedadas no GitHub (repo `RenanComprovaFacil/vixeee-artes`, ver `INFRA.md`).

6. **Erro 9007 do IG ("mídia não está pronta")** já foi mitigado com um nó "Espera 30s" antes de publicar, mais retry de 5x a cada 20s. Se reaparecer, aumentar a espera para 45–60s e reimportar o workflow.

7. **Container de mídia do IG não publicado expira em 24h.** Ao publicar Reels, consultar o status do container no máximo 1x por minuto, por até ~5 minutos.

8. **Deploy é só por SSH.** O "Run Command" da Oracle Cloud Agent não existe nesta instância — não há alternativa de deploy remoto sem SSH.

## Contexto do fluxo atual (referência)

- 7 gatilhos de agenda: `Agenda Dia 1` … `Agenda Dia 7`, cron `0 19 * * N`.
- 1 Webhook `POST /webhook/vixeee-publicar` — botão de teste manual, sempre posta o dia 1.
- Cada `Dia N Dados` (nó Set estático) carrega os campos do produto do dia.
- Nó `Config` (Set com `includeOtherFields=true`) injeta as credenciais no item.
- A partir daí, 3 ramos:
  - Telegram `sendPhoto`.
  - IG feed container → Espera 30s → IG feed publicar (com retry).
  - IG story container (`media_type=STORIES`) → Espera 30s → IG story publicar (com retry).
- **Alvo da Fase 1:** substituir os 7 nós Set estáticos por leitura de `dados/semana.json`.
