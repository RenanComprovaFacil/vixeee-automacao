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

---

## Restrições descobertas em 20/08/2026 (n8n **2.34.5**, testado na VM)

Todas verificadas executando de verdade, num workflow descartável sem nós de
publicação — nenhum post foi disparado para descobrir isto.

9. **`$env` está BLOQUEADO nos nós.** Expressão `{{$env.QUALQUER_COISA}}` falha com:

   ```
   NodeOperationError: access to env vars denied
   "...contact the administrator to remove the environment variable
    N8N_BLOCK_ENV_ACCESS_IN_NODE"
   ```

   No n8n 2.x isso passou a ser o **padrão**. Para liberar, é preciso recriar o
   container com `-e N8N_BLOCK_ENV_ACCESS_IN_NODE=false`.

10. **`raw.githubusercontent.com` serve `.json` como `text/plain; charset=utf-8`.**
    Sem forçar o formato, o nó HTTP Request entrega o corpo como **string** e
    `$json.produtos` vira `undefined` — o fluxo publica campos vazios **em
    silêncio**. Obrigatório no nó:

    ```json
    "options": { "response": { "response": { "responseFormat": "json" } } }
    ```

11. **O n8n 2.x versiona workflows.** `import:workflow` cria uma versão nova com
    `activeVersionId = null`, mesmo que o workflow estivesse ativo. Sintoma:

    ```
    404 — Active version not found for workflow with id "..."
    ```

    A sequência correta de deploy é sempre:

    ```
    import:workflow  →  update:workflow --active=true  →  docker restart  →  esperar
    ```

12. **Não existe `delete:workflow` na CLI** (`Command "delete:workflow" not found`).
    Para remover um workflow, use a interface. Desativar pela CLI funciona.

13. **`n8n execute --id=...` não funciona** com a instância principal rodando:
    *"n8n Task Broker's port 5679 is already in use"*. É a mesma trava do item 1.
    Para testar um fluxo sem a interface, use um **Webhook com
    `responseMode: "lastNode"`** — a resposta HTTP traz a saída do último nó.

14. **Esperar o boot direito.** `GET /healthz` responde em ~35 s, mas o banco ainda
    não está pronto (`503 Database is not ready!`), e as rotas de webhook só são
    registradas depois disso. **Não use `sleep` fixo nem aceite qualquer resposta
    como "pronto"** — faça polling até receber um campo que o próprio fluxo produz.
    Boot completo observado: **~90 s**.
