import json
from typing import Dict, Any
from rich.console import Console
from langsmith import traceable

from creator_copilot.config import AppConfig
from creator_copilot.models import ConversationLog
from creator_copilot.llm import call_llm
from creator_copilot.prompts import GENERATE_DRAFT_SCRIPT, REFINE_SCRIPT
from creator_copilot.text_processing import condense_conversation_log, extract_all_urls

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
    
    # Prepara o histórico da conversa formatado (agora apenas com fatos, sem as perguntas e URLs repetidas)
    conv_text = condense_conversation_log(conversation_log)
    
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
    
    final_script = final_script.strip()
    
    # Extrai as fontes únicas e anexa ao final de forma determinística
    sources = extract_all_urls(conversation_log)
    if sources:
        sources_text = "\n\n## 📚 Fontes Consultadas\n"
        sources_text += "\n".join([f"- [{s['title']}]({s['url']})" for s in sources])
        final_script += sources_text
        
    return final_script
