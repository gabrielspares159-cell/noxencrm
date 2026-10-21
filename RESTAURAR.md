# Restaurar a Noxen em outra máquina

## Do backup (tar.gz)
1. Instale **Docker Desktop**, **Git** e **Python 3.12+**, e deixe pelo menos 5 GB livres no disco do Docker.
2. Copie o arquivo `noxen-dados-AAAA-MM-DD-HHMM.tar.gz` para a pasta onde a Noxen vai ficar.
3. No Windows (PowerShell), dentro dessa pasta:
   ```powershell
   .\restaurar.ps1 -Arquivo .\noxen-dados-AAAA-MM-DD-HHMM.tar.gz
   ```
   No Linux ou Mac: `bash restaurar.sh noxen-dados-AAAA-MM-DD-HHMM.tar.gz`
   (os dois scripts também vêm dentro do backup: extraia com `tar -xzf arquivo.tar.gz` e eles aparecem em `noxen/`).
4. O script:
   - extrai os arquivos para `noxen/`;
   - baixa o buscador em `ferramentas/google-maps-scraper-kit`;
   - devolve as buscas salvas ao volume do Docker, se o backup tiver;
   - roda `docker compose up -d`.

## Do repositório git
```bash
git clone --recurse-submodules <URL do repositório> noxen
cd noxen
docker compose up -d
```

## Depois de restaurar
- **Central local:** http://localhost:8090. **Painel antigo:** http://localhost:8090/painel. **Buscador:** http://localhost:8080.
- **A Central publicada** (https://claude.ai/artifact/SkXRwUrkNyaFkfkybM7pwD) continua a mesma, porque fica no claude.ai. Abra o Claude Code na pasta `noxen` e o Diretor Noxen volta a funcionar com o `CLAUDE.md`.
- **Edições feitas na Central publicada** ficam no banco do claude.ai e não estão no tar.gz, a não ser que tenham sido consolidadas antes ("consolidar central"). O backup traz em `backups/banco/` o que havia no banco no dia.
- **Arquivos originais fora do projeto** (carrossel em alta, logos, fotos, PDF do benchmark) estão em `backups/extras/`.
