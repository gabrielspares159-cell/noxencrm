"""Gera painel.html a partir dos arquivos do CRM da Noxen.

Uso:  py ferramentas/gerar_painel.py   (rodar de dentro da pasta Noxen ou de qualquer lugar)

Lê crm/carteira.md, crm/leads.md e clientes/*/financeiro.md. Os cálculos de datas
(vencimentos, reuniões) são feitos no navegador, então o painel continua certo nos
dias seguintes mesmo sem gerar de novo — gere de novo só quando os arquivos mudarem.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent


def ler_tabelas(caminho):
    """Retorna as tabelas markdown do arquivo como listas de dicts (chave = cabeçalho)."""
    if not caminho.exists():
        return []
    tabelas, atual, cabecalho = [], None, None
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha.startswith("|"):
            if atual is not None:
                tabelas.append(atual)
            atual, cabecalho = None, None
            continue
        celulas = [c.strip() for c in linha.strip("|").split("|")]
        if cabecalho is None:
            cabecalho, atual = celulas, []
        elif all(re.fullmatch(r":?-+:?", c) for c in celulas if c):
            continue
        elif any(celulas):
            atual.append(dict(zip(cabecalho, celulas)))
    if atual is not None:
        tabelas.append(atual)
    return tabelas


def primeira_tabela(caminho):
    tabelas = ler_tabelas(caminho)
    return tabelas[0] if tabelas else []


def main():
    carteira = primeira_tabela(BASE / "crm" / "carteira.md")
    leads = primeira_tabela(BASE / "crm" / "leads.md")

    pagamentos = []
    for fin in sorted((BASE / "clientes").glob("*/financeiro.md")):
        pasta = fin.parent.name
        if pasta.startswith("_"):
            continue
        for tabela in ler_tabelas(fin):
            for linha in tabela:
                if "Status" in linha and "Vencimento" in linha:
                    pagamentos.append({"Pasta": pasta, **linha})

    dados = {
        "geradoEm": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "carteira": carteira,
        "leads": leads,
        "pagamentos": pagamentos,
    }
    json_seguro = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    modelo = (Path(__file__).parent / "painel_modelo.html").read_text(encoding="utf-8")
    saida = BASE / "painel.html"
    saida.write_text(modelo.replace("/*__DADOS__*/null", json_seguro), encoding="utf-8")
    print(f"Painel gerado: {saida}  ({len(carteira)} clientes, {len(leads)} leads, {len(pagamentos)} pagamentos)")


if __name__ == "__main__":
    sys.exit(main())
