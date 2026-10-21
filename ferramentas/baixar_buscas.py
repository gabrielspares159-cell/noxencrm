"""Baixa os resultados do buscador de empresas (Google Maps Scraper Kit) para crm/buscas/.

Uso:  py ferramentas/baixar_buscas.py

O buscador roda em http://localhost:8080 (Docker, pasta ferramentas/google-maps-scraper-kit).
Para cada busca concluída ("ok") que ainda não foi baixada, salva um CSV só com os campos
úteis para prospecção. A Central (ferramentas/gerar_central.py) lê esses arquivos e mostra
as buscas na seção "Buscador de empresas", prontas para importar na Prospecção.
"""
import csv
import io
import json
import os
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path

BASE_URL = os.environ.get("SCRAPER_BASE_URL", "http://localhost:8080")
PASTA = Path(__file__).resolve().parent.parent / "crm" / "buscas"
CAMPOS = ["title", "category", "phone", "emails", "website", "address", "review_rating", "review_count", "link"]


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]


def get(caminho):
    with urllib.request.urlopen(BASE_URL + caminho, timeout=60) as r:
        return r.read()


def main():
    try:
        jobs = json.loads(get("/api/v1/jobs"))
    except Exception as e:
        sys.exit(f"Buscador fora do ar em {BASE_URL}. Rode 'docker compose up -d' em ferramentas/google-maps-scraper-kit.\n({e})")
    PASTA.mkdir(parents=True, exist_ok=True)
    novos = 0
    for job in jobs:
        if job.get("Status") != "ok":
            continue
        data = (job.get("Date") or "")[:10]
        palavras = ", ".join(job.get("Data", {}).get("keywords", []))
        nome = job.get("Name") if job.get("Name") not in (None, "", "scrape-py", "job") else (palavras or job["ID"][:8])
        destino = PASTA / f"{data}-{slug(nome)}-{job['ID'][:6]}.csv"
        if destino.exists():
            continue
        bruto = get(f"/api/v1/jobs/{job['ID']}/download").decode("utf-8", "replace")
        linhas = list(csv.DictReader(io.StringIO(bruto)))
        with destino.open("w", newline="", encoding="utf-8-sig") as f:
            f.write(f"# busca: {nome} | palavras: {'; '.join(job.get('Data', {}).get('keywords', []))} | data: {data}\n")
            w = csv.DictWriter(f, fieldnames=CAMPOS, extrasaction="ignore")
            w.writeheader()
            w.writerows(linhas)
        novos += 1
        print(f"  baixada: {destino.name} ({len(linhas)} empresas)")
    print(f"Pronto: {novos} busca(s) nova(s) em {PASTA}")


if __name__ == "__main__":
    sys.exit(main())
