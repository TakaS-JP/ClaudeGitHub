# Claude.ai Project Setup — Task Manager GPT

> A helpful assistant for managing tasks and to-do lists.

## Step 1: Create a New Project on Claude.ai

1. Open [claude.ai](https://claude.ai) and sign in (Pro or Team plan required).
2. Click **Projects** in the left sidebar → **New project**.
3. Name the project **Task Manager GPT**.

## Step 2: Set Custom Instructions (System Prompt)

1. Open the project settings and find **Custom instructions**.
2. Paste the following prompt:

```
You are an AI assistant specialized in task management. Help users create, update, and organize their tasks. Always be concise and actionable. When listing tasks, use a numbered list. As an AI assistant you should prioritize clarity and brevity.
```

## Step 3: Upload Knowledge Files

1. In the project settings click **Add content** → **Upload files**.
2. Upload the following files:

   - `task_guidelines.pdf`

   - `productivity_tips.txt`


> Claude will use these files as project knowledge automatically in every conversation.

## Step 4: Connect Custom Actions via MCP

Your GPT's custom actions have been converted to a **FastMCP server** located in `mcp_server/server.py`.

### Install MCP server dependencies
```bash
pip install -r mcp_server/requirements.txt
```

### Connect to Claude Desktop (claude.ai desktop app)
Add the following to your `claude_desktop_config.json` (usually at `~/.config/claude/claude_desktop_config.json` on Linux/Mac or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "task-manager-gpt": {
      "command": "python",
      "args": [
        "mcp_server/server.py"
      ]
    }
  }
}
```

Restart Claude Desktop after saving the config.

> **Note:** MCP server support for the claude.ai web app is available for Team/Enterprise plans. For individual Pro accounts use the Claude Desktop app.

## Step 5: Built-in Capabilities (Web Search & Code Execution)

Claude.ai Pro/Team includes the following capabilities that replace ChatGPT's built-in tools — no extra setup needed:

| ChatGPT feature | Claude.ai equivalent |
|---|---|
| Web browsing | Web search (enabled per conversation) |
| Code interpreter | Analysis tool (runs Python in-browser) |
| DALL-E image generation | Not available — use a separate image tool |

To enable web search in a conversation click the **Search** icon in the message box.

## Conversation Starters

You can pin these as starter messages in the project description:


- Show me all my open tasks

- Add a new task for today

- What tasks are due this week?
