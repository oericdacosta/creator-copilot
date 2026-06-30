import string
from typing import List

import nltk
from nltk.corpus import stopwords

from creator_copilot.models import ConversationLog

# Baixa as stopwords caso não existam localmente
nltk.download('stopwords', quiet=True)
PT_STOPWORDS = set(stopwords.words('portuguese'))

def limit_word_count_preserve_newline(input_string: str, max_word_count: int) -> str:
    """Limita o texto a max_word_count preservando as linhas completas."""
    word_count = 0
    limited_string = ""
    for line in input_string.split('\n'):
        line_words = line.split()
        for lw in line_words:
            if word_count < max_word_count:
                limited_string += lw + " "
                word_count += 1
            else:
                break
        if word_count >= max_word_count:
            break
        limited_string = limited_string.strip() + "\n"
    return limited_string.strip()

def condense_conversation_log(conversation_log: ConversationLog, max_words: int = 5000) -> str:
    """Condensa o log de conversa focando apenas nos fatos descobertos, removendo perguntas e URLs."""
    formatted = []
    # Usamos um set para evitar adicionar a mesmíssima resposta duas vezes
    seen_answers = set()
    
    for persona, turns in conversation_log.dialogues.items():
        if not turns:
            continue
            
        formatted.append(f"--- Fatos descobertos pela perspectiva: {persona} ---")
        for turn in turns:
            ans = turn.answer.strip()
            # Ignora respostas genéricas de erro/vazias
            if not ans or "desculpe" in ans.lower() or "não consegui" in ans.lower():
                continue
                
            if ans not in seen_answers:
                formatted.append(f"- {ans}")
                seen_answers.add(ans)
        formatted.append("\n")
        
    full_text = "\n".join(formatted)
    return limit_word_count_preserve_newline(full_text, max_words)

def extract_all_urls(conversation_log: ConversationLog) -> List[dict]:
    """Extrai uma lista única de fontes (título e URL) usadas na pesquisa para deduplicação."""
    sources = {}
    for turns in conversation_log.dialogues.values():
        for turn in turns:
            if turn.search_results:
                for res in turn.search_results:
                    if res.url not in sources:
                        sources[res.url] = res.title
                        
    return [{"title": title, "url": url} for url, title in sources.items()]

def extract_keywords(text: str) -> str:
    """Extrai palavras-chave de um texto removendo pontuação e stopwords."""
    # Remove pontuação
    translator = str.maketrans('', '', string.punctuation)
    clean_text = text.translate(translator).lower()
    
    # Divide em palavras e remove stopwords
    words = clean_text.split()
    keywords = [word for word in words if word not in PT_STOPWORDS and len(word) > 2]
    
    return " ".join(keywords)

def generate_search_queries_deterministic(question: str, topic: str, max_queries: int) -> List[str]:
    """Gera queries de busca de forma determinística, sem usar LLM."""
    queries = []
    
    # 1. A própria pergunta geralmente é uma boa query (como o STORM faz)
    clean_question = question.strip()
    if clean_question:
        queries.append(clean_question)
        
    # 2. Combinação do Tópico + Palavras-chave da Pergunta
    keywords = extract_keywords(clean_question)
    if keywords:
        query2 = f"{topic} {keywords}".strip()
        # Evita duplicatas exatas
        if query2.lower() != clean_question.lower():
            queries.append(query2)
            
    # 3. Apenas o tópico (como query genérica de fallback, se max_queries > 2)
    if len(queries) < max_queries:
        if topic.lower() not in [q.lower() for q in queries]:
            queries.append(topic)
            
    return queries[:max_queries]
