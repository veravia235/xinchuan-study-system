import streamlit as st
import os
from openai import OpenAI
from brain import search_full_brain

st.set_page_config(page_title="热点题库与阅卷", page_icon="🔥", layout="wide")
st.title("⚔️ 实时时事舆论场 × 阅卷解剖室")

base_url = "https://api.deepseek.com/v1"

# 1. 检测思考引擎
if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("⚠️ 请先回到主页配置你的 DeepSeek API 密钥！")
    st.stop()

# 2. 核心修复：直接读取本地永久库，绝不让用户重复上传！
if not os.path.exists("xinchuan_brain_text.json"):
    st.warning("⚠️ 知识库未找到！请回主页上传一次笔记，系统会自动永久保存。")
    st.stop()

hot_topics = [
    "AI大模型技术与深度伪造引发的认知危机", 
    "微短剧下沉市场背后的情感劳动与成瘾", 
    "网红塌房舆论事件中的群体极化与网络私刑"
]
current_hot = st.selectbox("选择本周重点防御的时事热点：", hot_topics)

st.markdown("### 🧑‍⚖️ 严苛阅卷官全真模拟")
student_ans = st.text_area("在此粘贴或撰写你的作答（接受考研标准审判）：", height=200)

if st.button("提交答卷进行机器判分"):
    if len(student_ans.strip()) < 15:
        st.warning("字数严重不足，请认真对待考场模拟！")
    else:
        with st.spinner("正在从你的整本笔记中调阅相关理论，进行严苛比对判卷..."):
            # 从本地永久库中打捞理论依据，阅卷更有底气
            ref_context = search_full_brain(current_hot, limit=20)
            
            prompt = f"""你是新传考研专业课阅卷组长。请针对热点【{current_hot}】，评判考生的作答：
            【考生作答】：{student_ans}
            【你的评分参考（来自用户的本地笔记资料）】：{ref_context}
            
            要求：
            1. 给出满分30分下的明确得分。
            2. 指出考生漏掉了哪些核心的高分专业词汇（必须结合提供的参考资料提取）。
            3. 给出一段可供直接背诵的高分示范大纲。
            4. 纪律：行文中绝对禁止使用‘极其’一词，一律替换为‘非常’、‘极度’、‘十分’等。
            """
            try:
                client = OpenAI(api_key=st.session_state.api_key, base_url=base_url)
                response = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}]
                )
                st.markdown("### 📋 官方详细判卷报告")
                st.write(response.choices[0].message.content)
            except Exception as e:
                st.error(f"阅卷官罢工，调用失败: {e}")