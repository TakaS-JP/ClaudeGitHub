#!/usr/bin/env python3
"""Migrate a ChatGPT GPT configuration to Claude.ai.

Usage:
    python migrate.py --gpt-config gpt_export.json --output-dir ./output

Outputs:
    output/claude_project_setup.md   — Step-by-step Claude.ai project setup guide
    output/mcp_server/server.py      — FastMCP server (only when GPT has custom actions)
    output/mcp_server/requirements.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from migrator import gpt_parser, mcp_generator, claude_project


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert a ChatGPT GPT export to a Claude.ai project setup."
    )
    parser.add_argument(
        "--gpt-config",
        required=True,
        metavar="FILE",
        help="Path to the GPT export JSON file.",
    )
    parser.add_argument(
        "--output-dir",
        default="output",
        metavar="DIR",
        help="Directory where generated files are written (default: ./output).",
    )
    args = parser.parse_args()

    gpt_config_path = Path(args.gpt_config)
    if not gpt_config_path.is_file():
        print(f"Error: GPT config file not found: {gpt_config_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = Path(args.output_dir)

    print(f"Loading GPT config from {gpt_config_path} ...")
    try:
        config = gpt_parser.load(gpt_config_path)
    except (ValueError, KeyError) as exc:
        print(f"Error parsing GPT config: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"  Name        : {config.name}")
    print(f"  Description : {config.description or '(none)'}")
    print(f"  Knowledge   : {len(config.knowledge_files)} file(s)")
    print(f"  Actions     : {'yes' if config.openapi_spec else 'no'}")

    has_mcp = False
    if config.openapi_spec:
        mcp_dir = output_dir / "mcp_server"
        print(f"\nGenerating MCP server → {mcp_dir}/")
        try:
            mcp_generator.generate(config.openapi_spec, mcp_dir)
            has_mcp = True
            print("  server.py and requirements.txt written.")
        except Exception as exc:  # noqa: BLE001
            print(f"Warning: Could not generate MCP server: {exc}", file=sys.stderr)

    print(f"\nGenerating Claude project setup guide → {output_dir}/claude_project_setup.md")
    claude_project.generate(config, output_dir, has_mcp=has_mcp)

    print("\nDone!")
    print(f"  {output_dir}/claude_project_setup.md")
    if has_mcp:
        print(f"  {output_dir}/mcp_server/server.py")
        print(f"  {output_dir}/mcp_server/requirements.txt")


if __name__ == "__main__":
    main()
