import os
import time
from typing import List
from tavily import TavilyClient
from rich.console import Console

from creator_copilot.config import SearchConfig
from creator_copilot.models import SearchResult

console = Console()

def search_web(queries: List[str], config: SearchConfig) -> List[SearchResult]:
    """
    Realiza buscas na web usando a API da Tavily para uma lista de queries,
    e retorna uma lista unificada de resultados estruturados.
    Evita URLs duplicadas.
    """
    api_key = os.environ.get(config.api_key_env)
    if not api_key:
        raise ValueError(f"Variável de ambiente '{config.api_key_env}' não encontrada no sistema ou no arquivo .env.")

    client = TavilyClient(api_key=api_key)
    
    collected_results = []
    seen_urls = set()

    for query in queries:
        try:
            # Usando a profundidade configurada (geralmente "basic" para economizar créditos)
            # O parâmetro max_results usa a configuração top_k
            response = client.search(
                query=query, 
                search_depth=config.search_depth,
                max_results=config.top_k
            )
            
            for result_data in response.get("results", []):
                url = result_data.get("url")
                if not url or url in seen_urls:
                    continue
                    
                title = result_data.get("title", "")
                snippet = result_data.get("content", "")
                
                # Como Tavily 'basic' normalmente traz apenas 'content', usamos ele como snippet e description
                description = snippet
                
                if title and snippet:
                    seen_urls.add(url)
                    collected_results.append(
                        SearchResult(
                            url=url,
                            title=title,
                            snippet=snippet,
                            description=description
                        )
                    )
        except Exception as e:
            console.print(f"[yellow]Erro ao buscar query '{query}' no Tavily: {e}[/yellow]")
            # Aguarda um momento antes da próxima query caso tenha ocorrido um rate limit simples
            time.sleep(2)
            
    return collected_results
