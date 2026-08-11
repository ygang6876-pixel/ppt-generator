# 生产环境部署

## 本地 Docker 运行

复制环境变量：

```bash
cp .env.example .env
```

构建并启动：

```bash
docker compose up -d --build
```

查看状态：

```bash
docker compose ps
```

访问：

```text
http://127.0.0.1:5000
```

健康检查：

```bash
curl http://127.0.0.1:5000/healthz
```

## 单独使用 Docker

构建镜像：

```bash
docker build -t ppt-generator .
```

运行容器：

```bash
docker run --rm -p 5000:5000 --env-file .env.example ppt-generator
```

## 生产启动方式

容器内默认使用 Gunicorn 启动：

```bash
gunicorn -c gunicorn.conf.py app:app
```

## 环境变量

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `PPT_GENERATOR_PORT` | `5000` | 对外服务端口 |
| `WEB_CONCURRENCY` | CPU 自动计算 | Gunicorn worker 数 |
| `GUNICORN_THREADS` | `2` | 每个 worker 的线程数 |
| `GUNICORN_TIMEOUT` | `180` | 请求超时时间，PPT/Mermaid 生成可能较慢 |
| `GUNICORN_GRACEFUL_TIMEOUT` | `30` | 优雅退出等待时间 |
| `GUNICORN_KEEPALIVE` | `5` | Keep-alive 时间 |
| `GUNICORN_LOG_LEVEL` | `info` | 日志级别 |

## Mermaid 渲染

Docker 镜像中安装了 Chromium，并配置：

```text
PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
```

Mermaid CLI 使用 `puppeteer-config.json` 中的 no-sandbox 配置，适配容器环境。

## 注意事项

- `.doc` / `.wps` 自动转换在 Linux 容器中依赖 LibreOffice 或其他转换工具；当前 Dockerfile 默认不安装 LibreOffice。
- 推荐生产环境优先上传 `.docx`、Markdown、图片。
- 如果需要容器内直接转换 `.doc` / `.wps`，可扩展 Dockerfile 安装 LibreOffice。
