"""Gera central/index.html (a Central Noxen) a partir dos arquivos do projeto.

Uso:  py ferramentas/gerar_central.py

Fontes lidas (nada é alterado nelas):
  crm/carteira.md, crm/leads.md, crm/financeiro-noxen.md
  clientes/<cliente>/perfil.md, reunioes.md, financeiro.md, campanhas.md, resultados.md,
      calendario-conteudo.md e conteudos/*.md
  central/conteudo/scripts.md, ideias.md, tarefas.md, base.md, conteudos.md,
      mensagens-prospeccao.json
  central/conteudo/imagens/<grupo>/*.jpg (prévias de imagens)

O resultado é um único arquivo HTML com os dados embutidos (central/app.html + dados).
Edições feitas na própria Central ficam guardadas no banco do artifact publicado;
veja central/LEIA-ME.md.
"""
import base64
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_painel import ler_tabelas, primeira_tabela  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
# Dados curados da Central. Numa cópia nova (sem dados), usa os modelos vazios de central/conteudo.exemplo.
CONTEUDO = BASE / "central" / "conteudo"
if not CONTEUDO.exists():
    CONTEUDO = BASE / "central" / "conteudo.exemplo"


def slug(texto):
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]


def ler(caminho):
    return caminho.read_text(encoding="utf-8") if caminho.exists() else ""


def campos_lista(texto):
    """Linhas '- Chave: valor' de um markdown -> dict (chave como está no arquivo)."""
    out = {}
    for linha in texto.splitlines():
        m = re.match(r"^-\s+([^:]+):\s*(.*)$", linha.strip())
        if m:
            out[m.group(1).strip()] = m.group(2).strip()
    return out


def secoes(texto):
    """Divide em blocos '## Título'. Cada bloco: titulo, dados (linhas '- chave: valor' logo
    abaixo do título) e corpo (o resto, em markdown)."""
    blocos = []
    for parte in re.split(r"^## ", texto, flags=re.M)[1:]:
        linhas = parte.split("\n")
        titulo, resto = linhas[0].strip(), linhas[1:]
        dados, i = {}, 0
        while i < len(resto) and (resto[i].startswith("- ") and re.match(r"^- [a-zA-Zçã_]+:", resto[i])):
            k, v = resto[i][2:].split(":", 1)
            dados[k.strip().lower()] = v.strip()
            i += 1
        blocos.append({"titulo": titulo, "dados": dados, "corpo": "\n".join(resto[i:]).strip()})
    return blocos


def front_matter(texto):
    m = re.match(r"^---\n(.*?)\n---\n?(.*)$", texto, flags=re.S)
    if not m:
        return {}, texto
    dados = {}
    for linha in m.group(1).splitlines():
        if ":" in linha:
            k, v = linha.split(":", 1)
            dados[k.strip().lower()] = v.strip()
    return dados, m.group(2).strip()


def valor(chave_parcial, linha):
    for k, v in linha.items():
        if k.lower().startswith(chave_parcial.lower()):
            return v
    return ""


def grupo_prospect(lead):
    t = f"{lead.get('Lead / Empresa', '')} {lead.get('Segmento', '')}".lower()
    if lead.get("Origem") == "Indicação" or lead.get("Etapa") in ("Reunião marcada", "Proposta enviada"):
        return "Negociações"
    if "marmor" in t or "mármore" in t or "granito" in t:
        return "Marmorarias"
    if "planejad" in t or "marcenaria" in t:
        return "Planejados"
    if "esquadria" in t or "vidr" in t:
        return "Esquadrias"
    return "Varejo"


def clientes():
    carteira = primeira_tabela(BASE / "crm" / "carteira.md")
    out = []
    for linha in carteira:
        nome = linha.get("Cliente", "")
        pasta = BASE / "clientes" / slug(nome)
        perfil = campos_lista(ler(pasta / "perfil.md"))
        reunioes_txt = ler(pasta / "reunioes.md")
        fin_txt = ler(pasta / "financeiro.md")
        fin = campos_lista(fin_txt)
        historico = []
        for tabela in ler_tabelas(pasta / "reunioes.md"):
            historico += [r for r in tabela if "Pauta" in r]
        pagamentos = []
        for tabela in ler_tabelas(pasta / "financeiro.md"):
            pagamentos += [r for r in tabela if "Vencimento" in r and "Status" in r]
        campanhas = [r for t in ler_tabelas(pasta / "campanhas.md") for r in t if r.get("Campanha")]
        resultados = [r for t in ler_tabelas(pasta / "resultados.md") for r in t if r.get("Mês")]
        calendario = [r for t in ler_tabelas(pasta / "calendario-conteudo.md") for r in t if r.get("Data")]
        obs = ler(pasta / "perfil.md").split("## Observações")[-1].strip() if "## Observações" in ler(pasta / "perfil.md") else ""
        out.append({
            "id": slug(nome), "nome": nome, "pasta": f"clientes/{slug(nome)}",
            "segmento": linha.get("Segmento", ""), "cidade": linha.get("Cidade/UF", ""),
            "status": linha.get("Status", ""), "implementacao": valor("Implementa", linha),
            "mensalidade": valor("Mensalidade", linha), "vencimento": valor("Dia de venc", linha),
            "proximaReuniao": valor("Próxima reuni", linha), "responsavel": valor("Respons", linha),
            "perfil": perfil, "observacoes": obs,
            "reunioes": {"frequencia": campos_lista(reunioes_txt).get("Frequência combinada (ex.: quinzenal, toda 1ª segunda do mês)", ""),
                         "proxima": campos_lista(reunioes_txt).get("Próxima reunião (data e hora)", ""),
                         "historico": historico},
            "financeiro": {k: v for k, v in fin.items()}, "pagamentos": pagamentos,
            "campanhas": campanhas, "resultados": resultados, "calendario": calendario,
        })
    return out


