import os
import json
import dataclasses
from rich.console import Console
import langsmith
from langsmith import traceable

from creator_copilot.config import AppConfig
from creator_copilot.modules.perspective_discovery import discover_perspectives
from creator_copilot.modules.research_dialogue import run_research_dialogue
from creator_copilot.modules.script_generation import generate_draft_script, refine_script

console = Console()

class CreatorCopilotEngine:
    def __init__(self, config: AppConfig):
        self.config = config

    @traceable(name="CreatorCopilot Pipeline")
    def run(self, topic: str):
        run_tree = langsmith.get_current_run_tree()
        if run_tree:
            run_tree.metadata.update({
                "topic": topic,
                "content_type": self.config.pipeline.content_type,
                "num_perspectives": self.config.pipeline.num_perspectives,
                "num_dialogue_turns": self.config.pipeline.num_dialogue_turns,
                "dialogue_model": self.config.llm.dialogue_model,
                "script_model": self.config.llm.script_model,
            })
            
        console.rule(f"[bold green]Iniciando Creator Copilot: {topic}[/bold green]")
        
        # Cria diretório de saída
        safe_topic = topic.replace(" ", "_").replace("/", "_").lower()
        output_dir = os.path.join(self.config.output.dir, safe_topic)
        os.makedirs(output_dir, exist_ok=True)
        
        # Fase 1: Descobrir Perspectivas
        personas = discover_perspectives(topic, self.config)
        console.print(f"[green]✓ {len(personas)} personas geradas.[/green]")
        
        # Fase 2: Pesquisa Simulada (Diálogos)
        conversation_log = run_research_dialogue(topic, personas, self.config)
        
        # Salva log de conversa (Checkpoint 1)
        conv_log_path = os.path.join(output_dir, "conversation_log.json")
        with open(conv_log_path, "w", encoding="utf-8") as f:
            json.dump(dataclasses.asdict(conversation_log), f, ensure_ascii=False, indent=2)
        console.print(f"[green]✓ Logs de pesquisa salvos em {conv_log_path}[/green]")
            
        # Fase 3: Geração de Roteiro (Draft)
        draft_script = generate_draft_script(topic, self.config)
        
        # Salva o rascunho (Checkpoint 2)
        draft_path = os.path.join(output_dir, "draft_script.md")
        with open(draft_path, "w", encoding="utf-8") as f:
            f.write(draft_script)
            
        # Fase 3: Refinamento do Roteiro (Final)
        final_script = refine_script(topic, draft_script, conversation_log, self.config)
        
        # Salva o roteiro final (Markdown e JSON)
        final_path = os.path.join(output_dir, "final_script.md")
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(final_script)
            
        final_json_path = os.path.join(output_dir, "final_script.json")
        with open(final_json_path, "w", encoding="utf-8") as f:
            json.dump({
                "topic": topic,
                "script_markdown": final_script
            }, f, ensure_ascii=False, indent=2)
            
        console.rule("[bold green]Processo Concluído![/bold green]")
        console.print(f"Todos os artefatos foram salvos em: [bold]{output_dir}[/bold]")
        
        return final_script
