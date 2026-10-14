from __future__ import annotations

from pathlib import Path

from dailybrief.mcp_server import (
    MCP_TOOLS,
    handle_mcp_request,
    handle_tool_mark_task_completed,
)
from dailybrief.memory import save_history_entry


def test_mcp_initialize() -> None:
    req = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {},
    }
    resp = handle_mcp_request(req)
    assert resp is not None
    assert resp["id"] == 1
    assert resp["result"]["serverInfo"]["name"] == "dailybrief"
    assert "tools" in resp["result"]["capabilities"]


def test_mcp_tools_list() -> None:
    req = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
    }
    resp = handle_mcp_request(req)
    assert resp is not None
    tools = resp["result"]["tools"]
    assert len(tools) == 3
    tool_names = [t["name"] for t in tools]
    assert "get_daily_briefing" in tool_names
    assert "get_git_and_blocker_context" in tool_names
    assert "mark_task_completed" in tool_names


def test_mcp_call_get_daily_briefing(tmp_path: Path) -> None:
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_daily_briefing",
            "arguments": {"source": str(tmp_path)},
        },
    }
    resp = handle_mcp_request(req)
    assert resp is not None
    assert "result" in resp
    content = resp["result"]["content"][0]["text"]
    assert isinstance(content, str)


def test_mcp_call_get_git_and_blocker_context() -> None:
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_git_and_blocker_context",
            "arguments": {"lang": "en"},
        },
    }
    resp = handle_mcp_request(req)
    assert resp is not None
    content = resp["result"]["content"][0]["text"]
    assert "Chronic Blockers" in content


def test_mcp_call_mark_task_completed(tmp_path: Path) -> None:
    note_file = tmp_path / "tasks.md"
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "mark_task_completed",
            "arguments": {
                "task_title": "Fix memory leak in auth middleware",
                "note_path": str(note_file),
            },
        },
    }
    resp = handle_mcp_request(req)
    assert resp is not None
    assert "Successfully marked task" in resp["result"]["content"][0]["text"]
    assert note_file.exists()
    content = note_file.read_text(encoding="utf-8")
    assert "- [x] Fix memory leak in auth middleware" in content


def test_mcp_invalid_method() -> None:
    req = {
        "jsonrpc": "2.0",
        "id": 99,
        "method": "unknown_rpc_method",
    }
    resp = handle_mcp_request(req)
    assert resp is not None
    assert resp["error"]["code"] == -32601
