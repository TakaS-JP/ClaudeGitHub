"""Generate a Claude.ai Project setup guide from a GPTConfig."""
from __future__ import annotations

import json
from pathlib import Path

from migrator.gpt_parser import GPTConfig

_CHATGPT_PHRASES = [
    "As a GPT",
    "as a GPT",
    "You are a GPT",
    "you are a GPT",
    "ChatGPT",
    "chatgpt",
    "OpenAI",
    "openai",
]


def _adapt_instructions(instructions: str) -> str:
    """Replace ChatGPT-specific phrasing so the prompt suits Claude."""
    result = instructions
    replacements = {
        "As a GPT": "As an AI assistant",
        "as a GPT": "as an AI assistant",
        "You are a GPT": "You are an AI assistant",
        "you are a GPT": "you are an AI assistant",
        "ChatGPT": "Claude",
        "chatgpt": "Claude",
        "OpenAI": "Anthropic",
        "openai": "Anthropic",
    }
    for old, new in replacements.items():
        result = result.replace(old, new)
    return result


def _mcp_config_snippet(project_name: str) -> str:
    safe_name = project_name.lower().replace(" ", "-")
    return json.dumps(
        {
            "mcpServers": {
                safe_name: {
                    "command": "python",
                    "args": ["mcp_server/server.py"],
                }
            }
        },
        indent=2,
        ensure_ascii=False,
    )


def generate(config: GPTConfig, output_dir: Path, has_mcp: bool) -> None:
    """Write *claude_project_setup.md* into *output_dir*."""
    output_dir.mkdir(parents=True, exist_ok=True)

    adapted_instructions = _adapt_instructions(config.instructions)

    sections: list[str] = []

    # Title
    sections.append(f"# Claude.ai Project Setup — {config.name}\n")
    if config.description:
        sections.append(f"> {config.description}\n")

    # Step 1 — Create project
    sections.append("## Step 1: Create a New Project on Claude.ai\n")
    sections.append(
        "1. Open [claude.ai](https://claude.ai) and sign in (Pro or Team plan required).\n"
        "2. Click **Projects** in the left sidebar → **New project**.\n"
        f'3. Name the project **{config.name}**.\n'
    )

    # Step 2 — Set custom instructions
    sections.append("## Step 2: Set Custom Instructions (System Prompt)\n")
    sections.append(
        "1. Open the project settings and find **Custom instructions**.\n"
        "2. Paste the following prompt:\n"
    )
    sections.append(f"```\n{adapted_instructions}\n```\n")

    # Step 3 — Knowledge files
    if config.knowledge_files:
        sections.append("## Step 3: Upload Knowledge Files\n")
        sections.append(
            "1. In the project settings click **Add content** → **Upload files**.\n"
            "2. Upload the following files:\n"
        )
        for kf in config.knowledge_files:
            name = kf.get("name", str(kf))
            sections.append(f"   - `{name}`\n")
        sections.append(
            "\n> Claude will use these files as project knowledge automatically in every conversation.\n"
        )
    else:
        sections.append("## Step 3: Knowledge Files\n")
        sections.append("No knowledge files were defined in this GPT.\n")

    # Step 4 — MCP / Custom actions
    if has_mcp:
        sections.append("## Step 4: Connect Custom Actions via MCP\n")
        sections.append(
            "Your GPT's custom actions have been converted to a **FastMCP server** "
            "located in `mcp_server/server.py`.\n\n"
            "### Install MCP server dependencies\n"
            "```bash\n"
            "pip install -r mcp_server/requirements.txt\n"
            "```\n\n"
            "### Connect to Claude Desktop (claude.ai desktop app)\n"
            "Add the following to your `claude_desktop_config.json` "
            "(usually at `~/.config/claude/claude_desktop_config.json` on Linux/Mac "
            "or `%APPDATA%\\Claude\\claude_desktop_config.json` on Windows):\n\n"
            f"```json\n{_mcp_config_snippet(config.name)}\n```\n\n"
            "Restart Claude Desktop after saving the config.\n\n"
            "> **Note:** MCP server support for the claude.ai web app is available for "
            "Team/Enterprise plans. For individual Pro accounts use the Claude Desktop app.\n"
        )
    else:
        sections.append("## Step 4: Custom Actions\n")
        sections.append("No custom actions (OpenAPI spec) were found in this GPT.\n")

    # Step 5 — Built-in capabilities
    sections.append("## Step 5: Built-in Capabilities (Web Search & Code Execution)\n")
    sections.append(
        "Claude.ai Pro/Team includes the following capabilities that replace "
        "ChatGPT's built-in tools — no extra setup needed:\n\n"
        "| ChatGPT feature | Claude.ai equivalent |\n"
        "|---|---|\n"
        "| Web browsing | Web search (enabled per conversation) |\n"
        "| Code interpreter | Analysis tool (runs Python in-browser) |\n"
        "| DALL-E image generation | Not available — use a separate image tool |\n"
        "\nTo enable web search in a conversation click the **Search** icon in the message box.\n"
    )

    # Conversation starters
    if config.conversation_starters:
        sections.append("## Conversation Starters\n")
        sections.append(
            "You can pin these as starter messages in the project description:\n\n"
        )
        for s in config.conversation_starters:
            sections.append(f"- {s}\n")

    doc = "\n".join(sections)
    out_path = output_dir / "claude_project_setup.md"
    out_path.write_text(doc, encoding="utf-8")
