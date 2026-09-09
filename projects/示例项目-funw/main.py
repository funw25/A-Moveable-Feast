#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
课程作业查重小助手
基于 TF‑IDF 的文本相似度检测工具
支持 .txt, .docx, .pdf 文件
生成相似度热力图 + 高亮重复句子
"""

import os
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Dict

import numpy as np
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# 尝试导入可选分词库，若失败则使用默认分词器
try:
    import jieba
    USE_JIEBA = True
except ImportError:
    USE_JIEBA = False
    print("⚠️ 未安装 jieba，将使用默认字符分词（中文效果较差），建议 pip install jieba")

# 读取不同格式文件的函数
def read_file(filepath: str) -> str:
    """根据文件扩展名读取文本内容"""
    ext = Path(filepath).suffix.lower()
    if ext == '.txt':
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    elif ext == '.docx':
        try:
            import docx
            doc = docx.Document(filepath)
            return '\n'.join([para.text for para in doc.paragraphs])
        except ImportError:
            raise ImportError("需要安装 python-docx 来读取 .docx 文件")
    elif ext == '.pdf':
        try:
            import fitz  # PyMuPDF
            text = ''
            with fitz.open(filepath) as pdf:
                for page in pdf:
                    text += page.get_text()
            return text
        except ImportError:
            raise ImportError("需要安装 PyMuPDF 来读取 .pdf 文件")
    else:
        raise ValueError(f"不支持的文件类型: {ext}")

def split_sentences(text: str) -> List[str]:
    """简单中文分句（按句号、问号、感叹号、换行分割）"""
    import re
    # 按中文标点分割，保留分割符以增强句子完整性
    sentences = re.split(r'[。！？\n]+', text)
    # 过滤空句子
    return [s.strip() for s in sentences if s.strip()]

def get_custom_tokenizer():
    """返回自定义分词器（使用 jieba 或按字符切分）"""
    if USE_JIEBA:
        def tokenizer(text):
            return list(jieba.cut(text))
        return tokenizer
    else:
        # 默认按单字符切分（对中文不够友好，但可工作）
        return lambda text: list(text)

def compute_document_similarity(docs: List[str]) -> Tuple[np.ndarray, TfidfVectorizer, np.ndarray]:
    """计算文档间相似度矩阵（基于 TF‑IDF）"""
    vectorizer = TfidfVectorizer(
        tokenizer=get_custom_tokenizer(),
        lowercase=False,        # 中文无需小写
        token_pattern=None,     # 使用自定义 tokenizer
        min_df=1,
        max_df=1.0,
        smooth_idf=True
    )
    tfidf_matrix = vectorizer.fit_transform(docs)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix, vectorizer, tfidf_matrix

def plot_heatmap(similarity_matrix: np.ndarray, filenames: List[str], output_path: str = "similarity_heatmap.png"):
    """绘制相似度热力图并保存"""
    plt.figure(figsize=(10, 8))
    plt.imshow(similarity_matrix, cmap='hot', interpolation='nearest')
    plt.colorbar(label='相似度')
    plt.title('文档相似度热力图')
    plt.xticks(range(len(filenames)), filenames, rotation=45, ha='right')
    plt.yticks(range(len(filenames)), filenames)
    # 在每个格子显示数值
    for i in range(len(filenames)):
        for j in range(len(filenames)):
            plt.text(j, i, f'{similarity_matrix[i, j]:.2f}',
                     ha='center', va='center', color='white', fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"✅ 热力图已保存至: {output_path}")

def find_top_sentence_pairs(
    docs: List[str],
    filenames: List[str],
    similarity_threshold: float = 0.6,
    top_k: int = 5
) -> List[Dict]:
    """
    找出跨文档重复度最高的句子对（基于句子级 TF‑IDF）
    返回: 列表，每个元素包含 {文档1, 句子1, 文档2, 句子2, 相似度}
    """
    # 1. 分句并记录归属
    sentences_per_doc = [split_sentences(doc) for doc in docs]
    all_sentences = []
    sentence_meta = []  # (doc_idx, sent_idx)
    for doc_idx, sent_list in enumerate(sentences_per_doc):
        for sent_idx, sent in enumerate(sent_list):
            all_sentences.append(sent)
            sentence_meta.append((doc_idx, sent_idx))

    if len(all_sentences) < 2:
        print("⚠️ 总句子数不足，跳过句子级分析")
        return []

    # 2. 计算句子 TF‑IDF
    vectorizer_sent = TfidfVectorizer(
        tokenizer=get_custom_tokenizer(),
        lowercase=False,
        token_pattern=None,
        min_df=1,
        max_df=1.0,
        smooth_idf=True
    )
    sent_tfidf = vectorizer_sent.fit_transform(all_sentences)
    # 计算相似度矩阵（仅上三角，节省内存）
    sim_matrix = cosine_similarity(sent_tfidf)

    # 3. 收集跨文档句子对
    pairs = []
    n = len(all_sentences)
    for i in range(n):
        doc_i, _ = sentence_meta[i]
        for j in range(i+1, n):
            doc_j, _ = sentence_meta[j]
            if doc_i == doc_j:
                continue  # 跳过同一文档内的句子
            sim = sim_matrix[i, j]
            if sim >= similarity_threshold:
                pairs.append({
                    'doc1': filenames[doc_i],
                    'sent1': all_sentences[i],
                    'doc2': filenames[doc_j],
                    'sent2': all_sentences[j],
                    'similarity': sim
                })

    # 4. 按相似度降序排序，取前 top_k
    pairs.sort(key=lambda x: x['similarity'], reverse=True)
    return pairs[:top_k]

def highlight_repeated_sentences(pairs: List[Dict]) -> None:
    """在控制台输出高亮的重复句子对"""
    if not pairs:
        print("✅ 未发现跨文档重复度较高的句子（阈值设定较高或内容原创性较好）。")
        return

    print("\n" + "="*60)
    print("🔍 发现重复度最高的句子对（跨文档）")
    print("="*60)
    for idx, pair in enumerate(pairs, 1):
        print(f"\n【{idx}】相似度: {pair['similarity']:.3f}")
        print(f"📄 {pair['doc1']} : {pair['sent1']}")
        print(f"📄 {pair['doc2']} : {pair['sent2']}")
    print("\n" + "="*60)

def main():
    parser = argparse.ArgumentParser(description="课程作业查重小助手")
    parser.add_argument('--dir', type=str, default='./docs',
                        help='包含待检测文档的目录 (默认: ./docs)')
    parser.add_argument('--threshold', type=float, default=0.6,
                        help='句子级相似度阈值 (默认: 0.6)')
    parser.add_argument('--top-k', type=int, default=5,
                        help='显示重复度最高的前 K 个句子对 (默认: 5)')
    args = parser.parse_args()

    # 1. 读取目录下所有支持的文件
    doc_dir = Path(args.dir)
    if not doc_dir.exists():
        print(f"❌ 目录不存在: {doc_dir}")
        sys.exit(1)

    supported_ext = ('.txt', '.docx', '.pdf')
    file_paths = [f for f in doc_dir.iterdir() if f.suffix.lower() in supported_ext]
    if not file_paths:
        print(f"❌ 在 {doc_dir} 中未找到任何 .txt/.docx/.pdf 文件")
        sys.exit(1)

    print(f"📂 发现 {len(file_paths)} 个文档:")
    for f in file_paths:
        print(f"   - {f.name}")

    # 2. 读取文本内容
    docs = []
    filenames = []
    for fpath in file_paths:
        try:
            text = read_file(str(fpath))
            docs.append(text)
            filenames.append(fpath.name)
            print(f"✅ 读取成功: {fpath.name} (字符数: {len(text)})")
        except Exception as e:
            print(f"❌ 读取 {fpath.name} 失败: {e}")
            continue

    if len(docs) < 2:
        print("❌ 至少需要 2 个有效文档才能进行查重")
        sys.exit(1)

    # 3. 计算文档级相似度
    similarity_matrix, vectorizer, tfidf_matrix = compute_document_similarity(docs)
    print("📊 文档级相似度矩阵:")
    print(similarity_matrix)

    # 4. 绘制热力图
    plot_heatmap(similarity_matrix, filenames)

    # 5. 句子级重复检测
    print("\n🔎 正在进行句子级重复检测...")
    top_pairs = find_top_sentence_pairs(
        docs, filenames,
        similarity_threshold=args.threshold,
        top_k=args.top_k
    )
    highlight_repeated_sentences(top_pairs)

    print("\n🎉 查重分析完成！")

if __name__ == "__main__":
    main()
