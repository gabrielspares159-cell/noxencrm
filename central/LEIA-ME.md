# Central Noxen: como funciona

**Link da Central (privado, só você abre):** https://claude.ai/artifact/SkXRwUrkNyaFkfkybM7pwD

A Central reúne as duas interfaces antigas, o `painel.html` (clientes e financeiro) e a Central de Envio (prospecção), numa única aplicação com 9 seções: Visão geral, Clientes, Financeiro, Prospecção, Scripts, Conteúdos, Ideias, Planejamento e Base estratégica.

## De onde vêm os dados

Os arquivos do projeto continuam sendo a fonte principal. A Central é gerada a partir deles por `ferramentas/gerar_central.py`.

| Seção | Arquivos lidos |
|---|---|
| Clientes | `crm/carteira.md` + `clientes/<cliente>/perfil.md`, `reunioes.md`, `financeiro.md`, `campanhas.md`, `resultados.md` |
| Financeiro | mensalidades da carteira, histórico de `clientes/*/financeiro.md` e `crm/financeiro-noxen.md` (receitas avulsas e despesas) |
| Prospecção | `crm/leads.md` (empresas, status, próxima ação, retorno) + `central/conteudo/mensagens-prospeccao.json` (mensagem, WhatsApp, Instagram) |
| Scripts | `central/conteudo/scripts.md` |
| Conteúdos | `clientes/<cliente>/conteudos/*.md` (com cabeçalho) + `central/conteudo/conteudos.md` (registro dos materiais em outras pastas) |
| Ideias | `central/conteudo/ideias.md` |
| Planejamento | `central/conteudo/tarefas.md` + os retornos de `crm/leads.md`, as reuniões da carteira, os vencimentos e as datas dos conteúdos |
| Base estratégica | `central/conteudo/base.md` |
| Estúdio criativo | `central/conteudo/estudio.json` (projetos, kits de marca, referências) + imagens em `central/conteudo/imagens/<pasta>/`, citadas como `"img:<pasta>/<arquivo>"` |

## Buscador de empresas (Google Maps)

- **O que é:** o Google Maps Scraper Kit (`ferramentas/google-maps-scraper-kit`, que embrulha o `gosom/google-maps-scraper`) roda no Docker deste computador, em http://localhost:8080. Ele busca empresas por segmento e cidade e devolve nome, telefone, site, endereço, nota e avaliações (e, se pedido, e-mails e redes sociais).
- **Ligar e desligar:** dentro de `ferramentas/google-maps-scraper-kit`, rode `docker compose up -d` para ligar e `docker compose stop` para desligar. Os containers reiniciam sozinhos com o Docker Desktop.
- **Salvar no projeto:** `py ferramentas/baixar_buscas.py` baixa todas as buscas concluídas para `crm/buscas/` (só os campos úteis). A Central mostra esses arquivos em **Buscador de empresas › Buscas salvas** depois de "atualizar central".
- **Na Central:**
  - **Nova busca** monta o pedido para o Diretor (ou o comando de terminal) e tem links para o buscador local, que só funcionam neste computador.
  - **Importar planilha** lê qualquer CSV direto no navegador, sem enviar para lugar nenhum.
  - **Abrir uma busca** permite filtrar (só WhatsApp, nota mínima, esconder quem já está no funil), escolher o modelo de mensagem e o segmento, e **Adicionar à Prospecção**. Cada empresa entra como "A contatar", com WhatsApp (celular com DDD) e mensagem usando o nome, a nota e o número de avaliações.
- **Limites:** a Central publicada não consegue acessar o `localhost`. As buscas rodam no buscador local, pelo Diretor, pelo terminal ou pelo navegador. Faça uma busca por vez, com profundidade 5: muitas buscas seguidas podem bloquear seu IP no Google por algumas horas. Raspar o Maps vai contra os termos do Google e os dados são pessoais (LGPD): use para prospecção com moderação e sem revender.

## Estúdio criativo

É a seção exclusiva para criar imagens, carrosséis, motion designs, vídeos e anúncios.