def prospects():
    leads = primeira_tabela(BASE / "crm" / "leads.md")
    msgs = json.loads(ler(CONTEUDO / "mensagens-prospeccao.json") or "[]")
    por_lead = {m["lead"]: m for m in msgs}
    obs_txt = ler(BASE / "crm" / "leads.md").split("## Observações")[-1]
    obs = [l[2:].strip() for l in obs_txt.splitlines() if l.startswith("- ")]
    out = []
    for l in leads:
        nome = l.get("Lead / Empresa", "")
        m = por_lead.get(nome)
        if not m:  # mesma pessoa de contato de outro lead com mensagem (ex.: duas propostas para o mesmo contato)
            irmao = next((x for x in leads if x is not l and x.get("Contato") and x.get("Contato") == l.get("Contato") and x.get("Lead / Empresa") in por_lead), None)
            m = por_lead.get(irmao.get("Lead / Empresa")) if irmao else None
        chave = nome.split(" (")[0].lower()[:14]
        notas = [o for o in obs if chave and chave in o.lower()]
        passo, _, biblioteca = l.get("Próximo passo", "").partition(" — Biblioteca ")
        if biblioteca:
            notas.insert(0, "Biblioteca de Anúncios " + biblioteca)
        out.append({
            "id": slug(nome), "nome": nome, "contato": l.get("Contato", ""), "segmento": l.get("Segmento", ""),
            "cidade": l.get("Cidade/UF", ""), "origem": l.get("Origem", ""), "status": l.get("Etapa", ""),
            "proximaAcao": passo.strip(), "retorno": l.get("Data do próximo passo", ""),
            "valor": valor("Valor estimado", l), "grupo": grupo_prospect(l),
            "canal": (m or {}).get("canal", ""), "whatsapp": (m or {}).get("whatsapp", ""),
            "instagram": (m or {}).get("instagram", ""), "anuncio": (m or {}).get("anuncio", ""),
            "mensagem": (m or {}).get("mensagem", ""), "dica": (m or {}).get("nota", ""),
            "envioPlanejado": (m or {}).get("envioPlanejado", ""), "notas": notas,
        })
    return out


def colecao_secoes(arquivo, tipo):
    out = []
    for b in secoes(ler(CONTEUDO / arquivo)):
        out.append({"id": slug(b["titulo"]), "titulo": b["titulo"], **b["dados"], "texto": b["corpo"], "tipo": tipo})
    return out


def imagens(grupo):
    pasta = CONTEUDO / "imagens" / grupo
    return ["data:image/jpeg;base64," + base64.b64encode(p.read_bytes()).decode() for p in sorted(pasta.glob("*.jpg"))]


def conteudos(lista_clientes):
    out = []
    nomes = {c["id"]: c["nome"] for c in lista_clientes}
    for b in secoes(ler(CONTEUDO / "conteudos.md")):
        d = b["dados"]
        texto = ler(BASE / d["arquivo"]) if d.get("arquivo") else b["corpo"]
        out.append({"id": slug(b["titulo"]), "titulo": b["titulo"], "relacionado": d.get("relacionado", ""),
                    "formato": d.get("formato", ""), "objetivo": d.get("objetivo", ""), "status": d.get("status", ""),
                    "canal": d.get("canal", ""), "data": d.get("data", ""), "arquivo": d.get("arquivo", ""),
                    "imagens": imagens(d["imagens"]) if d.get("imagens") else [], "texto": texto})
    for arq in sorted((BASE / "clientes").glob("*/conteudos/*.md")):
        d, corpo = front_matter(ler(arq))
        out.append({"id": slug(arq.stem), "titulo": d.get("titulo", arq.stem), "relacionado": nomes.get(arq.parent.parent.name, arq.parent.parent.name),
                    "formato": d.get("formato", ""), "objetivo": d.get("objetivo", ""), "status": d.get("status", ""),
                    "canal": d.get("canal", ""), "data": d.get("data", ""), "arquivo": str(arq.relative_to(BASE)).replace("\\", "/"),
                    "extra": {k: v for k, v in d.items() if k not in ("titulo", "formato", "objetivo", "status", "canal", "data")},
                    "imagens": [], "texto": corpo})
    return out


