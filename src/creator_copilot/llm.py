import os
import time
from typing import Optional
from openai import OpenAI
from openai import RateLimitError, APIError, APIConnectionError
from rich.console import Console

from creator_copilot.config import LLMConfig

from langsmith.wrappers import wrap_openai

console = Console()

def call_llm(
    prompt: str,
    config: LLMConfig,
    is_script: bool = False,
    system_prompt: Optional[str] = None
) -> str:
    """
    Realiza uma chamada para a API da OpenAI com retry exponencial e logging de tokens.
    """
    api_key = os.environ.get(config.api_key_env)
    if not api_key:
        raise ValueError(f"Variável de ambiente '{config.api_key_env}' não encontrada no sistema ou no arquivo .env.")

    client = OpenAI(api_key=api_key)
    
    # Ativa o tracking automático do LangSmith apenas se a chave e o tracing estiverem configurados
    if os.environ.get("LANGSMITH_API_KEY") and os.environ.get("LANGSMITH_TRACING", "").lower() == "true":
        client = wrap_openai(client)
    
    model = config.script_model if is_script else config.dialogue_model
    max_tokens = config.max_tokens_script if is_script else config.max_tokens_dialogue
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    max_retries = config.max_retries
    base_delay = config.base_delay

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=config.temperature,
                max_tokens=max_tokens,
                top_p=config.top_p
            )
            
              
            content = response.choices[0].message.content
            return content if content is not None else ""
            
        except RateLimitError as e:
            if attempt == max_retries - 1:
                console.print(f"[red]Falha ao chamar LLM após {max_retries} tentativas: Rate Limit.[/red]")
                raise e
            delay = base_delay * (2 ** attempt)
            console.print(f"[yellow]Rate limit atingido. Tentando novamente em {delay} segundos...[/yellow]")
            time.sleep(delay)
            
        except (APIError, APIConnectionError) as e:
            if attempt == max_retries - 1:
                console.print(f"[red]Falha ao chamar LLM após {max_retries} tentativas: Erro de API.[/red]")
                raise e
            delay = base_delay * (2 ** attempt)
            console.print(f"[yellow]Erro na API ({type(e).__name__}). Tentando novamente em {delay} segundos...[/yellow]")
            time.sleep(delay)
        except Exception as e:
            console.print(f"[red]Erro inesperado ao chamar LLM: {e}[/red]")
            raise e
