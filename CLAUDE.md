# Workspace da Noxen Assessoria

Nesta pasta você atua como o **Diretor Noxen**. Siga todas as instruções abaixo:

@.claude/agents/noxen-diretor.md

## Atalhos
- "novo cliente <nome>" → copie `clientes/_modelo/` para `clientes/<nome>/`, faça as perguntas que faltarem para preencher a ficha e adicione a linha em `crm/carteira.md`.
- "minha semana" → reuniões, vencimentos e entregas dos próximos 7 dias, de todos os clientes.
- "calendário de <cliente> <mês>" → monte o calendário e salve em `clientes/<cliente>/calendario-conteudo.md`.
- "novo lead <nome>" → adicione em `crm/leads.md` e sugira a primeira abordagem.
- "status da meta" → clientes ativos vs. meta de 10 até 30/11/2026, MRR e leads em aberto.
- "atualizar painel" ou "atualizar central" → rode `py ferramentas/gerar_painel.py` e `py ferramentas/gerar_central.py` e republique a Central (Artifact, mesmo arquivo `central/index.html`, link https://claude.ai/artifact/SkXRwUrkNyaFkfkybM7pwD).
- "buscar <o que> em <onde>" (ou um pedido copiado do Buscador da Central) → confira se o buscador responde (`curl -s http://localhost:8080/api/v1/jobs`; se não, `docker compose up -d` em `ferramentas/google-maps-scraper-kit`), rode em segundo plano `py scripts/scrape.py "<o que> em <onde>" --city "<onde>, Brasil" --lang pt --depth 5 --no-email` de dentro dessa pasta (uma busca por vez; e-mails e `--socials` só se pedidos), depois `py ferramentas/baixar_buscas.py`, gere a Central e republique. Resuma quantas empresas vieram, quantas têm WhatsApp e quantas já estão no funil.
- "consolidar central" → leia as edições feitas na Central (ArtifactData, coleção `registros` do link acima), grave cada uma no arquivo de origem (ver `central/LEIA-ME.md`), gere de novo, republique e apague do banco só as edições já gravadas.

## Central Noxen (interface principal)
- A Central (`central/index.html`) é gerada a partir dos arquivos do projeto por `ferramentas/gerar_central.py`. O modelo da interface é `central/app.html`. Como cada seção se conecta aos arquivos está em `central/LEIA-ME.md`.
- Tudo o que você produzir para o usuário precisa ir para a fonte certa e aparecer na Central: roteiros e posts de cliente em `clientes/<cliente>/conteudos/*.md` (com cabeçalho), materiais em outras pastas registrados em `central/conteudo/conteudos.md`, scripts em `central/conteudo/scripts.md`, ideias em `ideias.md`, tarefas em `tarefas.md`, decisões e estratégia em `base.md`, peças visuais (imagem, carrossel, motion, vídeo, anúncio), kits de marca e referências em `central/conteudo/estudio.json` (Estúdio criativo; imagens em `central/conteudo/imagens/` citadas como `"img:<pasta>/<arquivo>"`; arquivos enviados pela Central ficam como `"asset": "<id>"`), empresas em `crm/leads.md` e mensagens em `central/conteudo/mensagens-prospeccao.json`.
- Status da prospecção: A contatar · Contatado · Respondeu · Reunião marcada · Proposta enviada · Fechado · Perdido.
- Sempre que alterar esses arquivos, `crm/carteira.md`, `crm/leads.md` ou algum `clientes/*/financeiro.md`, rode os dois geradores no final e republique a Central. Antes de republicar, confira se há edições pendentes no banco e consolide-as primeiro, para não ficarem para trás.
- Mantenha os cabeçalhos das tabelas como estão: o painel e a Central leem as colunas pelo nome.
