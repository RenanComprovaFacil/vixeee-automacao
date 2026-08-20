# workflow/ — o n8n versionado

O workflow em PRODUCAO ("Vixeee Que Barato — Publicador", id `vixeeepub01`)
ainda vive DENTRO do container Docker na VM Oracle e NAO esta' neste repo.
Coloca-lo aqui, SEM segredos, e' entrega da Fase 0.

## Como versionar (Fase 0)
1. Exportar da VM (via SSH):
   ```
   docker exec n8n n8n export:workflow --id=vixeeepub01 --output=/tmp/wf.json
   docker cp n8n:/tmp/wf.json ./vixeee-publicador.json
   ```
2. REMOVER os segredos: o no' `Config` carrega `igToken`, `tgToken`, etc. em
   texto puro. Migrar para Credentials do n8n ou variaveis de ambiente e deixar
   o JSON apenas REFERENCIANDO — nunca contendo — os valores.
3. So' entao commitar `vixeee-publicador.json`.

## gen_workflow.py
Gerador que monta o JSON do workflow a partir dos dados. A versao atual esta'
no `backup_tecnico_vixeee.zip` no PC do Renan (ver
`docs/IMPORTAR-ARQUIVOS-EXISTENTES.md`). A meta da Fase 1 e' reescreve-lo para
LER `dados/semana.json` em vez de embutir os dados.
