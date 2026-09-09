# 📚 课程作业查重小助手
一个基于 Python 的简易文本相似度检测工具，帮助我快速检查小组作业中是否有重复段落。

## 项目简介
上学期写小组报告时，大家分工合作，但最后整合时发现有些同学写的内容非常相似。为了在提交前快速自查，我写了这个小脚本，利用 TF-IDF 算法计算文本相似度。

## ✨ 主要功能
- 支持 `.txt` 和 `.docx` 文件上传
- 一键生成相似度热力图
- 高亮显示重复度最高的句子

## 🛠️ 技术栈
- Python 3.9
- Scikit-learn (TF-IDF)
- PyMuPDF (读取PDF)
- Matplotlib (绘图)

## 🚀 如何运行
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 将待检测文件放入 /docs 目录
# 3. 运行主程序
python main.py --dir ./docs
```