def tarefas():
    linhas = primeira_tabela(CONTEUDO / "tarefas.md")
    return [{"id": l.get("ID") or slug(l.get("Tarefa", "")), "titulo": l.get("Tarefa", ""), "relacionado": l.get("Relacionado", ""),
             "prazo": l.get("Prazo", ""), "prioridade": l.get("Prioridade", ""), "status": l.get("Status", ""),
             "tipo": l.get("Tipo", ""), "obs": l.get("Observação", "")} for l in linhas]


def financeiro_noxen():
    texto = ler(BASE / "crm" / "financeiro-noxen.md")
    partes = {}
    for b in secoes(texto):
        tabelas = []
        atual = None
        for linha in b["corpo"].splitlines():
            if linha.startswith("|"):
                cel = [c.strip() for c in linha.strip("|").split("|")]
                if atual is None:
                    atual = {"cab": cel, "linhas": []}
                elif not all(re.fullmatch(r":?-+:?", c) for c in cel if c) and any(cel):
                    atual["linhas"].append(dict(zip(atual["cab"], cel)))
        partes[slug(b["titulo"])] = atual["linhas"] if atual else []
    return {"receitas": partes.get("receitas-avulsas", []), "despesas": partes.get("despesas", [])}


def expandir_imagens(valor):
    """Troca textos "img:<pasta>/<arquivo>" (em central/conteudo/imagens) pela imagem embutida."""
    if isinstance(valor, dict):
        return {k: expandir_imagens(v) for k, v in valor.items()}
    if isinstance(valor, list):
        return [expandir_imagens(v) for v in valor]
    if isinstance(valor, str) and valor.startswith("img:"):
        arq = CONTEUDO / "imagens" / valor[4:]
        if not arq.exists():
            print(f"  aviso: imagem não encontrada: {arq}")
            return ""
        tipo = "image/png" if arq.suffix.lower() == ".png" else "image/jpeg"
        return f"data:{tipo};base64," + base64.b64encode(arq.read_bytes()).decode()
    return valor


def estudio():
    texto = ler(CONTEUDO / "estudio.json")
    dados = json.loads(texto) if texto else {}
    return expandir_imagens({k: dados.get(k, []) for k in ("projetos", "kits", "referencias")})


def buscas():
    """Resultados do buscador de empresas salvos em crm/buscas/*.csv (ver ferramentas/baixar_buscas.py)."""
    out = []
    for arq in sorted((BASE / "crm" / "buscas").glob("*.csv"), reverse=True):
        texto = arq.read_text(encoding="utf-8-sig")
        meta = {}
        if texto.startswith("#"):
            primeira, texto = texto.split("\n", 1)
            for parte in primeira.lstrip("# ").split(" | "):
                if ":" in parte:
                    k, v = parte.split(":", 1)
                    meta[k.strip()] = v.strip()
        import csv as _csv
        import io as _io
        empresas = []
        for r in _csv.DictReader(_io.StringIO(texto)):
            nome = (r.get("title") or r.get("Nome") or "").strip()
            if not nome:
                continue
            empresas.append({"nome": nome, "categoria": r.get("category") or r.get("Categoria") or "",
                             "telefone": r.get("phone") or r.get("Telefone") or "", "email": r.get("emails") or r.get("E-mail") or "",
                             "site": r.get("website") or r.get("Site") or "", "endereco": r.get("address") or r.get("Endereço") or "",
                             "nota": r.get("review_rating") or r.get("Nota") or "", "avaliacoes": r.get("review_count") or r.get("Avaliações") or "",
                             "link": r.get("link") or r.get("Link Google Maps") or "", "whatsapp": r.get("WhatsApp") or ""})
        out.append({"id": slug(arq.stem), "arquivo": f"crm/buscas/{arq.name}", "titulo": meta.get("busca", arq.stem),
                    "palavras": meta.get("palavras", ""), "data": meta.get("data", ""), "empresas": empresas})
    return out


def main():
    lista_clientes = clientes()
    dados = {
        "geradoEm": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "meta": {"clientes": 10, "prazo": "30/11/2026"},
        "clientes": lista_clientes,
        "prospects": prospects(),
        "scripts": colecao_secoes("scripts.md", "script"),
        "ideias": colecao_secoes("ideias.md", "ideia"),
        "base": colecao_secoes("base.md", "base"),
        "conteudos": conteudos(lista_clientes),
        "tarefas": tarefas(),
        "financeiro": financeiro_noxen(),
        "estudio": estudio(),
        "buscas": buscas(),
    }
    json_seguro = json.dumps(dados, ensure_ascii=False).replace("</", "<\\/")
    modelo = ler(BASE / "central" / "app.html")
    saida = BASE / "central" / "index.html"
    saida.write_text(modelo.replace("/*__DADOS__*/null", json_seguro), encoding="utf-8")
    print(f"Central gerada: {saida}")
    print("  " + ", ".join(f"{k}: {len(v)}" for k, v in dados.items() if isinstance(v, list)))


if __name__ == "__main__":
    sys.exit(main())
