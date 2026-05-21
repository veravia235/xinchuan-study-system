import os
import streamlit as st
from pypdf import PdfReader
import docx2txt
import json

BRAIN_FILE = "xinchuan_brain_text.json"

def build_permanent_brain(uploaded_files):
    """【本地记忆追加版】通读新文件，并与原有的本地永久库无缝合并，绝不覆盖旧记录"""
    all_chunks = []
    existing_sources = set()
    
    # 1. 优先读取已经存在的历史文档记录
    if os.path.exists(BRAIN_FILE):
        try:
            with open(BRAIN_FILE, "r", encoding="utf-8") as f:
                all_chunks = json.load(f)
                # 记录已经存在的文件名，防止重复投喂同一份文件导致数据污染
                existing_sources = set([item.get("source", "") for item in all_chunks])
        except:
            all_chunks = []

    new_file_loaded = False
    
    # 2. 开始解析新上传的文件
    for f in uploaded_files:
        # 如果文件名已经存在于历史记录中，自动跳过，相当智能
        if f.name in existing_sources:
            st.sidebar.warning(f" Let's Go! 【{f.name}】已在档案库记录中，无需重复解析。")
            continue
            
        file_text = ""
        try:
            if f.name.endswith('.pdf'):
                pdf_reader = PdfReader(f)
                for page in pdf_reader.pages:
                    txt = page.extract_text()
                    if txt: file_text += txt + "\n"
            elif f.name.endswith('.docx'):
                file_text = docx2txt.process(f)
            elif f.name.endswith('.txt'):
                file_text = f.read().decode("utf-8")
            
            if file_text.strip():
                paragraphs = [p.strip() for p in file_text.split('\n') if len(p.strip()) > 10]
                for p in paragraphs:
                    all_chunks.append({"source": f.name, "content": p})
                new_file_loaded = True
        except Exception as e:
            st.error(f"研读【{f.name}】失败: {e}")
            
    if not new_file_loaded and len(uploaded_files) > 0:
        return True
        
    if not all_chunks:
        return False

    # 💾 安全写回本地 JSON 档案库，刷新网页或重启系统绝不丢失
    with open(BRAIN_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False, indent=2)
    return True

def search_full_brain(query, limit=50):
    """【精准定位打捞】扫描整本笔记，将来源文件与原文内容完美打包组合"""
    if not os.path.exists(BRAIN_FILE):
        return ""
    
    with open(BRAIN_FILE, "r", encoding="utf-8") as f:
        database = json.load(f)
        
    keywords = [k for k in query.split() if len(k) > 0]
    if not keywords:
        keywords = [query]
        
    matched_p = []
    for item in database:
        text = item["content"]
        source = item.get("source", "未知文件")
        if any(kw.lower() in text.lower() for kw in keywords):
            matched_p.append(f"【文件源：{source}】 原文内容：{text}")
            if len(matched_p) >= limit:
                break
                
    if len(matched_p) < 5 and database:
        matched_p = [f"【文件源：{item.get('source', '未知文件')}】 原文内容：{item['content']}" for item in database[:40]]
        
    return "\n\n".join(matched_p)