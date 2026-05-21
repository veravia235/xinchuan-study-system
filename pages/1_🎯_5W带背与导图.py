import streamlit as st
import os
from openai import OpenAI
from brain import search_full_brain
import json

st.set_page_config(page_title="5W带背与导图", page_icon="🎯", layout="wide")
st.title("🎯 5W 连贯带背与思维重构")

base_url = "https://api.deepseek.com/v1"

if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("⚠️ 请先回到主页配置你的 DeepSeek API 密钥！")
    st.stop()

if not os.path.exists("xinchuan_brain_text.json"):
    st.warning("⚠️ 请先回到主页上传你的笔记并构建记忆大脑！")
    st.stop()

theory_select = st.text_input("请输入你今天想攻克的考点（比如：议程设置理论、技术决定论）：")

if st.button("🧠 从我的整本笔记中打捞并拆解"):
    if not theory_select:
        st.warning("请输入考点名称！")
    else:
        with st.spinner(f"正在全库检索【{theory_select}】的最新论述..."):
            client = OpenAI(api_key=st.session_state.api_key, base_url=base_url)
            context = search_full_brain(theory_select, limit=30)
            
            prompt = f"""你是一位十分严苛的新传考研顶级名师。请阅读以下从用户笔记中捞出的参考碎片：\n{context}\n
            请用 5W 框架对【{theory_select}】进行深度【考点级拆解】。
            
            【严厉警告：拒绝敷衍】：
            1. 内容必须极度厚重！每个 W 下面的内容不能只有一两句话，必须包含背景、核心观点、优缺点评价，字数要足以支撑一道简答题。
            2. 【关键指令】：如果提供的资料碎片不够详细，你必须立刻调用你作为大模型的全量新传专业知识进行【深度补充与扩展】！绝不能以“资料缺失”为由敷衍！
            3. 提取并加粗核心踩分点（专业名词）。
            4. 行文中绝对禁止使用‘极其’一词，一律视语境替换为‘非常’、‘极度’、‘十分’等。
            
            输出为 JSON 格式，严格包含 "Who", "What", "Channel", "Whom", "Effect" 五个键。
            """
            
            try:
                res = client.chat.completions.create(
                    model="deepseek-chat",
                    messages=[{"role": "user", "content": prompt}],
                    response_format={ 'type': 'json_object' }
                )
                res_data = json.loads(res.choices[0].message.content)
                
                st.success("🎉 全库检索与拆解完成！")
                st.markdown("### 🧩 5W 核心知识图谱")
                st.info(f"**👤 控制研究 (Who):** {res_data.get('Who', '无')}")
                st.info(f"**📝 内容分析 (Says What):** {res_data.get('What', '无')}")
                st.info(f"**📺 媒介分析 (In Which Channel):** {res_data.get('Channel', '无')}")
                st.info(f"**👥 受众分析 (To Whom):** {res_data.get('Whom', '无')}")
                st.info(f"**💥 效果分析 (With What Effect):** {res_data.get('Effect', '无')}")
                
            except Exception as e:
                st.error(f"拆解失败，请重试: {e}")