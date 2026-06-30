# Creator Copilot 🎙️

O **Creator Copilot** é um assistente de linha de comando (CLI) construído em Python, focado na geração automatizada de roteiros investigativos e altamente estruturados para criadores de conteúdo (Podcasts, YouTube, Artigos).

Inspirado pelo paper e projeto **STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Answering)** de Stanford, esta ferramenta simula uma equipe de pesquisadores virtuais. Ela adota diferentes perspectivas e conduz um diálogo investigativo pesquisando fatos na internet antes de escrever o roteiro, minimizando severamente alucinações de LLMs.

## 🚀 Como Funciona a Magia?

O sistema roda em três fases automáticas:
1. **Fase 1 (Descobrindo Perspectivas):** Você informa um tema e o LLM age como um "Diretor de Conteúdo", levantando N perfis únicos (Ex: *O Cético, O Historiador, O Pioneiro Tecnológico*).
2. **Fase 2 (Diálogo de Pesquisa):** O LLM simula uma entrevista. Cada persona faz perguntas desafiadoras, o sistema busca respostas no Google (via Tavily API), lê os snippets e o Especialista responde baseando-se **apenas** nas fontes.
3. **Fase 3 (Geração e Refinamento do Roteiro):** A Inteligência desenha uma estrutura preliminar de roteiro, depois pega todo o gigantesco log de conversas da Fase 2 e enriquece o roteiro com fatos, ganchos e as fontes de pesquisa originais!

## ⚙️ Instalação e Configuração

### 1. Pré-requisitos
- [uv](https://github.com/astral-sh/uv) (O gerenciador de pacotes ultra-rápido)
- Python 3.11+
- Chave da API da OpenAI (`OPENAI_API_KEY`)
- Chave da API do Tavily (`TAVILY_API_KEY`)

### 2. Preparando o ambiente
Clone o repositório, abra a pasta e crie seu arquivo de ambiente:
```bash
cp .env.example .env
```
Abra o `.env` gerado e coloque suas chaves.

## 🕹️ Como Usar

Com o seu `.env` configurado, basta chamar o comando `creator-copilot` pelo `uv run` seguido do tema que você deseja. Dica: coloque o tema entre aspas!

```bash
uv run creator-copilot "A Origem do Xadrez"
uv run creator-copilot "A História da Inteligência Artificial"
uv run creator-copilot "Por que dormimos?"
```

O processo pode levar alguns minutos (ele estará lendo dezenas de páginas da web).
No final, todos os arquivos serão salvos magicamente dentro da pasta `output/<seu_tema>/`:
- `conversation_log.json`: Todos os diálogos e fontes extraídas da web.
- `draft_script.md`: A espinha dorsal gerada sem pesquisa.
- `final_script.md`: **O seu roteiro pronto para gravar.**

## 🔧 Personalização

Você tem total controle sobre a máquina! Abra o arquivo `config.yaml` na raiz do projeto e brinque com os valores:
- `num_perspectives`: Quer um vídeo mais profundo? Aumente para 5 ou mais.
- `num_dialogue_turns`: Define a profundidade das entrevistas. 
- `content_type`: Mude de "Podcast/YouTube" para "Artigo Acadêmico" ou "Documentário Curto".
- `search_depth`: Use "basic" para economizar, ou "advanced" para extrair páginas inteiras via IA!
