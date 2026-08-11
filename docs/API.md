# API 文档

服务启动后默认地址：

```text
http://127.0.0.1:5000
```

## 预览 PPT 结构

接口：

```http
POST /api/preview
```

表单字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `content_file` | file | 可选，支持 `.md`、`.txt`、`.docx`、`.doc`、`.wps` |
| `image_files` | file[] | 可选，可上传多张图片 |
| `content_text` | text | 可选，未上传文件时使用 |

示例：

```bash
curl -X POST http://127.0.0.1:5000/api/preview \
  -F "content_file=@inputs/example.md"
```

返回：

```json
{
  "title": "PPT 生成项目演示",
  "total_pages": 10,
  "slides": [
    {
      "index": 1,
      "title": "PPT 生成项目演示",
      "meta": "封面"
    }
  ]
}
```

## 生成 PPT

接口：

```http
POST /api/generate
```

表单字段：

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `content_file` | file | 可选，支持 `.md`、`.txt`、`.docx`、`.doc`、`.wps` |
| `image_files` | file[] | 可选，可上传多张图片 |
| `content_text` | text | 可选，未上传文件时使用 |
| `theme` | text | 可选，`auto`、`business`、`clean`、`dark`、`midnight`、`emerald`、`sunrise`、`ivory`、`tech`、`construction` |
| `footer` | text | 可选，页脚文字 |
| `output_name` | text | 可选，导出文件名 |

示例：

```bash
curl -X POST http://127.0.0.1:5000/api/generate \
  -F "content_file=@inputs/example.md" \
  -F "theme=tech" \
  -F "output_name=demo" \
  --output demo.pptx
```

## 错误返回

```json
{
  "error": "错误说明"
}
```

## Docker 部署

构建镜像：

```bash
docker build -t ppt-generator .
```

运行：

```bash
docker run --rm -p 5000:5000 ppt-generator
```

访问：

```text
http://127.0.0.1:5000
```
