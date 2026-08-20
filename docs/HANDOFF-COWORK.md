Repo exportado · MD
# Repositório exportado para o Claude Code — vixeee-automacao
 
> Registrado em 19/08/2026. O plano de evolução foi consolidado num scaffold de
> repositório e entregue ao Renan como `vixeee-automacao.zip` (no chat do
> Cowork), para o Claude Code trabalhar localmente no PC dele. Cowork e Claude
> Code atuam como o mesmo time.
 
## O que tem no repo
Árvore da seção 5 do plano (`vixeee-automacao/`), com:
- `CLAUDE.md` — ponto de entrada (acordo de time, estado atual, regras de ouro, 1ª ação).
- `docs/`: `PLANO-EVOLUCAO.md` (o plano completo, verbatim), `ROADMAP.md` (Fases 0–6 como checklists), `CONTEXTO.md`, `INFRA.md` (sem segredos), `RESTRICOES-N8N.md`, `IMPORTAR-ARQUIVOS-EXISTENTES.md`.
- `dados/`: `semana.json` (exemplo/template com os 7 links reais da Semana 1; campos numéricos ainda `null`), `semana.schema.json` (valida), `semana.lock.json.example`.
- `captura/`, `midia/`, `workflow/`, `.github/workflows/` — stubs com TODOs por fase.
- `SEGREDOS.local.md` — credenciais reais, **gitignored** (não sobe pro GitHub).
- `.gitignore`, `README.md`, `.env.example`.
## Decisões tomadas nesta exportação
- Entrega em `.zip` (não escrita direto no PC — nenhuma pasta estava conectada).
- Credenciais reais num `SEGREDOS.local.md` gitignored (opção escolhida pelo Renan).
- IP da VM, chave SSH e conta Oracle também foram tirados dos docs versionados e
  movidos só pro `SEGREDOS.local.md` (pensando em repo público).
## Pendências que o Claude Code assume a partir daqui (Fase 0)
- Recuperar `backup_tecnico_vixeee.zip` do PC (workflow JSON + gen_workflow.py + produtos_semana1.json).
- Exportar o workflow vivo da VM e **limpar segredos** antes de commitar.
- **Rotacionar** Page Token IG, App Secret Meta e bot token Telegram (estavam em texto puro).
- `git init` + criar o repo no GitHub (decidir público vs privado — ver seção 3 do plano).