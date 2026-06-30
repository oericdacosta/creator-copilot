import os
import yaml
from dataclasses import dataclass
from typing import Literal
from dotenv import load_dotenv

# Carrega o .env automaticamente
load_dotenv()

@dataclass
class LLMConfig:
    api_key_env: str
    dialogue_model: str
    script_model: str
    temperature: float
    top_p: float
    max_tokens_dialogue: int
    max_tokens_script: int
    max_retries: int
    base_delay: int

@dataclass
class SearchConfig:
    api_key_env: str
    engine: str
    search_depth: str
    top_k: int
    max_queries_per_turn: int
    region: str
    safe_search: str

@dataclass
class PipelineConfig:
    num_perspectives: int
    num_dialogue_turns: int
    content_type: str
    language: str

@dataclass
class OutputConfig:
    dir: str
    save_conversation_log: bool
    save_search_results: bool
    format: str

@dataclass
class LangSmithConfig:
    enabled: bool
    project_name: str

@dataclass
class AppConfig:
    llm: LLMConfig
    search: SearchConfig
    pipeline: PipelineConfig
    output: OutputConfig
    langsmith: LangSmithConfig

def load_config(config_path: str = "config.yaml") -> AppConfig:
    """Carrega o arquivo de configuração e retorna uma dataclass tipada."""
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {config_path}")
        
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        
    return AppConfig(
        llm=LLMConfig(**data.get("llm", {})),
        search=SearchConfig(**data.get("search", {})),
        pipeline=PipelineConfig(**data.get("pipeline", {})),
        output=OutputConfig(**data.get("output", {})),
        langsmith=LangSmithConfig(**data.get("langsmith", {"enabled": False, "project_name": "default"}))
    )
