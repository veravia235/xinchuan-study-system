import streamlit as st
import os
import json
from brain import build_permanent_brain

st.set_page_config(page_title="新传考研总控大厅", page_icon="🏛️", layout="wide")

st.title("🎓 新传考研全能系统 [智存旗舰版]")
st.markdown("欢迎回来！系统已成功升级：**支持密钥本地自动记住** 与 **已投喂文档全景看板**。")

CONFIG_FILE = "config.json"
BRAIN_FILE = "xinchuan_brain_text.json"

# 1. 自动化本地配置管理（用于记住 API Key）
def load_local_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_local_config(api_key):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump({"api_key": api_key}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"本地保存配置失败: {e}")

# 加载本地保存的钥匙
local_config = load_local_config()

if "api_key" not in st.session_state:
    st.session_state.api_key = local_config.get("api_key", "")

if "brain_loaded" not in st.session_state:
    st.session_state.brain_loaded = os.path.exists(BRAIN_FILE)

# 2. 侧边栏：核心控制台
with st.sidebar:
    st.header("⚙️ 核心大脑配置")
    # 只要本地存过，这里启动时会自动填好，无需再次动手
    api_key_input = st.text_input("DeepSeek API Key:", value=st.session_state.api_key, type="password")
    
    if api_key_input != st.session_state.api_key:
        st.session_state.api_key = api_key_input
        save_local_config(api_key_input)  # 触发输入改变时自动存入硬盘
        st.success("💾 密钥已安全保存到本地，下次启动无需重复填写！")

    if st.session_state.api_key:
        st.success("✅ DeepSeek 思考引擎已就绪")
        
    st.markdown("---")
    st.header("📂 永久投喂资料库（完全免费）")
    st.caption("新上传的资料会追加合并到你的专属本地库中。")
    files = st.file_uploader("拖拽考研笔记至此 (PDF/DOCX)", accept_multiple_files=True)
    
    if files and st.button("🚀 启动零成本全量通读"):
        with st.spinner("正在以十倍速全量扫描重构你的文档..."):
            success = build_permanent_brain(files)
            if success:
                st.session_state.brain_loaded = True
                st.success("🎉 重构完毕！新知识已成功固化！")
                st.rerun()
            else:
                st.error("解析失败，未提取到有效文本。")

# 3. 主界面：当前状态与文档足迹记录看板
if st.session_state.brain_loaded:
    st.success("🟢 当前状态：专属知识库已自动装载，请点击左侧边栏进入各大功能舱！")
    
    st.markdown("### 📋 本地数据库已加载的考研文档清单")
    st.caption("以下是系统目前已经深度记住并格式化的文件。在左侧侧边栏上传新文件会继续累加。")
    
    try:
        with open(BRAIN_FILE, "r", encoding="utf-8") as f:
            database = json.load(f)
            # 地毯式扫描提取库里所有不重复的文件来源
            uploaded_docs = list(set([item.get("source", "未知文档") for item in database]))
            
        if uploaded_docs:
            # 用优雅的列表展示出所有的文件，让你清清楚楚知道读了哪些
            for idx, doc_name in enumerate(uploaded_docs):
                st.markdown(f"**📄 文档 {idx+1}：** `{doc_name}`")
            
            # 提供一个一键重置的功能，方便换科目复习
            st.markdown("---")
            if st.button("🗑️ 清空所有本地文档记录（清空知识库）"):
                if os.path.exists(BRAIN_FILE):
                    os.remove(BRAIN_FILE)
                st.session_state.brain_loaded = False
                st.success("本地库已成功清空，正在重置大厅...")
                st.rerun()
        else:
            st.info("库里目前没有记录，请在左侧上传资料。")
    except Exception as e:
        st.error(f"读取文档清单时发生阻碍: {e}")
        
else:
    st.info("🟡 当前状态：等待激活。请先在左侧输入 DeepSeek Key 并上传你的考研笔记。")