from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class SearchResult:
    url: str
    title: str
    snippet: str
    description: str

@dataclass
class DialogueTurn:
    """Um turno do diálogo entrevistador-especialista."""
    persona: str
    question: str
    search_queries: List[str]
    search_results: List[SearchResult]
    answer: str
    
    def to_dict(self):
        return {
            "persona": self.persona,
            "question": self.question,
            "search_queries": self.search_queries,
            "search_results": [
                {
                    "url": r.url,
                    "title": r.title,
                    "snippet": r.snippet,
                    "description": r.description
                } for r in self.search_results
            ],
            "answer": self.answer
        }

@dataclass
class ConversationLog:
    """Todas as conversas de todas as personas."""
    topic: str
    perspectives: List[str]
    dialogues: Dict[str, List[DialogueTurn]] = field(default_factory=dict)
    
    def to_dict(self):
        return {
            "topic": self.topic,
            "perspectives": self.perspectives,
            "dialogues": {
                persona: [turn.to_dict() for turn in turns]
                for persona, turns in self.dialogues.items()
            }
        }

@dataclass
class ScriptSection:
    title: str
    talking_points: List[str] = field(default_factory=list)
    curiosities: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    subsections: List['ScriptSection'] = field(default_factory=list)

@dataclass
class ScriptOutline:
    """Roteiro estruturado para vídeo/podcast."""
    topic: str
    content_type: str
    sections: List[ScriptSection] = field(default_factory=list)
