import os
import streamlit as st
from pypdf import PdfReader
import docx2txt
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

# 建立一个稳定、本地免流的语义向量转化器
class SharedLocalEmbeddings(Embeddings):
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()
    def embed_query(self, text):
        return self.model.encode(text).tolist()

def build_permanent_brain(uploaded_files, chunk_size=500):
    """深度研读文档，并转化为可以永久保存的 FAISS 向量库"""
    all_text = []
    for f in uploaded_files:
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
            elif f.name.endswith('.doc'):
                st.warning(f"⚠️ 拦截提示：发现老旧的 .doc 文件【{f.name}】，系统仅支持新版 .docx 或 PDF，请另存为后重试。")
                continue
            
            if file_text.strip():
                all_text.append(f"--- 来源文件: {f.name} ---\n" + file_text)
        except Exception as e:
            st.error(f"研读【{f.name}】时受阻: {e}")
            
    if not all_text:
        return False

    # 重叠切片算法，确保上下文语意不断裂
    chunks = []
    combined_raw = "\n".join(all_text)
    for i in range(0, len(combined_raw), chunk_size - 100):
        chunks.append(combined_raw[i:i+chunk_size])
        
    embeddings = SharedLocalEmbeddings()
    vector_store = FAISS.from_texts(chunks, embeddings)
    
    # 💾 永久保存在本地，生成记忆文件
    vector_store.save_local("xinchuan_brain.faiss")
    return True