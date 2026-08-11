# PPT Generator

一个根据 Markdown 或文本提纲自动生成 PowerPoint 文件的项目。

## 当前功能

- 读取 Markdown 文件
- 将一级标题作为封面标题
- 将二级标题拆成独立内容页
- 将普通段落和列表转换为 PPT 内容
- 导出 `.pptx` 文件

## 快速开始

安装依赖：

```bash
pip install -r requirements.txt
```

生成示例 PPT：

```bash
python main.py inputs/example.md outputs/example.pptx
```

## Markdown 写法

```markdown
# 演示标题

## 第一页标题

- 要点一
- 要点二

## 第二页标题

这里是一段正文。
```

## 项目结构

```text
ppt-generator/
├─ main.py
├─ requirements.txt
├─ inputs/
│  └─ example.md
├─ outputs/
└─ src/
   ├─ markdown_parser.py
   └─ ppt_builder.py
```
一个根据文本、Markdown或提纲自动生成PPT的项目
