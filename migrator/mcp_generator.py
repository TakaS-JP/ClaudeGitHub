"""Generate a FastMCP server from an OpenAPI 3.x spec string."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml


def _safe_identifier(text: str) -> str:
    """Convert arbitrary text to a valid Python identifier."""
    result = re.sub(r"[^a-zA-Z0-9_]", "_", text)
    if result and result[0].isdigit():
        result = "_" + result
    return result or "tool"


def _json_schema_from_parameters(parameters: list[dict]) -> dict:
    """Build a JSON Schema object from OpenAPI parameter list."""
    props: dict[str, Any] = {}
    required: list[str] = []
    for param in parameters:
        if param.get("in") not in ("query", "path", "header"):
            continue
        name = param["name"]
        schema = dict(param.get("schema", {}))
        if not schema:
            schema = {"type": "string"}
        description = param.get("description", "")
        if description:
            schema["description"] = description
        props[name] = schema
        if param.get("required", False):
            required.append(name)
    result: dict[str, Any] = {"type": "object", "properties": props}
    if required:
        result["required"] = required
    return result


def _json_schema_from_request_body(request_body: dict) -> dict | None:
    """Extract JSON Schema from an OpenAPI requestBody."""
    content = request_body.get("content", {})
    for mime, media in content.items():
        if "json" in mime:
            return media.get("schema")
    return None


def generate(openapi_spec: str, output_dir: Path) -> None:
    """Parse *openapi_spec* and write a FastMCP server to *output_dir*."""
    try:
        spec = yaml.safe_load(openapi_spec)
    except yaml.YAMLError:
        spec = json.loads(openapi_spec)

    servers = spec.get("servers", [{}])
    base_url = (servers[0].get("url", "") if servers else "").rstrip("/")

    tools: list[dict[str, Any]] = []
    paths: dict = spec.get("paths", {})
    for path, path_item in paths.items():
        for method, operation in path_item.items():
            if method.lower() not in ("get", "post", "put", "patch", "delete"):
                continue
            op_id = operation.get("operationId") or f"{method}_{path}"
            func_name = _safe_identifier(op_id)
            summary = operation.get("summary") or operation.get("description") or op_id

            params = operation.get("parameters", [])
            input_schema = _json_schema_from_parameters(params)

            request_body = operation.get("requestBody")
            body_schema: dict | None = None
            if request_body:
                body_schema = _json_schema_from_request_body(request_body)
                if body_schema:
                    # Merge body fields into input_schema
                    body_props = body_schema.get("properties", {})
                    body_required = body_schema.get("required", [])
                    input_schema["properties"].update(body_props)
                    existing_req = input_schema.get("required", [])
                    input_schema["required"] = list(set(existing_req + body_required))

            tools.append(
                {
                    "func_name": func_name,
                    "summary": summary,
                    "method": method.upper(),
                    "path": path,
                    "input_schema": input_schema,
                    "has_body": body_schema is not None,
                    "path_params": [
                        p["name"] for p in params if p.get("in") == "path"
                    ],
                    "query_params": [
                        p["name"] for p in params if p.get("in") == "query"
                    ],
                }
            )

    _write_server(tools, base_url, output_dir)
    _write_requirements(output_dir)


def _write_server(tools: list[dict], base_url: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "\"\"\"Auto-generated MCP server (converted from ChatGPT GPT Actions).\"\"\"",
        "from __future__ import annotations",
        "",
        "import json",
        "import httpx",
        "from mcp.server.fastmcp import FastMCP",
        "",
        f'BASE_URL = "{base_url}"',
        "",
        'mcp = FastMCP("gpt-actions")',
        "",
    ]

    for tool in tools:
        schema_str = json.dumps(tool["input_schema"], ensure_ascii=False, indent=4)
        # Indent the schema for embedding in the docstring / decorator
        props = tool["input_schema"].get("properties", {})
        param_list = ", ".join(
            f'{p}: str = ""' for p in props
        )

        path_fmt = tool["path"]
        for pp in tool["path_params"]:
            path_fmt = path_fmt.replace(f"{{{pp}}}", f"{{{pp}}}")

        query_build = ""
        if tool["query_params"]:
            qp_dict = "{" + ", ".join(f'"{p}": {p}' for p in tool["query_params"]) + "}"
            query_build = f"    params = {{k: v for k, v in {qp_dict}.items() if v}}\n"
        else:
            query_build = "    params = {}\n"

        body_arg = ""
        if tool["has_body"]:
            body_props = [
                p
                for p in props
                if p not in tool["path_params"] and p not in tool["query_params"]
            ]
            if body_props:
                body_dict = "{" + ", ".join(f'"{p}": {p}' for p in body_props) + "}"
                body_arg = f"    body = {{k: v for k, v in {body_dict}.items() if v}}\n"
            else:
                body_arg = "    body = {}\n"

        method = tool["method"]
        if method in ("GET", "DELETE") and not tool["has_body"]:
            request_call = (
                f'    resp = httpx.{method.lower()}('
                f'f"{{BASE_URL}}{path_fmt}", params=params)\n'
            )
        else:
            request_call = (
                f'    resp = httpx.{method.lower()}('
                f'f"{{BASE_URL}}{path_fmt}", params=params, json=body)\n'
            )

        lines += [
            f"@mcp.tool()",
            f"def {tool['func_name']}({param_list}) -> str:",
            f'    """{tool["summary"]}"""',
            query_build.rstrip("\n"),
        ]
        if tool["has_body"]:
            lines.append(body_arg.rstrip("\n"))
        lines += [
            request_call.rstrip("\n"),
            "    resp.raise_for_status()",
            "    return resp.text",
            "",
        ]

    lines += [
        "",
        'if __name__ == "__main__":',
        "    mcp.run()",
    ]

    server_path = output_dir / "server.py"
    server_path.write_text("\n".join(lines), encoding="utf-8")


def _write_requirements(output_dir: Path) -> None:
    req = output_dir / "requirements.txt"
    req.write_text("mcp[cli]>=1.0.0\nhttpx>=0.27.0\n", encoding="utf-8")
