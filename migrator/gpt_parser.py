"""Parse a ChatGPT GPT export JSON into a structured GPTConfig."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class GPTConfig:
    name: str
    description: str
    instructions: str
    conversation_starters: list[str]
    knowledge_files: list[dict[str, Any]]
    openapi_spec: str | None  # Raw YAML or JSON string from actions.spec


def load(path: str | Path) -> GPTConfig:
    """Load and validate a GPT export JSON file."""
    text = Path(path).read_text(encoding="utf-8")
    data = json.loads(text)

    name = str(data.get("name", "Unnamed GPT")).strip()
    description = str(data.get("description", "")).strip()
    instructions = str(data.get("instructions", "")).strip()
    if not instructions:
        raise ValueError("GPT config must contain non-empty 'instructions'")

    starters = [str(s) for s in data.get("conversation_starters", [])]
    knowledge_files = list(data.get("knowledge_files", []))

    actions = data.get("actions") or {}
    openapi_spec: str | None = None
    if actions:
        spec = actions.get("spec")
        if spec:
            openapi_spec = str(spec).strip()

    return GPTConfig(
        name=name,
        description=description,
        instructions=instructions,
        conversation_starters=starters,
        knowledge_files=knowledge_files,
        openapi_spec=openapi_spec,
    )
