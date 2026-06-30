import argparse
import sys
from rich.console import Console

from creator_copilot.config import load_config
from creator_copilot.engine import CreatorCopilotEngine

console = Console()

def main():
    parser = argparse.ArgumentParser(description="Creator Copilot - Assistente de Roteiros Baseado em Pesquisa (Estilo STORM)")
    parser.add_argument("topic", type=str, help="O tema do roteiro que você deseja criar (ex: 'A História da Inteligência Artificial')")
    
    args = parser.parse_args()
    
    try:
        config = load_config()
    except Exception as e:
        console.print(f"[red]Erro ao carregar configurações: {e}[/red]")
        sys.exit(1)
        
    engine = CreatorCopilotEngine(config)
    
    try:
        engine.run(args.topic)
    except KeyboardInterrupt:
        console.print("\n[yellow]Execução cancelada pelo usuário.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Erro inesperado durante a execução: {e}[/red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
