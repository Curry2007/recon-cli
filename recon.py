"""recon-cli v0.2：函数化的 URL 侦察工具。"""
import sys
import re
import ssl
import socket
import json
import argparse
import datetime
from urllib.parse import urlparse

import requests

TIMEOUT = 8


def get_cert_expiry(host: str, port: int = 443):
    """取 TLS 证书到期时间；失败返回 None。"""
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=TIMEOUT) as raw:
            with ctx.wrap_socket(raw, server_hostname=host) as tls:
                cert = tls.getpeercert()
        naive = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
        return naive.replace(tzinfo=datetime.timezone.utc)
    except Exception:
        return None


def fetch(url: str, timeout: int = TIMEOUT, allow_redirects: bool = True):
    
    return requests.get(url, timeout=timeout, allow_redirects=allow_redirects)


def get_title(html: str) -> str:
    """从 HTML 里提取 <title> 内容；找不到返回 '(无 title)'。"""
    match = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
    return match.group(1).strip() if match else "(无 title)"


def build_report(resp, title: str) -> dict:
    """把 Response 组装成纯数据字典。"""
    data = {
        "url": resp.url,
        "status": resp.status_code,
        "title": title[:70],
        "server": resp.headers.get("Server", ""),
        "elapsed": round(resp.elapsed.total_seconds(), 2),
        "length": len(resp.content),
    }
    if resp.url.startswith("https://"):
        host = urlparse(resp.url).hostname
        expiry = get_cert_expiry(host)
        if expiry:
            now = datetime.datetime.now(datetime.timezone.utc)
            data["cert_expiry"] = expiry.strftime("%Y-%m-%d")
            data["cert_days_left"] = (expiry - now).days
    return data


def print_report(data: dict) -> None:
    """把字典按人看的格式打印。"""
    print("=" * 52)
    print(f"URL      : {data['url']}")
    print(f"状态码   : {data['status']}")
    print(f"标题     : {data['title']}")
    print(f"Server   : {data['server'] or '(无)'}")
    print(f"耗时     : {data['elapsed']:.2f} 秒")
    print(f"长度     : {data['length']} 字节")
    if "cert_expiry" in data:
        print(f"证书到期 : {data['cert_expiry']}（剩 {data['cert_days_left']} 天）")
    print("=" * 52)


def parse_args():
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description="轻量资产侦察工具")
    parser.add_argument("url", help="目标 URL，例如 https://example.com")
    parser.add_argument("--timeout", type=int, default=TIMEOUT, help="超时秒数，默认 8")
    parser.add_argument("--json", action="store_true", help="以 JSON 格式输出")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        resp = fetch(url, timeout=args.timeout)
    except requests.RequestException as exc:
        print(f"[!] 请求失败: {exc}")
        return 1

    data = build_report(resp, get_title(resp.text))

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print_report(data)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())