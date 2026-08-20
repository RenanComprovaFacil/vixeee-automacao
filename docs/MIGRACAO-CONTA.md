# Migração para conta pessoal + Cloudflare Pages

> **Motivo:** o projeto foi criado por engano na conta do GitHub da empresa. Além
> do nome aparecer na URL pública, projeto pessoal hospedado em conta corporativa
> cria ambiguidade sobre a titularidade do trabalho.
>
> **Estado:** planejado. Nada migrado ainda. A automação segue rodando normalmente.

---

## O ganho, além de trocar de conta

Hoje o repositório **precisa** ser público por dois motivos: o GitHub Pages serve
dele, e o Instagram busca as artes via `raw.githubusercontent`.

Saindo para o Cloudflare Pages, as artes e o `semana.json` passam a ser servidos
do próprio site. Aí **o repositório pode ser privado** e nada público aponta para
conta nenhuma do GitHub:

```
hoje    Instagram → raw.githubusercontent.com/<conta>/vixeee-artes/dia4_post.jpg
        bio       → <conta>.github.io/vixeee-automacao/

depois  Instagram → <subdominio>.pages.dev/artes/dia4_post.jpg
        bio       → <subdominio>.pages.dev
```

O GitHub vira um cofre privado de código. O nome da conta some da parte visível.

---

## Inventário — o que está amarrado à conta atual

| Item | Onde | Como resolver |
|---|---|---|
| 2 repositórios públicos | `vixeee-automacao`, `vixeee-artes` | recriar na conta pessoal, apagar os antigos |
| URL da página | GitHub Pages | trocar por `pages.dev` |
| Endereços no código | **centralizados em `config.json`** ✅ | editar 3 linhas |
| Autoria dos commits | 15 commits com `<conta>@users.noreply.github.com` | reescrever |
| URLs dentro do workflow n8n | 3 URLs | regerar + reimportar |

> ⚠️ **Apagar, não transferir.** A transferência de repositório deixa um
> redirecionamento permanente do endereço antigo para o novo — o rastro
> continua. Criar novos e apagar os antigos corta a ligação.

---

## Passo a passo

### Fase A — preparação (não afeta produção)

1. **Autenticar o `gh` na conta pessoal**
   ```bash
   gh auth login          # escolher a conta pessoal
   gh auth status         # confirmar
   ```
   Hoje o `gh` está autenticado na conta da empresa nesta máquina.

2. **Trazer as 14 artes para dentro do repositório**, em `publico/artes/`.
   Elas passam a ser servidas pelo Pages junto com a página.

   > *Compromisso assumido:* imagens versionadas fazem o histórico crescer
   > (~3 MB por semana). Aceitável por bastante tempo; se incomodar, o caminho é
   > mover as artes para o Cloudflare R2 ou reiniciar o histórico.

3. **Reescrever a autoria dos 15 commits** para o e-mail da conta pessoal
   (`git filter-branch` ou `rebase`; com 15 commits é instantâneo).

4. **Criar os repositórios privados** na conta pessoal e subir o histórico.

### Fase B — hospedagem

5. Criar conta na Cloudflare (só e-mail, sem cartão para o Pages).
6. Criar o projeto no Pages apontando para o repositório privado, com a pasta
   `publico/` como diretório de saída.
7. Escolher o subdomínio: `<algo>.pages.dev`. **Sugestão: não usar nome pessoal.**
8. Confirmar que respondem:
   - `https://<sub>.pages.dev`
   - `https://<sub>.pages.dev/artes/dia1_post.jpg`
   - `https://<sub>.pages.dev/dados/semana.json`

### Fase C — virar a chave (a parte sensível)

9. Editar o `config.json` com os 3 endereços novos.
10. Regerar: `python site/gen_site.py && python workflow/gen_workflow_v3.py`
11. Reimportar o workflow no n8n — **respeitando a sequência obrigatória**
    (`RESTRICOES-N8N.md`, item 11):
    ```
    import:workflow → update:workflow --active=true → docker restart → esperar ~90s
    ```
12. **Testar sem publicar** (fluxo de teste sem nós de publicação) e confirmar que
    as URLs novas respondem.
13. Trocar o link da bio no Instagram.

### Fase D — limpeza

14. Confirmar o post das 19h saindo normal com as URLs novas.
15. **Só então** apagar os dois repositórios da conta da empresa.
16. Remover a conta da empresa do `gh auth` nesta máquina.

---

## Ordem importa

**Não apague os repositórios antigos antes do passo 14.** Enquanto o n8n em
produção ainda apontar para as URLs antigas, apagá-los quebra a publicação. A
sequência segura é: novo no ar → migrar → confirmar → apagar o velho.

---

## Rollback

Se algo falhar na Fase C, é só reverter o `config.json` para os valores antigos,
regerar e reimportar. Os repositórios antigos ainda existem até o passo 15 — essa
é exatamente a razão de eles serem apagados por último.

---

## Depois: domínio próprio

Com o Cloudflare Pages no ar, apontar um `vixeeequebarato.com.br` (~R$40/ano) é
mudança de DNS, sem retrabalho no projeto. Fica melhor na bio e a marca ganha.
Não é pré-requisito de nada.