- **Projetos:** quadro por status (Briefing → Em criação → Revisão → Aprovado → Entregue). Cada projeto tem:
  - briefing e direção visual (paleta, tipografia, estilo, o que evitar);
  - storyboard de quadros ou roteiro de cenas, com imagem em cada quadro;
  - referências (links e imagens), imagens e arquivos adicionais;
  - entregas e revisões.
  - O botão **Copiar briefing para o Diretor** gera o pedido completo para colar no chat.
- **Kits de marca:** cores (clique copia o hex), fontes com prévia, tom, elementos, logos e fotos de cada cliente.
- **Banco de referências:** links e imagens soltas, com tags e cliente, que podem ser enviadas para qualquer projeto.
- **Formatos e guias:** tamanhos mais usados e checklist de entrega.
- **Envio de arquivos:** arraste e solte, clique ou cole (Ctrl+V). Aceita PNG, JPG, WebP, GIF, SVG, MP4, WebM e PDF, até 20 MB (SVG até 2 MB). Os arquivos ficam guardados na própria Central publicada e não existem no arquivo local.
- **Sugestão com IA:** no storyboard, sugere quadros ou cenas a partir do briefing. Usa a sua conta Claude: a primeira vez pede autorização, e você revisa antes de aplicar.

Cada informação fica em um lugar só. O retorno de um lead, por exemplo, vem do pipeline e aparece sozinho no Planejamento e na Visão geral.

## Editar pela Central

Os botões **Editar**, **Novo**, **Registrar**, o status da prospecção, o checkbox de tarefa e o status de conteúdo salvam a mudança no banco de dados do próprio artifact:

- A mudança aparece na hora, no celular e no computador, e continua lá quando você volta.
- A mudança **ainda não está nos arquivos `.md`**. O rodapé do menu mostra quantas edições estão nessa situação.
- Se a página for aberta fora do claude.ai (o arquivo local), as edições ficam só naquele navegador. O rodapé avisa "Edições salvas só neste navegador".
- O botão **Copiar edições feitas aqui (JSON)** copia tudo o que foi alterado, como cópia de segurança.

## Consolidar e atualizar (com o Diretor Noxen)

Peça **"consolidar central"**. O diretor:
1. Lê as edições guardadas no banco da Central.
2. Grava cada uma no arquivo certo (carteira, leads, tarefas, ideias, scripts, financeiro, fichas).
3. Roda `py ferramentas/gerar_central.py` e republica a Central no mesmo link.
4. Apaga do banco as edições que já foram para os arquivos.

Peça **"atualizar central"** sempre que o diretor produzir algo novo, como um cliente, um roteiro, uma lista de prospecção ou um script. O diretor salva no arquivo certo, gera e republica.

## Como incluir coisas novas nos arquivos

- **Cliente:** "novo cliente <nome>" (copia `clientes/_modelo/` e adiciona uma linha na carteira).
- **Empresa para prospectar:** uma linha em `crm/leads.md`. A mensagem vai em `mensagens-prospeccao.json`, com o mesmo nome da coluna "Lead / Empresa".
- **Roteiro ou post de cliente:** um arquivo em `clientes/<cliente>/conteudos/` com cabeçalho (`titulo`, `formato`, `objetivo`, `status`, `canal`, `data`).
- **Material em outra pasta:** um bloco em `central/conteudo/conteudos.md` com `- arquivo: caminho`.
- **Script, ideia ou trecho da base:** um bloco "## Título" no arquivo correspondente.
- **Tarefa:** uma linha em `central/conteudo/tarefas.md`.

## Interfaces antigas

- `painel.html` continua sendo gerado por `ferramentas/gerar_painel.py`, mas a Central substitui o painel.
- A Central de Envio antiga (artifact `8vFxeq1o…`) e o `agencia/campanhas/central-envio.html` ficaram preservados. Os 6 envios marcados nela em 21/10 já foram registrados em `crm/leads.md` e aparecem na nova Prospecção. Use só a nova Central daqui em diante.

## Limites

- Não existe sincronização automática entre a Central e os arquivos `.md`: as edições só chegam aos arquivos quando você pede "consolidar central".
- Os links do WhatsApp abrem a conversa com o texto pronto, mas o envio é sempre feito por você.
- As imagens do carrossel aparecem em prévia reduzida. Os originais estão em Downloads.
