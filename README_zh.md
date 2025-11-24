# markdown-paper

> 中文 | [English](./README.md)

**markdown-paper** 是一个极简的 Python 命令行工具，用来管理你用 Markdown 书写的文献笔记。  
它受到了 [Mu Li](https://www.bilibili.com/video/BV1nA41157y4) 老师的启发，在 [autoLiterature](https://github.com/WilmerWang/autoLiterature) 的基础上做了简化与修改，让和 Markdown 的配合更加顺滑。

推荐最佳实践：搭配 Typora 使用，并在 Typora 中将图片和文件引用路径改为 **相对路径**。

最后，将文献和 Markdown 笔记放置于一个文件夹下，用 LLM 和 Agent 来食用文献，如 Copilot，效果更佳。

## 功能概览

### 1. 从 Markdown 笔记出发，获取文献及元信息

markdown-paper 会扫描指定的 Markdown 文件或文件夹，自动识别文献 ID，并：

- 更新笔记中该文献的元信息；
- 可选地下载对应 PDF。

**识别规则：**

- 自动识别列表项中的 `- {xxx}`。
- 当笔记中包含 `- {paper_id}` 时：仅更新文献元信息，**不下载 PDF**。
- 当笔记中包含 `- {{paper_id}}` 时：更新文献元信息，并 **下载 PDF**。

`paper_id` 支持以下类型：

- 已发表文章：`doi`
- 预印本：`arxiv_id`、`biorxiv_id`、`medrxiv_id`（注意拼写）

基本用法：

```bash
md-paper -i <note-file-or-folder> [-o <output-folder>] [-p <proxy>]
```

- `-i` / `--input` ：指向单个 Markdown 文件或包含多个 Markdown 笔记的文件夹。
- `-o` / `--output`：保存 PDF 和图片的目标文件夹（必须是一个文件夹）。
- `-p` / `--proxy` ：代理地址，例如 `127.0.0.1:7890`。

### 2. 从 PDF 出发，重命名并回写元信息到 Markdown

对于一些需要登录才能下载或无法直接抓取的论文，可以先手动下载 PDF，再让 md-paper 来：

1. 读取 PDF 前几页，识别其中的 DOI；
2. 通过 CrossRef 获取题目 / 作者 / 期刊 / 引用次数等；
3. 将 PDF 重命名为 `Title.pdf`；
4. 同步在 Markdown 笔记中添加或更新对应条目。

用法：

```bash
md-paper -i <note-file> -r <pdf-folder> [-p <proxy>]
```

- `-i` / `--input`  ：指向要追加 / 更新条目的 Markdown 文件。
- `-r` / `--rename`：指向待处理 PDF 所在的文件夹。
- `-p` / `--proxy` ：用于访问 CrossRef 的代理。

如果某些 PDF 中未检测到 DOI，或 CrossRef 未返回信息，  
程序会在日志中给出警告，并 **不会重命名** 这些文件。

## 安装

### 1. 使用 pip 安装

```bash
pip install markdown-paper
# 或者
pip3 install markdown-paper
```

### 2. 源码安装

```bash
git clone https://github.com/ryan-utopia/markdown-paper.git
cd markdown-paper
python setup.py install
```

## 命令行参数

```bash
md-paper

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        The path to the note file or note file folder.
  -o OUTPUT, --output OUTPUT
                        The folder path to save paper pdfs and images. NOTE: MUST BE FOLDER
  -r RENAME, --rename RENAME
                        The folder path that contains pdfs to be renamed.
  -p PROXY, --proxy PROXY
                        The proxy. e.g. 127.0.0.1:7890
```

## 许可证

本项目采用 MIT 协议开源，详情见 [LICENSE](./LICENSE) 文件。
