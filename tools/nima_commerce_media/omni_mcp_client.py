from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests

DEFAULT_ENDPOINT = "https://image-toolkit-production.up.railway.app/mcp"
PROTOCOL_VERSION = "2025-03-26"


@dataclass
class MCPResponse:
    payload: dict[str, Any]
    session_id: str | None = None


def _decode_response(response: requests.Response) -> dict[str, Any]:
    ctype = response.headers.get("content-type", "")
    text = response.text
    if "text/event-stream" in ctype:
        data_lines = []
        for line in text.splitlines():
            if line.startswith("data:"):
                data_lines.append(line[5:].strip())
        for raw in reversed(data_lines):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                continue
        raise RuntimeError("MCP SSE response contained no JSON data event")
    return response.json()


class StreamableHTTPMCPClient:
    def __init__(self, endpoint: str, timeout: int = 60):
        self.endpoint = endpoint
        self.timeout = timeout
        self.session = requests.Session()
        self.session_id: str | None = None
        self.next_id = 1

    @property
    def headers(self) -> dict[str, str]:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
        }
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id
        return headers

    def request(self, method: str, params: dict[str, Any] | None = None) -> MCPResponse:
        request_id = self.next_id
        self.next_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params
        response = self.session.post(self.endpoint, headers=self.headers, json=payload, timeout=self.timeout)
        response.raise_for_status()
        self.session_id = response.headers.get("Mcp-Session-Id") or self.session_id
        body = _decode_response(response)
        if body.get("error"):
            raise RuntimeError(f"MCP {method} failed: {body['error']}")
        return MCPResponse(body, self.session_id)

    def notify(self, method: str, params: dict[str, Any] | None = None) -> None:
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        response = self.session.post(self.endpoint, headers=self.headers, json=payload, timeout=self.timeout)
        if response.status_code not in {200, 202, 204}:
            response.raise_for_status()
        self.session_id = response.headers.get("Mcp-Session-Id") or self.session_id

    def initialize(self) -> dict[str, Any]:
        response = self.request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "nima-commerce-media-factory", "version": "1.0"},
            },
        )
        self.notify("notifications/initialized")
        return response.payload["result"]

    def list_tools(self) -> list[dict[str, Any]]:
        response = self.request("tools/list")
        return response.payload["result"].get("tools", [])

    def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        response = self.request("tools/call", {"name": name, "arguments": arguments})
        return response.payload["result"]


def probe(endpoint: str, output: Path) -> int:
    client = StreamableHTTPMCPClient(endpoint)
    initialized = client.initialize()
    tools = client.list_tools()
    payload = {
        "endpoint": endpoint,
        "protocolVersion": initialized.get("protocolVersion"),
        "serverInfo": initialized.get("serverInfo"),
        "capabilities": initialized.get("capabilities"),
        "session_id_present": bool(client.session_id),
        "tools": tools,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Connected to OMNI MCP: {payload.get('serverInfo')}")
    print(f"Discovered {len(tools)} tool(s)")
    for tool in tools:
        print(f"- {tool.get('name')}: {tool.get('description','')[:140]}")
    return 0 if tools else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="OMNI Streamable HTTP MCP client for Nima")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--probe", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("commerce-media-evidence/omni-mcp-tools.json"))
    parser.add_argument("--tool")
    parser.add_argument("--arguments", default="{}", help="JSON object for tools/call")
    args = parser.parse_args()

    if args.probe:
        return probe(args.endpoint, args.output)

    if args.tool:
        client = StreamableHTTPMCPClient(args.endpoint)
        client.initialize()
        result = client.call_tool(args.tool, json.loads(args.arguments))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0

    parser.error("Use --probe or --tool")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
