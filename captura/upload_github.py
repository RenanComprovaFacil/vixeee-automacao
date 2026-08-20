#!/usr/bin/env python3
"""
upload_github.py — Sobe as artes (out/diaN_post.jpg e out/diaN_story.jpg) para o
repositório GitHub das artes, via API (não precisa de git instalado). Deixa o
fluxo 100% hands-off: as URLs raw ficam iguais às do workflow.

Precisa de um GitHub Token (PAT) com permissão de escrita no repo. O Renan cria
uma vez em github.com/settings/tokens (Fine-grained → repo vixeee-artes →
Contents: Read and write) e guarda em SEGREDOS.local.md. O Claude lê de lá.

USO:  GITHUB_TOKEN=xxxx python3 upload_github.py --owner RenanComprovaFacil --repo vixeee-artes --dir ./out
Se não houver token, este script falha de propósito — nesse caso use o caminho
manual (entregar out/ como zip e o Renan arrasta pro repo, mantendo os nomes).
"""
import os, sys, base64, json, argparse, urllib.request

def gh_api(method, url, token, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Authorization": f"Bearer {token}", "Accept":"application/vnd.github+json",
        "User-Agent":"vixeee-uploader", "X-GitHub-Api-Version":"2022-11-28"})
    try:
        return json.loads(urllib.request.urlopen(req).read())
    except urllib.error.HTTPError as e:
        if e.code == 404: return None
        raise

def put_file(owner, repo, path, local, token, branch="main"):
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    existing = gh_api("GET", url + f"?ref={branch}", token)
    payload = {"message": f"update {path}", "branch": branch,
               "content": base64.b64encode(open(local,"rb").read()).decode()}
    if existing and "sha" in existing:
        payload["sha"] = existing["sha"]   # sobrescreve o arquivo existente
    gh_api("PUT", url, token, payload)
    print(f"  subido: {path}")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--owner", required=True); ap.add_argument("--repo", required=True)
    ap.add_argument("--dir", default="./out"); ap.add_argument("--branch", default="main")
    a = ap.parse_args()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("Sem GITHUB_TOKEN no ambiente. Use o caminho manual (zip + arrastar no site).")
    files = sorted(f for f in os.listdir(a.dir) if f.endswith(".jpg"))
    if not files:
        sys.exit(f"Nenhum .jpg em {a.dir}")
    for f in files:
        put_file(a.owner, a.repo, f, os.path.join(a.dir, f), token, a.branch)
    print(f"OK: {len(files)} artes atualizadas em {a.owner}/{a.repo}@{a.branch}")

if __name__ == "__main__":
    main()
