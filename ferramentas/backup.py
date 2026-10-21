"""Gera um backup completo dos dados da Noxen em backups/noxen-dados-AAAA-MM-DD-HHMM.tar.gz.

Uso:  py ferramentas/backup.py

O arquivo leva tudo o que foi registrado (CRM, fichas, conteúdos, Estúdio, buscas salvas,
base estratégica, instruções do Diretor e ferramentas) mais, se existirem:
  - backups/banco/*.json          exportações do banco da Central publicada (feitas pelo Diretor)
  - backups/extras/                arquivos originais fora do projeto (carrosséis em alta, logos, PDFs)
  - backups/buscador/*.tar.gz      dados do buscador exportados do Docker
Para restaurar em outra máquina, veja RESTAURAR.md dentro do arquivo.
"""
import sys
import tarfile
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
INCLUIR = ["CLAUDE.md", ".claude/agents", "crm", "clientes", "agencia", "central/conteudo", "central/app.html",
           "central/index.html", "central/LEIA-ME.md", "painel.html", "ferramentas/gerar_painel.py",
           "ferramentas/painel_modelo.html", "ferramentas/gerar_central.py", "ferramentas/baixar_buscas.py",
           "ferramentas/backup.py", "docker-compose.yml", "docker", ".gitignore", ".gitmodules", "README.md",
           "RESTAURAR.md", "restaurar.ps1", "restaurar.sh", ".gitattributes", "modelos", "central/conteudo.exemplo", ".claude/launch.json"]
EXTRAS = ["backups/banco", "backups/extras", "backups/buscador"]


def main():
    destino = BASE / "backups" / f"noxen-dados-{datetime.now():%Y-%m-%d-%H%M}.tar.gz"
    destino.parent.mkdir(exist_ok=True)
    n = 0
    with tarfile.open(destino, "w:gz") as tar:
        for item in INCLUIR + EXTRAS:
            p = BASE / item
            if p.exists():
                tar.add(p, arcname=f"noxen/{item}", filter=lambda t: None if "__pycache__" in t.name else t)
                n += 1
    print(f"Backup criado: {destino} ({destino.stat().st_size / 1e6:.1f} MB, {n} itens)")


if __name__ == "__main__":
    sys.exit(main())
