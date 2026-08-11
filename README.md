# PPT Generator

一个根据 Markdown 或文本提纲自动生成 PowerPoint 文件的项目。

## 当前功能

- 读取 Markdown 文件
- 将一级标题作为封面标题
- 将二级标题拆分成独立内容页
- 将普通段落和列表转换为 PPT 内容
- 支持 Markdown 图片插入
- 支持 Markdown 表格转 PPT 表格
- 使用中文字体和统一主题样式
- 支持自定义页脚文字
- 支持网页粘贴或上传 Markdown 后生成 PPT
- 导出 `.pptx` 文件

## 快速开始

安装依赖：

```bash
pip install -r requirements.txt
```

命令行生成示例 PPT：

```bash
python main.py inputs/example.md outputs/example.pptx
```

命令行生成带自定义页脚的 PPT：

```bash
python main.py inputs/example.md outputs/example.pptx --footer "我的PPT生成项目"
```

启动网页界面：

```bash
python app.py
```

打开浏览器访问：

```text
http://127.0.0.1:5000
```

## Markdown 写法

```markdown
# 演示标题

这里会作为封面副标题。

## 第一页标题

- 要点一
- 要点二

## 第二页标题

这里是一段正文。

![图片说明](images/demo.png)

## 表格页

| 模块 | 状态 | 说明 |
| --- | --- | --- |
| 标题页 | 已完成 | 自动生成封面 |
| 内容页 | 已完成 | 支持段落和列表 |
| 表格页 | 已完成 | Markdown 表格转 PPT 表格 |
```

## 项目结构

```text
ppt-generator/
|-- app.py
|-- main.py
|-- requirements.txt
|-- inputs/
|   |-- example.md
|   `-- images/
|       `-- demo.png
|-- outputs/
`-- src/
    |-- markdown_parser.py
    |-- ppt_builder.py
    `-- theme.py
```

## 后续计划

- 支持更多主题模板
- 支持 Word 文档转 PPT
- 增加图片文件一并上传
