import re
from typing import List
from rich.console import Console
from langsmith import traceable

from creator_copilot.config import AppConfig
from creator_copilot.llm import call_llm
from creator_copilot.prompts import DISCOVER_PERSPECTIVES

console = Console()

@traceable(name="Fase 1: Descoberta de Perspectivas")
def discover_perspectives(topic: str, config: AppConfig) -> List[str]:
    """
    Descobre diferentes ângulos de pesquisa (personas) para o tema usando o LLM.
    Sempre adiciona uma persona padrão ("Pesquisador de fatos gerais").
    """
    console.print(f"[bold blue]Fase 1: Descobrindo perspectivas para o tema[/bold blue] '{topic}'")
    
    prompt = DISCOVER_PERSPECTIVES.format(
        topic=topic,
        content_type=config.pipeline.content_type,
        num_perspectives=config.pipeline.num_perspectives
    )
    
    # Chama o LLM (gpt-4o-mini por padrão, pois is_script=False)
    response = call_llm(
        prompt=prompt,
        config=config.llm,
        is_script=False,
        system_prompt="Você é um experiente diretor de conteúdo buscando ângulos criativos e investigativos."
    )
    
    # Processa a resposta
    lines = [line.strip() for line in response.split('\n') if line.strip()]
    
    # Limpa possíveis números ou bullets indesejados (caso o modelo não obedeça 100%)
    cleaned_personas = []
    for line in lines:
        # Remove números, pontos, hífens ou asteriscos no começo da linha
        clean_line = re.sub(r'^[\d\.\-\*\s]+', '', line).strip()
        if clean_line:
            cleaned_personas.append(clean_line)
            
    # Garante que não passamos do número pedido (o LLM as vezes gera a mais)
    cleaned_personas = cleaned_personas[:config.pipeline.num_perspectives]
    
    # Adiciona a persona base obrigatória (inspirado no STORM's Basic fact writer)
    base_persona = "Pesquisador de fatos gerais e contexto histórico"
    
    final_personas = [base_persona] + cleaned_personas
    
    return final_personas
