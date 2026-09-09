# 📚 课程作业查重小助手

一个帮你快速揪出小组作业中“复制粘贴”段落的 Python 命令行工具。

> 您是否被查重困扰？是否被小组作业逼到要疯掉？欢迎关注这个“自救脚本”。如果你也有类似的烦恼，欢迎拿去用，也欢迎改造成你想要的样子。

---

## 项目简介

基于 TF-IDF 算法计算文本间的相似度，能快速标出哪些段落需要人工复核。

---

## ✨主要功能

- 支持 `.txt` 和 `.docx` 格式文件
- 批量计算多个文件之间的相似度矩阵
- 一键生成相似度热力图（可视化）
- 高亮显示重复度最高的前 N 个句子
- 输出 HTML 格式的对比报告（便于分享）

---

## 技术栈

| 用途 | 工具/库 |
|------|---------|
| 文本处理 | Python 3.9 + jieba（中文分词） |
| 相似度计算 | Scikit-learn (TF-IDF + 余弦相似度) |
| 文档解析 | PyMuPDF (PDF) + python-docx (DOCX) |
| 可视化 | Matplotlib + Seaborn |
| 报告生成 | Jinja2（HTML 模板） |

---

## 如何运行

### 环境要求
- Python 3.8+
- pip

### 安装步骤

```bash
# 1. 克隆仓库（或下载本目录）
git clone https://github.com/你的用户名/你的项目名.git
cd 你的项目名

# 2. 安装依赖
pip install -r requirements.txt

# 3. 将待检测的文档放入 docs/ 目录下
# 支持格式：.txt, .docx

# 4. 运行主程序
python main.py --dir ./docs

# 可选参数：
# --output 指定报告输出目录（默认 reports/）
# --top N 显示重复度最高的 N 个句子（默认 5）
