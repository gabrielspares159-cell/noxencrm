#!/usr/bin/env bash
# Restaura a Noxen a partir de um backup tar.gz (ver RESTAURAR.md).
set -euo pipefail
tar -xzf "$1"
cd noxen
[ -f ferramentas/google-maps-scraper-kit/docker-compose.yml ] || git clone --depth 1 https://github.com/vzbaggio/google-maps-scraper-kit.git ferramentas/google-maps-scraper-kit
buscas=$(ls backups/buscador/*.tar.gz 2>/dev/null | head -1 || true)
if [ -n "$buscas" ]; then
  docker volume create noxen_gmaps_data >/dev/null
  docker run --rm -v noxen_gmaps_data:/to -v "$PWD/backups/buscador:/from" alpine sh -c "tar -xzf /from/$(basename "$buscas") -C /to"
fi
docker compose up -d
echo "Pronto. Central local: http://localhost:8090  ·  Buscador: http://localhost:8080"
