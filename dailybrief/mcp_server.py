from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import sys
from typing import Any

from dailybrief.blockers import detect_blockers
from dailybrief.config import load_config
from dailybrief.git_context import collect_git_context
from dailybrief.memory import load_recent_history
from dailybrief.reader import read_notes

MCP_TOOLS: list[dict[str, Any]] = [
    {
        "name": "get_daily_briefing",
        "description": "Returns the latest executive daily briefing, key priorities, and reminders.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Optional directory containing notes (defaults to ./notes)",
                },
                "lang": {
                    "type": "string",
                    "enum": ["en", "tr"],
                    "description": "Language code (en or tr, defaults to en)",
                },
            },
        },
    },
    {
        "name": "get_git_and_blocker_context",
        "description": "Returns active git branches, uncommitted files, and chronic carry-over blocker alerts.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lang": {
                    "type": "string",
                    "enum": ["en", "tr"],
                    "description": "Language code (en or tr, defaults to en)",
                },
            },
        },
    },
    {
        "name": "mark_task_completed",
        "description": "Marks a specific task or priority as completed in local notes and persistent history.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "task_title": {
                    "type": "string",
                    "description": "The task title or description to mark as completed",
                },
                "note_path": {
                    "type": "string",
                    "description": "Optional path of the markdown note file to append [x] completion",
                },
            },
            "required": ["task_title"],
        },
    },
]


def handle_tool_get_daily_briefing(args: dict[str, Any]) -> str:
    today = date.today().strftime("%Y-%m-%d")
    history = load_recent_history(days=1)
    if history and history[0].date == today:
        return history[0].brief

    # If no cached brief today, attempt reading notes
    source_dir = Path(args.get("source") or "./notes")
    try:
        notes = read_notes(source_dir)
        notes_summary = "\n".join(f"- {n.name}: {n.content[:100]}..." for n in notes)
        return f"Notes available in {source_dir} ({len(notes)} files):\n{notes_summary}\n\nRun 'dailybrief' to generate full LLM synthesis."
    except Exception as exc:
        return f"No daily briefing found for today ({today}). Error reading notes: {exc}"


def handle_tool_get_git_and_blocker_context(args: dict[str, Any]) -> str:
    lang = str(args.get("lang", "en")).lower()
    config = load_config()

    git_ctx = collect_git_context(config.watched_repos if config.watched_repos else None)
    history = load_recent_history(days=5)

    git_summary = git_ctx.format_for_prompt(lang=lang) if git_ctx else "No active git repository detected."

    blockers = detect_blockers(
        history_entries=history,
        git_commits=git_ctx.recent_commits if git_ctx else None,
        git_modified_files=git_ctx.modified_files if git_ctx else None,
        lang=lang,
    )

    blocker_lines = []
    if blockers:
        for b in blockers:
            blocker_lines.append(f"⚠️ {b.task} ({b.streak_days} days carried over) - Advice: {b.advice}")
    else:
        blocker_lines.append("No chronic blockers detected.")

    blocker_str = "\n".join(blocker_lines)
    return f"{git_summary}\n\nChronic Blockers:\n{blocker_str}"


def handle_tool_mark_task_completed(args: dict[str, Any]) -> str:
    task = str(args.get("task_title", "")).strip()
    if not task:
        return "Error: task_title is required."

    today = date.today().strftime("%Y-%m-%d")
    note_path_arg = args.get("note_path")

    if note_path_arg:
        target_path = Path(note_path_arg)
    else:
        notes_dir = Path("./notes")
        notes_dir.mkdir(parents=True, exist_ok=True)
        target_path = notes_dir / f"completed-{today}.md"

    entry = f"\n- [x] {task} (Completed via MCP on {today})\n"
    if target_path.exists():
        content = target_path.read_text(encoding="utf-8")
        target_path.write_text(content + entry, encoding="utf-8")
    else:
        target_path.write_text(f"# Completed Tasks - {today}\n{entry}", encoding="utf-8")

    return f"Successfully marked task '{task}' as completed in {target_path.resolve()}."


def execute_mcp_tool(name: str, args: dict[str, Any]) -> str:
    if name == "get_daily_briefing":
        return handle_tool_get_daily_briefing(args)
    elif name == "get_git_and_blocker_context":
        return handle_tool_get_git_and_blocker_context(args)
    elif name == "mark_task_completed":
        return handle_tool_mark_task_completed(args)
    else:
        raise ValueError(f"Unknown MCP tool: {name}")


def handle_mcp_request(req: dict[str, Any]) -> dict[str, Any] | None:
    req_id = req.get("id")
    method = req.get("method")
    params = req.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "dailybrief",
                    "version": "0.2.0",
                },
            },
        }
    elif method in ("notifications/initialized", "initialized"):
        # Notification - no response
        return None
    elif method == "ping":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {},
        }
    elif method in ("tools/list", "tools/listTools"):
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": MCP_TOOLS,
            },
        }
    elif method in ("tools/call", "tools/executeTool"):
        tool_name = params.get("name")
        tool_args = params.get("arguments", {})
        try:
            output_text = execute_mcp_tool(tool_name, tool_args)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": output_text,
                        }
                    ],
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32603,
                    "message": f"Tool execution error: {exc}",
                },
            }
    else:
        if req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {
                    "code": -32601,
                    "message": f"Method '{method}' not found",
                },
            }
        return None


def run_mcp_server() -> None:
    # Stdio loop reading JSON-RPC messages from stdin and replying to stdout
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            # Support Content-Length header framing if client sends it
            if line.startswith("Content-Length:"):
                length_str = line.split(":", 1)[1].strip()
                length = int(length_str)
                # Read blank line
                sys.stdin.readline()
                content = sys.stdin.read(length)
                req_data = json.loads(content)
            else:
                req_data = json.loads(line)

            resp_data = handle_mcp_request(req_data)
            if resp_data is not None:
                encoded = json.dumps(resp_data, ensure_ascii=False)
                sys.stdout.write(encoded + "\n")
                sys.stdout.flush()
        except KeyboardInterrupt:
            break
        except Exception as exc:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()
