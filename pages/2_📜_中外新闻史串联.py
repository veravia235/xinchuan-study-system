import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="中外新闻史串联", page_icon="📜", layout="wide")
st.title("📜 中外新闻史时空纵横线")

base_url = "https://api.deepseek.com/v1"

if "api_key" not in st.session_state or not st.session_state.api_key:
    st.warning("⚠️ 请先回到主页配置你的 API 密钥！")
    st.stop()
if "active_brain" not in st.session_state or not st.session_state.active_brain:
    st.warning("⚠️ 请先回到主页上传你的笔记并构建记忆大脑！")
    st.stop()

st.markdown("### 🧙‍♂️ 记忆库时空重构")
st.caption("点击下方按钮，AI将精读你上传的几十万字新闻史笔记，自动抽炼出核心考点轴。")

if st.button("✨ 深度扫描私库并重构历史时空轴"):
    with st.spinner("正在横跨历史长河，打捞年份、人物与高分语料..."):
        client = OpenAI(api_key=st.session_state.api_key, base_url=base_url)
        # 专门打捞文档里的历史发展线索
matched_history = st.session_state.active_brain.similarity_search("新闻史 年份 时间 事件 意义 创办 创刊 阶段", k=40)
        h_context = "\n".join([d.page_content for d in matched_history])
        
        h_prompt = f"""请精读以下用户的新闻史笔记片段：\n{h_context}\n
        请帮我整理出至少 10 个（或更多）最硬核的历史时空卡片，覆盖各个不同时期。必须严格输出为 JSON 数组格式，不要包含任何 markdown 块或多余解释。
        期望的 JSON 格式如下：
        [
          {{"time": "年份或历史时期", "title": "报刊名或重大事件", "person": "核心历史人物", "tag": "名词解释踩分关键词", "significance": "可直接抄到论述题里的高分金句语料"}}
        ]
        纪律：行文中绝对禁止使用‘极其’一词，一律根据语境细化替换为‘非常’、‘极度’、‘十分’等表达。
        """
        try:
            res = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": h_prompt}],
                response_format={ 'type': 'json_object' }
            )
            import json
            # 兼容处理返回的 key
            res_data = json.loads(res.choices[0].message.content)
            st.session_state.dynamic_history = res_data if isinstance(res_data, list) else res_data.get("history", [])
            st.success("时空轴重构成功！相当顺利！")
        except Exception as e:
            st.error(f"历史数据抽炼失败: {e}")

st.markdown("---")

# 渲染视图
if "dynamic_history" in st.session_state and st.session_state.dynamic_history:
    st.subheader("📁 从你的资料库中自动重构出的独家历史考点轴")
    for item in st.session_state.dynamic_history:
        st.markdown(f"""
        <div style='padding: 22px; border-radius: 10px; border-left: 6px solid #c05621; background: #fffaf0; margin-bottom: 15px;'>
            <h4 style='color: #c05621; margin: 0 0 10px 0;'>⏱️ 时期/年份：{item.get('time')} | 《{item.get('title')}》</h4>
            <p style='margin: 5px 0;'><b>👤 核心人物：</b> {item.get('person')}</p>
            <p style='margin: 5px 0;'><b>⚠️ 高频名解踩分点：</b> <span style='color:#c05621; font-weight:bold;'>{item.get('tag')}</span></p>
            <p style='margin: 5px 0; background: #fff; padding: 8px; border-radius: 4px;'><b>📝 论述题高分语料金句：</b> <i>“{item.get('significance')}”</i></p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.subheader("📌 默认内置通识串联线")
    st.caption("提示：在主页上传你的笔记并点击上方按钮，此处的静态内容会被你的独家笔记直接替换。")
    
    history_mode = st.radio("切换展示视角：", ["横向时间横切（同代中外事件碰撞）", "纵向专题史脉络演进"], horizontal=True)
    if "横向" in history_mode:
        with st.expander("⏱️ 19世纪末20世纪初：中国维新改革 vs 美国商业煽情", expanded=True):
            h_col1, h_col2 = st.columns(2)
            with h_col1:
                st.markdown("#### 🇨🇳 中国：维新派办报高潮\n- **领军人物：** 梁启超、康有为\n- **核心报刊：** 《时务报》《国闻报》\n- **高频名解：** 时务文体、去塞求通、耳目喉舌论\n- **高分金句：** 开启政论报刊先河，使新闻媒介十分深刻地嵌入政治改良进程。")
            with h_col2:
                st.markdown("#### 🇺🇸 外国：黄色新闻大战\n- **领军人物：** 普利策 vs 赫斯特\n- **核心报刊：** 《世界报》vs《纽约日报》\n- **高频名解：** 黄色新闻、煽情主义、美西战争\n- **高分金句：** 展现了自由主义报业市场化走向极端的异化反思，直接催生了后来的客观性报道规范。")
    else:
        with st.expander("🔥 专题：中国共产党党报体制演进线", expanded=True):
            st.markdown("""
            1. **苏区孕育期：** 《红色中华》，奠定了密切联系群众、阶级立场鲜明的基本底色。
            2. **延安成熟期：** 1942年《解放日报》改版。**核心踩分点**：正式确立党性、群众性、战斗性、组织性四大原则。
            3. **社会主义建设探索期：** 1956年新闻工作改革。**核心踩分点**：探讨新闻规律，倡导“同栏不同音”，反公式化、教条化文风。
            """)