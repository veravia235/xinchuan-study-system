import streamlit as st
import os
from brain import SharedLocalEmbeddings, build_permanent_brain
from langchain_community.vectorstores import FAISS

st.set_page_config(page_title="新传考研总控大厅", page_icon="🏛️", layout="wide")

st.title("🎓 新传考研全能系统 [旗舰总控台]")
st.markdown("欢迎来到你的专属考研基地！请先在此处配置你的**核心大脑**，左侧的独立功能舱将全部挂载该大脑的永久记忆。")

# 全局记忆挂载
if "active_brain" not in st.session_state:
    if os.path.exists("xinchuan_brain.faiss"):
        st.session_state.active_brain = FAISS.load_local("xinchuan_brain.faiss", SharedLocalEmbeddings(), allow_dangerous_deserialization=True)
    else:
        st.session_state.active_brain = None

# 全局 API Key 保存
# 全局 API Key 保存（增加本地环境安全容错）
if "api_key" not in st.session_state:
    try:
        st.session_state.api_key = st.secrets.get("DEEPSEEK_API_KEY", "")
    except:
        st.session_state.api_key = ""

with st.sidebar:
    st.header("⚙️ 引擎核心设置")
    api_key_input = st.text_input("DeepSeek API Key:", value=st.session_state.api_key, type="password")
    if api_key_input:
        st.session_state.api_key = api_key_input
        st.success("✅ 接口已通畅")
        
    st.markdown("---")
    st.header("🧠 投喂专属资料库")
    files = st.file_uploader("将你的独家笔记拖拽至此 (PDF/DOCX/TXT)", accept_multiple_files=True)
    
    if files and st.button("🚀 启动深度解析引擎"):
        with st.spinner("正在逐字吞吐资料，构建永久神经网..."):
            success = build_permanent_brain(files)
            if success:
                st.session_state.active_brain = FAISS.load_local("xinchuan_brain.faiss", SharedLocalEmbeddings(), allow_dangerous_deserialization=True)
                st.success("🎉 记忆重构完毕！你的资料已化为 AI 的肌肉记忆！")
                st.balloons()
            else:
                st.error("解析失败，未提取到有效文本。")

if st.session_state.active_brain:
    st.success("🟢 当前状态：相当完美！专属知识库已挂载，请点击左侧边栏进入各大功能舱！")
else:
    st.info("🟡 当前状态：等待喂食。请先在左侧上传你的复习资料，再使用具体功能哦！")
    
st.markdown("---")
st.markdown("### 👈 左侧边栏已自动生成菜单，请点击进入对应功能。")