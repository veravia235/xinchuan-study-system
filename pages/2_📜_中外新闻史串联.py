import streamlit as st
from openai import OpenAI
import json

st.set_page_config(page_title="中外新闻史串联", page_icon="📜", layout="wide")
st.title("📜 中外新闻史时空纵横线")

base_url = "https://api.deepseek.com/v1"

# 检查权限与大脑
if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("⚠️ 请先回到主页配置你的 API 密钥！")
    st.stop()
if "active_brain" not in st.session_state or not st.session_state.active_brain:
    st.warning("⚠️ 请先回到主页上传你的笔记并构建记忆大脑！")
    st.stop()

st.markdown("### 🧙‍♂️ 记忆库时空重构")
st.caption("点击下方按钮，AI将精读你上传的笔记，自动抽炼出核心考点轴。")

if st.button("✨ 深度扫描私库并重构历史时空轴"):
    with st.spinner("正在横跨历史长河，打捞年份、人物与高分语料..."):
        client = OpenAI(api_key=st.session_state.api_key, base_url=base_url)
        # 深度检索：打捞文档里的历史发展线索 (k=40 表示拉满检索，获取更全内容)
        matched_history = st.session_state.active_brain.similarity_search("新闻史 年份 时间 事件 意义 创办 创刊 阶段", k=40)
        h_context = "\n".join([d.page_content for d in matched_history])
        
        h_prompt = f"""请精读以下用户的新闻史笔记片段：\n{h_context}\n
        请帮我整理出至少10个最硬核的历史时空卡片。必须严格输出为 JSON 数组格式，不要包含任何 markdown 块或多余解释。
        期望的 JSON 格式如下：
        [
          {{"time": "年份或时期", "title": "事件/报刊", "person": "核心人物", "tag": "名解踩分点", "significance": "论述题金句"}}
        ]
        纪律：禁止使用‘极其’一词，一律根据语境细化替换为‘非常’、‘极度’、‘十分’等表达。
        """
        try:
            res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": h_prompt}],
                response_format={ 'type': 'json_object' }
            )
            res_content = res.choices[0].message.content
            # 处理可能的 json 嵌套
            res_data = json.loads(res_content)
            st.session_state.dynamic_history = res_data if isinstance(res_data, list) else res_data.get("history", [])
            st.success("时空轴重构成功！")
        except Exception as e:
            st.error(f"历史数据抽炼失败: {e}")

st.markdown("---")

# 渲染视图
if "dynamic_history" in st.session_state and st.session_state.dynamic_history:
    st.subheader("📁 从你的资料库中自动重构出的独家历史考点轴")
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
    st.info("👈 请在上方点击按钮，让 AI 深度解析你的笔记。")