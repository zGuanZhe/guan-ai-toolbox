#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Context Protocol (MCP) 标准服务模板 (Python 版)
遵循 Model Context Protocol 规范，通过标准输入输出 (stdio) 提供 Tool 与 Resource。
"""

import sys
import json

def send_response(response):
    payload = json.dumps(response, ensure_ascii=False)
    sys.stdout.write(f"Content-Length: {len(payload.encode('utf-8'))}\r\n\r\n{payload}")
    sys.stdout.flush()

def handle_request(req):
    method = req.get("method")
    req_id = req.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "guan-toolbox-mcp",
                    "version": "1.0.0"
                }
            }
        }
    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "ping",
                        "description": "测试 MCP 连接活性与响应延迟",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "message": {"type": "string"}
                            }
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "ping":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [
                        {"type": "text", "text": f"pong: {args.get('message', 'hello')}"}
                    ]
                }
            }
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": "Method not found"}
    }

def main():
    # 极简 stdio JSON-RPC 消息循环
    pass

if __name__ == "__main__":
    main()
