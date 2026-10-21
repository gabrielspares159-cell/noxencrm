param([Parameter(Mandatory = $true)][string]$Arquivo)
# Restaura a Noxen a partir de um backup tar.gz (ver RESTAURAR.md).
$ErrorActionPreference = "Stop"
tar -xzf $Arquivo
Set-Location noxen
if (-not (Test-Path "ferramentas\google-maps-scraper-kit\docker-compose.yml")) {
    git clone --depth 1 https://github.com/vzbaggio/google-maps-scraper-kit.git ferramentas\google-maps-scraper-kit
}
$buscas = Get-ChildItem "backups\buscador\*.tar.gz" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($buscas) {
    docker volume create noxen_gmaps_data | Out-Null
    docker run --rm -v noxen_gmaps_data:/to -v "${PWD}\backups\buscador:/from" alpine sh -c "tar -xzf /from/$($buscas.Name) -C /to"
}
docker compose up -d
Write-Host "Pronto. Central local: http://localhost:8090  ·  Buscador: http://localhost:8080"
