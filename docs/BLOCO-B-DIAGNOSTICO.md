# Bloco B — Diagnóstico do servidor (só leitura)

> **Fase 0.** Nenhum comando aqui altera qualquer coisa: são todos de leitura.
> Podem ser rodados a qualquer hora, **inclusive durante o post das 19h**.
> Quem executa: **Renan** (a chave SSH é dele). Cole o resultado de volta no chat.

Abrir o SSH primeiro (o caminho da chave e o IP estão em `SEGREDOS.local.md`):

```bash
ssh -i "<CAMINHO_DA_CHAVE_SSH>" ubuntu@<IP_DA_VM>
```

---

## B1 — O post das 19h está saindo às 19h de Brasília?

**Por quê:** há uma suspeita antiga de que o container esteja em UTC. Se estiver, o
post sai às **16h** de Brasília e ninguém percebeu até hoje.

```bash
echo "== host ==" && date && \
echo "== container ==" && sudo docker exec n8n date && \
echo "== variaveis de fuso ==" && (sudo docker exec n8n printenv | grep -Ei 'TZ|TIMEZONE' || echo "NENHUMA definida")
```

**Como ler o resultado:**
- `-03` ou `BRT` no container → está certo, nada a fazer.
- `UTC` ou `+00` → **confirmado o desvio de 3 horas**, entra no Bloco C.

---

## B2 — Como esse container foi criado? ⚠️ (o comando mais importante do Bloco B)

**Por quê:** para tirar as senhas de dentro do n8n é preciso recriar o container com
variáveis de ambiente. Mas o comando original que criou esse container **não está
documentado em lugar nenhum**. Sem saber o caminho exato do volume, recriar significa
**perder o banco do n8n** — todos os workflows e credenciais junto.

```bash
sudo docker inspect n8n --format '{{json .Config.Env}}' && \
echo "--- VOLUMES ---" && sudo docker inspect n8n --format '{{json .Mounts}}' && \
echo "--- PORTAS ---" && sudo docker inspect n8n --format '{{json .NetworkSettings.Ports}}' && \
echo "--- IMAGEM / RESTART ---" && sudo docker inspect n8n --format '{{.Config.Image}} | {{.HostConfig.RestartPolicy.Name}}'
```

**O que fazer com o resultado:** cole no chat. Eu monto o comando `docker run` exato e
verdadeiro, e registro ele no `docs/INFRA.md` — para nunca mais ficarmos sem essa
informação.

---

## B3 — A VM está na zona de risco de ser recolhida pela Oracle?

**Por quê:** a Oracle apaga máquinas gratuitas que passam 7 dias com CPU **e** rede
abaixo de 20%. Uma VM que só publica 1 post por dia fica bem abaixo disso — e a
automação sumiria sem aviso.

```bash
echo "== carga ==" && uptime && cat /proc/loadavg && \
echo "== memoria ==" && free -m && \
echo "== rede (bytes rx/tx acumulados) ==" && awk 'NR>2 {print $1, $2, $10}' /proc/net/dev && \
echo "== crontab atual ==" && (crontab -l 2>/dev/null || echo "sem crontab do usuario")
```

**Como ler:** load average constantemente abaixo de 0,2 numa máquina de 1/8 de OCPU
significa **abaixo do gatilho**. Com esse número na mão decidimos entre instalar o
keep-alive ou aceitar o risco por escrito.

---

## B4 — O workflow que está no ar é igual ao que versionamos?

**Por quê:** o JSON que importamos veio do backup de 19/08. Se alguém mexeu no n8n
depois disso, o repositório estaria guardando uma versão desatualizada.

```bash
sudo docker exec n8n n8n export:workflow --id=vixeeepub01 --output=/tmp/wf.json && \
sudo docker cp n8n:/tmp/wf.json ~/wf_live.json && \
wc -c ~/wf_live.json && \
grep -o '"name": *"[^"]*"' ~/wf_live.json | wc -l
```

Depois, **no PowerShell do PC** (não no SSH):

```powershell
scp -i "<CAMINHO_DA_CHAVE_SSH>" ubuntu@<IP_DA_VM>:~/wf_live.json "$env:USERPROFILE\Downloads\wf_live.json"
```

> ⚠️ **Salve em `Downloads`, nunca dentro da pasta do repositório.** Esse arquivo sai
> do servidor **com os tokens em texto puro**. O `.gitignore` já bloqueia o nome
> `wf_live.json`, mas não conte só com isso.

**Como ler:** o arquivo deve ter 23 nós. Me avise o número e eu comparo com o
versionado.

---

## B5 — Existe alguma máquina A1 esquecida na conta Oracle?

**Por quê:** a Oracle cortou pela metade a cota gratuita do tipo A1 (de 4 OCPU/24 GB
para 2 OCPU/12 GB) e começou a **apagar** as que passavam do limite em 18/08/2026.

**Onde:** Oracle Cloud Console → **Compute → Instances** → filtrar por *Todos os
compartimentos*.

**O que anotar:** existe alguma instância com shape `VM.Standard.A1.Flex`? Quantos
OCPUs? Qual o estado (`Running` / `Terminated`)?

> ⚠️ **Só olhar.** Não clicar em *Stop* nem *Terminate* em nada — parar a
> `n8n-afiliados` troca o IP público da VM.

---

## Resumo do que preciso de volta

| # | O que colar no chat |
|---|---|
| B1 | a saída do `date` do container |
| B2 | **a saída completa do `docker inspect`** — a mais importante |
| B3 | load average, memória e se existe crontab |
| B4 | o número de nós do `wf_live.json` |
| B5 | existe A1? qual estado? |

Com isso eu fecho o diagnóstico e monto o Bloco C (a janela de manutenção) com os
comandos exatos e o rollback escrito.
