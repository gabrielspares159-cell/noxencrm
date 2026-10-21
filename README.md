# Noxen Assessoria

Workspace de marketing e vendas da Noxen: CRM em arquivos, Central de marketing e vendas e buscador de empresas, com o Claude atuando como **Diretor Noxen** (`CLAUDE.md` e `.claude/agents/noxen-diretor.md`).

> Este repositório é público e traz **só o código e a estrutura**. Os dados de clientes e prospecção (`crm/`, `clientes/<cliente>/`, `agencia/campanhas/`, `central/conteudo/`) ficam fora do git, guardados no backup tar.gz.
>
> - **Máquina nova com os seus dados:** restaure o backup (veja [RESTAURAR.md](RESTAURAR.md)).
> - **Começar do zero:** copie `modelos/crm/` para `crm/`. A Central usa os modelos vazios de `central/conteudo.exemplo/` até existir `central/conteudo/`.

## Rodar com Docker
```bash
git clone --recurse-submodules <URL> noxen
cd noxen
docker compose up -d
```
| Endereço | O que é |
|---|---|
| http://localhost:8090 | Central Noxen (versão local; as edições ficam no navegador) |
| http://localhost:8090/painel | Painel antigo |
| http://localhost:8080 | Buscador de empresas (Google Maps Scraper Kit) |

Comandos úteis:
- `docker compose run --rm gerador`: gera de novo a Central e o painel depois de mudar os arquivos.
- `docker compose --profile ferramentas run --rm baixar-buscas`: salva as buscas concluídas em `crm/buscas/` e gera a Central.
- `docker compose stop`: desliga tudo. Os dados do buscador ficam no volume `google-maps-scraper-kit_gmaps_data`.

A **Central completa** (edições sincronizadas entre aparelhos, envio de arquivos, IA) é a publicada no claude.ai: https://claude.ai/artifact/SkXRwUrkNyaFkfkybM7pwD

## Estrutura
| Pasta | Conteúdo |
|---|---|
| `crm/` | carteira, pipeline de leads, financeiro da Noxen, buscas salvas |
| `clientes/<cliente>/` | ficha, reuniões, financeiro, campanhas, resultados e conteúdos de cada cliente |
| `agencia/` | posicionamento e materiais da própria Noxen (estudos de prospecção, roteiros) |
| `central/` | modelo (`app.html`), dados curados (`conteudo/`) e guia (`LEIA-ME.md`) da Central |
| `ferramentas/` | geradores, backup e o buscador (submódulo `google-maps-scraper-kit`) |
| `docker/` | configuração do nginx da Central local |

## Backup e restauração
- `py ferramentas/backup.py` cria `backups/noxen-dados-AAAA-MM-DD-HHMM.tar.gz`.
- Para restaurar em outra máquina, veja [RESTAURAR.md](RESTAURAR.md).
