# -*- coding: utf-8 -*-
"""
本地代理桥：把浏览器无法直接使用的「带用户名密码」上游代理，桥接成本地无鉴权代理。

用法：
    python3 proxy_bridge.py --upstream "http://user:pass@host:port" --listen 127.0.0.1:8899

说明：
    Chromium / DrissionPage 的 --proxy-server 不支持带账号密码的代理（ERR_NO_SUPPORTED_PROXIES）。
    本脚本在本地监听一个无鉴权端口，收到浏览器的 CONNECT 请求后，用「Proxy-Authorization: Basic」
    转发到上游代理，从而让浏览器能走带鉴权的代理。

仅实现 HTTPS CONNECT 隧道（chatgpt.com / pay.153.ink 等均为 HTTPS，足够使用）。
"""
from __future__ import annotations

import argparse
import base64
import select
import socket
import threading
from urllib.parse import urlparse


def parse_upstream(raw: str):
    if "://" not in raw:
        raw = "http://" + raw
    u = urlparse(raw)
    host = u.hostname or ""
    port = u.port or 80
    user = u.username or ""
    password = u.password or ""
    return host, port, user, password


def relay(a: socket.socket, b: socket.socket):
    try:
        while True:
            r, _, _ = select.select([a, b], [], [], 120)
            if not r:
                break
            for s in r:
                data = s.recv(65536)
                if not data:
                    return
                (b if s is a else a).sendall(data)
    except Exception:
        pass
    finally:
        for s in (a, b):
            try:
                s.close()
            except Exception:
                pass


def handle(client: socket.socket, upstream_host: str, upstream_port: int, auth_header: str):
    up = None
    try:
        buf = b""
        while b"\r\n\r\n" not in buf:
            d = client.recv(4096)
            if not d:
                return
            buf += d
        first_line = buf.split(b"\r\n", 1)[0].decode("utf-8", "replace")
        parts = first_line.split()
        if len(parts) < 2 or parts[0].upper() != "CONNECT":
            # 仅支持 CONNECT（HTTPS）
            try:
                client.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            except Exception:
                pass
            return
        target = parts[1]  # host:port

        up = socket.create_connection((upstream_host, upstream_port), timeout=20)
        req = (
            f"CONNECT {target} HTTP/1.1\r\n"
            f"Host: {target}\r\n"
            f"Proxy-Authorization: Basic {auth_header}\r\n"
            f"\r\n"
        )
        up.sendall(req.encode("utf-8"))

        resp = b""
        while b"\r\n\r\n" not in resp:
            d = up.recv(4096)
            if not d:
                return
            resp += d
        status_line = resp.split(b"\r\n", 1)[0].decode("utf-8", "replace")
        if "200" in status_line:
            client.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")
        else:
            client.sendall(resp)
            return

        relay(client, up)
    except Exception:
        pass
    finally:
        try:
            client.close()
        except Exception:
            pass
        if up:
            try:
                up.close()
            except Exception:
                pass


def main():
    parser = argparse.ArgumentParser(description="本地代理桥")
    parser.add_argument("--upstream", required=True, help="上游代理，例如 http://user:pass@host:port")
    parser.add_argument("--listen", default="127.0.0.1:8899", help="本地监听地址，默认 127.0.0.1:8899")
    args = parser.parse_args()

    host, port, user, password = parse_upstream(args.upstream)
    if not host:
        raise SystemExit("上游代理地址无效")
    cred = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")

    lh, _, lp = args.listen.rpartition(":")
    listen_host = lh or "127.0.0.1"
    listen_port = int(lp or 8899)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((listen_host, listen_port))
    srv.listen(128)
    print(f"[proxy-bridge] 本地监听 {listen_host}:{listen_port} -> 上游 {host}:{port} (auth={'yes' if user else 'no'})", flush=True)

    while True:
        c, _ = srv.accept()
        threading.Thread(target=handle, args=(c, host, port, cred), daemon=True).start()


if __name__ == "__main__":
    main()
