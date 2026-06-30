import re
import asyncio
from typing import List
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from langsmith import traceable

from creator_copilot.config import AppConfig
from creator_copilot.models import ConversationLog, DialogueTurn, SearchResult
from creator_copilot.llm import call_llm_async
from creator_copilot.search import search_web_async
from creator_copilot.prompts import ASK_QUESTION, ANSWER_FROM_SOURCES
from creator_copilot.text_processing import generate_search_queries_deterministic

console = Console()

async def _run_persona_dialogue(topic: str, persona: str, config: AppConfig, progress: Progress, task_id, semaphore: asyncio.Semaphore) -> List[DialogueTurn]:
    async with semaphore:
        history_turns: List[DialogueTurn] = []
        
        for turn_idx in range(config.pipeline.num_dialogue_turns):
            progress.update(task_id, description=f"[bold green]{persona}[/bold green] - Turno {turn_idx + 1}/{config.pipeline.num_dialogue_turns} (Gerando pergunta...)")
            
            # 1. Gerar Pergunta (Entrevistador)
            history_text = _format_history(history_turns) if history_turns else "Nenhum histórico ainda. Esta é a primeira pergunta."
            
            question_prompt = ASK_QUESTION.format(
                persona=persona,
                topic=topic,
                history=history_text
            )
            
            question = await call_llm_async(
                prompt=question_prompt,
                config=config.llm,
                is_script=False,
                system_prompt="Você é um excelente entrevistador investigativo."
            )
            question = question.strip()
            
            if not question or question.lower().startswith("obrigado"):
                break
                
            # 2. Gerar Termos de Busca (Queries) - via código determinístico
            progress.update(task_id, description=f"[bold green]{persona}[/bold green] - Turno {turn_idx + 1}/{config.pipeline.num_dialogue_turns} (Gerando termos de busca...)")
            queries = generate_search_queries_deterministic(
                question=question,
                topic=topic,
                max_queries=config.search.max_queries_per_turn
            )
            
            # 3. Buscar na Web
            progress.update(task_id, description=f"[bold green]{persona}[/bold green] - Turno {turn_idx + 1}/{config.pipeline.num_dialogue_turns} (Buscando na web...)")
            search_results = await search_web_async(queries, config.search)
            
            # 4. Responder com base nas fontes
            progress.update(task_id, description=f"[bold green]{persona}[/bold green] - Turno {turn_idx + 1}/{config.pipeline.num_dialogue_turns} (Sintetizando resposta...)")
            
            if search_results:
                sources_text = _format_sources(search_results)
                answer_prompt = ANSWER_FROM_SOURCES.format(
                    topic=topic,
                    question=question,
                    sources=sources_text
                )
                
                try:
                    answer = await call_llm_async(
                        prompt=answer_prompt,
                        config=config.llm,
                        is_script=False,
                        system_prompt="Você é um especialista que responde perguntas de forma direta, usando estritamente as fontes fornecidas."
                    )
                except Exception as e:
                    answer = f"Desculpe, não consegui formular a resposta devido a um erro: {e}"
            else:
                answer = "Desculpe, não consegui encontrar informações confiáveis na internet sobre esta pergunta."
            
            # Registra o turno
            turn = DialogueTurn(
                persona=persona,
                question=question,
                search_queries=queries,
                search_results=search_results,
                answer=answer
            )
            history_turns.append(turn)
            
            progress.advance(task_id)
            
        return history_turns

@traceable(name="Fase 2: Diálogo de Pesquisa")
async def run_research_dialogue(topic: str, personas: List[str], config: AppConfig) -> ConversationLog:
    """
    Executa o diálogo de pesquisa simulado para cada persona em paralelo.
    O Entrevistador (Persona) faz perguntas, e o Especialista busca na web e responde.
    """
    console.print(f"\n[bold blue]Fase 2: Iniciando diálogo de pesquisa para '{topic}'[/bold blue]")
    
    conversation_log = ConversationLog(topic=topic, perspectives=personas)
    max_concurrency = getattr(config.pipeline, "max_concurrency", 4)
    semaphore = asyncio.Semaphore(max_concurrency)
    
    # Execução em paralelo
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        
        tasks = []
        for persona in personas:
            task_id = progress.add_task(f"Pesquisando com a persona: [bold green]{persona}[/bold green]...", total=config.pipeline.num_dialogue_turns)
            tasks.append(
                _run_persona_dialogue(topic, persona, config, progress, task_id, semaphore)
            )
            
        results = await asyncio.gather(*tasks)
        
        for persona, history in zip(personas, results):
            conversation_log.dialogues[persona] = history
            
    console.print(f"[green]✓ Diálogo de pesquisa concluído para {len(personas)} personas.[/green]")
    return conversation_log

def _format_history(history: List[DialogueTurn]) -> str:
    formatted = []
    for turn in history:
        formatted.append(f"Q: {turn.question}")
        formatted.append(f"A: {turn.answer}\n")
    return "\n".join(formatted)

def _format_sources(results: List[SearchResult]) -> str:
    formatted = []
    for i, res in enumerate(results):
        formatted.append(f"Fonte [{i+1}]: {res.title}")
        formatted.append(f"Snippet: {res.snippet}\n")
    # Limita o tamanho para evitar estourar o contexto (inspirado no limit_word_count_preserve_newline)
    full_text = "\n".join(formatted)
    words = full_text.split()
    if len(words) > 1000:
        return " ".join(words[:1000]) + "..."
    return full_text
