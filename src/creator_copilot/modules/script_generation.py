import json
from typing import Dict, Any
from rich.console import Console
from langsmith import traceable

from creator_copilot.config import AppConfig
from creator_copilot.models import ConversationLog
from creator_copilot.llm import call_llm
from creator_copilot.prompts import GENERATE_DRAFT_SCRIPT, REFINE_SCRIPT

console = Console()

@traceable(name="Fase 3: Draft")
def generate_draft_script(topic: str, config: AppConfig) -> str:
    """
    Passo 1 da Geração: Cria o esboço preliminar sem usar dados da pesquisa,
    apenas com o conhecimento paramétrico (interno) do modelo.
    """
    console.print(f"\n[bold blue]Fase 3: Gerando esboço preliminar do roteiro para '{topic}'...[/bold blue]")
    
    prompt = GENERATE_DRAFT_SCRIPT.format(
        topic=topic,
        content_type=config.pipeline.content_type
    )
    
    # Usa o modelo de script (mais robusto, com mais contexto, ex: gpt-4o)
    draft_outline = call_llm(
        prompt=prompt,
        config=config.llm,
        is_script=True,
        system_prompt="Você é um experiente roteirista de conteúdo digital."
    )
    
    return draft_outline.strip()

@traceable(name="Fase 3: Refinamento")
def refine_script(topic: str, draft_outline: str, conversation_log: ConversationLog, config: AppConfig) -> str:
    """
    Passo 2 da Geração: Usa o rico histórico de pesquisas da Fase 2 para 
    enriquecer, refinar e expandir o roteiro preliminar.
    """
    console.print(f"[bold blue]Fase 3: Refinando o roteiro com os dados da pesquisa...[/bold blue]")
    
    # Prepara o histórico da conversa formatado
    conv_text = _format_conversation_log(conversation_log)
    
    prompt = REFINE_SCRIPT.format(
        topic=topic,
        content_type=config.pipeline.content_type,
        draft_outline=draft_outline,
        conversation_log=conv_text
    )
    
    final_script = call_llm(
        prompt=prompt,
        config=config.llm,
        is_script=True,
        system_prompt="Você é um roteirista chefe que exige precisão e riqueza de detalhes nos roteiros."
    )
    
    return final_script.strip()

def _format_conversation_log(conversation_log: ConversationLog) -> str:
    """
    Formata o histórico inteiro de diálogos num texto único para o LLM processar.
    Limita o tamanho para evitar estourar o limite de tokens (inspirado no limit_word_count_preserve_newline do STORM).
    """
    formatted = []
    for persona, turns in conversation_log.dialogues.items():
        if not turns:
            continue
        formatted.append(f"--- Pesquisa com a perspectiva: {persona} ---")
        for turn in turns:
            formatted.append(f"Entrevistador: {turn.question}")
            formatted.append(f"Especialista: {turn.answer}")
            if turn.search_results:
                # Extrai as URLs e títulos para referenciar
                refs = [f"[{res.title}]({res.url})" for res in turn.search_results]
                formatted.append(f"Fontes Utilizadas: {', '.join(refs)}\n")
            else:
                formatted.append("\n")
            
    full_text = "\n".join(formatted)
    
    # Controle básico de limite de palavras (aproximadamente 5000 palavras, 
    # o que dá ~6000-7000 tokens dependendo do idioma).
    words = full_text.split()
    if len(words) > 5000:
        return " ".join(words[:5000]) + "\n\n... (histórico truncado devido ao tamanho)"
        
    return full_text
