import streamlit as st
import os
from openai import OpenAI
from brain import search_full_brain
import json

st.set_page_config(page_title="中外新闻史串联", page_icon="📜", layout="wide")
st.title("📜 中外新闻史时空纵横线")

base_url = "https://api.deepseek.com/v1"

if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("⚠️ 请先回到主页配置你的 DeepSeek API 密钥！")
    st.stop()
if not os.path.exists("xinchuan_brain_text.json"):
    st.warning("⚠️ 请先回到主页上传你的笔记并构建记忆大脑！")
    st.stop()

st.markdown("### 🧙‍♂️ 记忆库时空重构")
st.caption("点击下方按钮，AI将开启地毯式打捞，绝不遗漏任何年份考点。")

if st.button("✨ 启动全库地毯式检索 (深度重构)"):
    with st.spinner("正在从整本笔记中地毯式捞取历史发展线索..."):
        h_context = search_full_brain("新闻史 年份 时间 事件 创办 创刊 阶段 发展 历史", limit=50)
        
        h_prompt = f"""你现在是顶级新传考研导师。请执行【严谨的历史时空轴重构】。
        阅读以下打捞出的所有历史素材碎片：\n{h_context}\n
        
        【严厉警告：拒绝错乱与短小】：
        1. 必须按真实发生的【先后时间顺序】严格排列，绝不允许时间线错乱！
        2. 拒绝残缺！至少输出 15 到 25 个重大节点。如果提供的素材有断层或语焉不详，请动用你的专业新传知识库进行考研级别的【自动补全】。
        3. 每个节点的“名解踩分点”和“论述题金句”必须详实饱满（不少于80字），直接给出满分作答标准，绝对不能只写一句废话。
        4. 行文中绝对禁止使用‘极其’一词，一律视语境替换为‘非常’、‘极度’、‘十分’等。
        
        【输出格式】：严格的 JSON 数组。
        [
          {{"time": "真实的历史年份/时期（如1840年）", "title": "事件/报刊", "person": "核心人物", "tag": "详细饱满的名解踩分点", "significance": "长篇论述题高分语料金句"}}
        ]
        """
        try:
            client = OpenAI(api_key=st.session_state.api_key, base_url=base_url)
            res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": h_prompt}],
                response_format={ 'type': 'json_object' }
            )
            res_data = json.loads(res.choices[0].message.content)
            
            if isinstance(res_data, list):
                st.session_state.dynamic_history = res_data
            else:
                for key, value in res_data.items():
                    if isinstance(value, list):
                        st.session_state.dynamic_history = value
                        break
            st.success("🎉 全景高密度时空轴重构成功！")
        except Exception as e:
            st.error(f"深度挖掘失败: {e}")

st.markdown("---")

if "dynamic_history" in st.session_state and st.session_state.dynamic_history:
    st.subheader("📁 从你的整本资料库中榨干出的高密度时空轴")
    for item in st.session_state.dynamic_history:
        st.markdown(f"""
        <div style='padding: 22px; border-radius: 10px; border-left: 6px solid #c05621; background: #fffaf0; margin-bottom: 15px;'>
            <h4 style='color: #c05621; margin: 0 0 10px 0;'>⏱️ 时期/年份：{item.get('time', '未知')} | 《{item.get('title', '未知')}》</h4>
            <p style='margin: 5px 0;'><b>👤 核心人物：</b> {item.get('person', '无')}</p>
            <p style='margin: 5px 0;'><b>⚠️ 高频名解踩分点：</b> <span style='color:#c05621; font-weight:bold;'>{item.get('tag', '无')}</span></p>
            <p style='margin: 5px 0; background: #fff; padding: 8px; border-radius: 4px;'><b>📝 论述题高分语料金句：</b> <i>“{item.get('significance', '无')}”</i></p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("👈 请在左侧侧边栏投喂笔记后，点击上方按钮开启地毯式扫描。")