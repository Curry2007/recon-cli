"""recon-cli v0.1：最小可用的 URL 侦察工具。"""
import sys
import re
import ssl
import socket
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


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: python recon.py https://example.com")
        return 2

    url = sys.argv[1]
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    try:
        resp = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
    except requests.RequestException as exc:
        print(f"[!] 请求失败: {exc}")
        return 1

    match = re.search(r"<title[^>]*>(.*?)</title>", resp.text, re.I | re.S)
    title = match.group(1).strip() if match else "(无 title)"

    print("=" * 52)
    print(f"URL      : {resp.url}")
    print(f"状态码   : {resp.status_code}")
    print(f"标题     : {title[:70]}")
    print(f"Server   : {resp.headers.get('Server', '(无)')}")
    print(f"耗时     : {resp.elapsed.total_seconds():.2f} 秒")
    print(f"长度     : {len(resp.content)} 字节")

    if resp.url.startswith("https://"):
        host = urlparse(resp.url).hostname
        expiry = get_cert_expiry(host)
        if expiry:
            now = datetime.datetime.now(datetime.timezone.utc)
            print(f"证书到期 : {expiry:%Y-%m-%d}（剩 {(expiry - now).days} 天）")
        else:
            print("证书到期 : 取不到")
    print("=" * 52)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())