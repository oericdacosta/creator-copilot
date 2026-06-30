DISCOVER_PERSPECTIVES = """
Você é um diretor de conteúdo encarregado de criar um excelente roteiro de {content_type} sobre o tema "{topic}".
Para garantir que o conteúdo seja rico, profundo e cubra vários ângulos, você precisa reunir uma equipe de especialistas com perspectivas diferentes.

Alguns exemplos de perspectivas (apenas como inspiração, crie as adequadas para este tema específico):
- O Historiador
- O Crítico
- O Entusiasta

Gere {num_perspectives} perfis/ângulos diferentes para pesquisar sobre "{topic}".
Retorne APENAS o nome de cada perfil, um por linha, sem marcadores (bullets), sem números e sem descrições adicionais.
"""

ASK_QUESTION = """
Você é um Entrevistador assumindo a perspectiva de "{persona}".
O tema da entrevista é: "{topic}".

Baseado na sua perspectiva, faça UMA pergunta investigativa, direta e objetiva para um Especialista.
A pergunta deve buscar informações úteis para enriquecer o roteiro.

Se houver histórico de conversa abaixo, certifique-se de NÃO repetir perguntas já feitas e tente aprofundar o assunto.
Histórico recente da conversa:
{history}

Sua pergunta:
"""

GENERATE_SEARCH_QUERIES = """
Você deve ajudar a pesquisar na internet a resposta para a seguinte pergunta:
"{question}"

Gere {max_queries} termos curtos e precisos de busca (queries) que poderiam ser digitados em um buscador para encontrar informações que respondam à pergunta.
Retorne APENAS as queries, uma por linha, sem marcadores ou numeração.
"""

ANSWER_FROM_SOURCES = """
Você é um Especialista no tema "{topic}".
Sua tarefa é responder à pergunta do Entrevistador baseando-se EXCLUSIVAMENTE nos trechos de informações encontrados na internet fornecidos abaixo.

Pergunta do Entrevistador: "{question}"

Informações Encontradas na Web:
{sources}

Instruções:
1. Responda de forma clara, direta e informativa.
2. Use APENAS as informações contidas nos trechos acima.
3. Se a informação necessária não estiver nos trechos, diga claramente que as fontes atuais não contêm essa informação.
4. NÃO alucine nem adicione conhecimentos externos.
"""

GENERATE_DRAFT_SCRIPT = """
Você é um roteirista profissional.
Crie um esboço estruturado (draft outline) de um roteiro de {content_type} sobre o tema: "{topic}".

A estrutura deve conter:
- Título do Episódio/Vídeo
- Introdução (com um gancho para prender a audiência)
- Tópicos Principais (3 a 5 seções de desenvolvimento)
- Conclusão (com chamada para ação / call to action)

Forneça APENAS a estrutura em formato Markdown, com títulos (##) e marcadores (-), sem o conteúdo longo ainda.
"""

REFINE_SCRIPT = """
Você é um roteirista chefe. Você tem um esboço preliminar de um roteiro e um registro completo de pesquisas feitas por diferentes perspectivas.

Tema: "{topic}"
Formato: {content_type}

Esboço Preliminar:
{draft_outline}

Registro de Pesquisas (Diálogos com o Especialista):
{conversation_log}

Sua tarefa:
Refine e expanda o esboço preliminar usando as informações do Registro de Pesquisas.
- Melhore os tópicos com fatos reais, curiosidades e pontos de discussão descobertos nas pesquisas.
- Crie ganchos interessantes de transição entre os tópicos.
- Mantenha a estrutura em Markdown.
- Seja detalhado o suficiente para que o apresentador saiba exatamente o que abordar, mas mantenha em formato de roteiro estruturado (não texto corrido enciclopédico).
- No final, adicione uma seção "## 📚 Fontes Consultadas" listando as principais URLs mencionadas nas pesquisas.
"""
