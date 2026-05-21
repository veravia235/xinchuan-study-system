import streamlit as st
from openai import OpenAI
import os
from brain import search_full_brain
import json

st.set_page_config(page_title="全能AI导师", page_icon="🤖", layout="wide")
st.title("🤖 你的专属温和 AI 导师")

base_url = "https://api.deepseek.com/v1"

if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("⚠️ 请先回到主页配置你的 API 密钥！")
    st.stop()

if not os.path.exists("xinchuan_brain_text.json"):
    st.warning("⚠️ 发现你的私库尚未挂载，请先回主页上传笔记！")
    st.stop()

# 获取当前已解析的文件清单
file_list_str = "未知文件"
try:
    with open("xinchuan_brain_text.json", "r", encoding="utf-8") as f:
        db = json.load(f)
        filenames = list(set([item.get("source", "未知文件") for item in db]))
        file_list_str = "、".join(filenames)
except:
    pass

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "wrong_pool" not in st.session_state:
    st.session_state.wrong_pool = []

ai_mode = st.radio("配置导师执教风格：", [
    "☕ 围炉煮茶 (温和基础答疑与陪伴)", 
    "🍃 循循善诱 (温和启发思考)", 
    "🎯 考点温和突击 (基于笔记进行查漏补缺)"
], horizontal=True)

st.markdown("---")

for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

u_input = st.chat_input("向导师发问，或者回答导师的抽题...")

try:
    u_audio = st.audio_input("Or 开启麦克风，直接进行背诵/提问：")
except AttributeError:
    u_audio = None

final_query = u_input if u_input else ("【收到用户的语音输入，请结合私有库温和解答】" if u_audio else "")

if final_query:
    with st.chat_message("user"):
        st.write(final_query)
    st.session_state.chat_messages.append({"role": "user", "content": final_query})
    
    rag_context = ""
    rag_context_text = search_full_brain(final_query, limit=20)
    
    if rag_context_text:
        with st.expander("🔍 导师正在调阅的私库核心线索"):
            st.caption(rag_context_text[:300] + "......(已截断展示)")
        rag_context = "\n【用户个人笔记参考素材（包含文件源和原文）如下】:\n" + rag_context_text
            
    # 🌟 核心提效提示词：彻底丢弃大标题，改用正常交谈，严格指出文件出处
    sys_prompt = f"""你是一位十分资深、温和且具有高度同理心的新传考研辅导学长。
    
    【核心交互纪律——拒绝死板，自然的AI对答】：
    1. 必须使用【自然的AI对话语气】进行交谈，像朋友聊天一样娓娓道来。
    2. 【绝对禁止】总是输出“### 级大标题”、“1. 2. 3.”等生硬、啰嗦的列表分段结构。直接用段落把话连贯地讲清楚。
    3. 语言要精炼、透彻，直接击中核心，把理论或历史的来龙去脉讲得非常明白。
    4. 【铁律：必须精准指出出处】：在回答时，只要引用或参考了用户笔记的内容，必须在对话中明确指出。格式要求如：“这句话在你的【xxx文件】里有提及，原文第几处写到……”。必须点出具体的文件名和对应的原文句子供用户核对。
    
    挂载在本地的文件清单有：【{file_list_str}】。
    """
    
    if "循循善诱" in ai_mode:
        sys_prompt += "请多用启发性的方式温柔引导，不要给枯燥的板书。"
    elif "突击" in ai_mode:
        sys_prompt += "请根据素材随机抽取考点提问，并温柔纠错。"
        
    sys_prompt += "纪律要求：行文中绝对禁止使用‘极其’一词，视具体情况更改为‘非常’、‘相当’、‘很是’、‘极度’、‘十分’等。"

    payload = [{"role": "system", "content": sys_prompt + rag_context}]
    payload.extend(st.session_state.chat_messages[-6:])
    
    try:
        client = OpenAI(api_key=st.session_state.api_key, base_url=base_url)
        with st.chat_message("assistant"):
            box = st.empty()
            reply = ""
            res_stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=payload,
                stream=True
            )
            for chunk in res_stream:
                if chunk.choices[0].delta.content:
                    reply += chunk.choices[0].delta.content
                    box.markdown(reply + "▌")
            box.markdown(reply)
            
        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        
        if "漏掉" in reply or "不准确" in reply or "错误" in reply or "补充" in reply:
            st.session_state.wrong_pool.append(final_query)
            
    except Exception as e:
        st.error(f"连接 AI 导师发生阻碍: {e}")