# recon-cli

一个用 Python 写的轻量资产侦察命令行工具（学习项目，持续迭代中）。
> 环境要求：Python 3.10+（开发和测试用 3.12.4）
## 30 秒上手

```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python recon.py https://example.com
```

> Windows 用 `.venv\Scripts\activate`；Linux / macOS 用 `source .venv/bin/activate`。

## 它做什么

- 发起 HTTP/HTTPS 请求，输出状态码、页面标题、Server 头
- 输出 TLS 证书到期时间与剩余天数
- 打印请求耗时与响应体大小

## 结果

```
====================================================
URL      : https://example.com/
状态码   : 200
标题     : Example Domain
Server   : cloudflare
耗时     : 0.75 秒
长度     : 577 字节
证书到期 : 2026-12-25（剩 66 天）
====================================================
```

## 局限与后续

- 只支持单个 URL，不做批量、不做子域爆破
- 单线程逐个请求，没有并发
- 不解析 robots.txt、sitemap，不做指纹库匹配
- 下一步：并发 + 指纹识别 + JSON 报告输出

## License

MIT，见 [LICENSE](LICENSE)