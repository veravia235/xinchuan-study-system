import streamlit as st
import os
import time
import json
from openai import OpenAI
from pypdf import PdfReader
import docx2txt
from langchain_community.vectorstores import FAISS
from sentence_transformers import SentenceTransformer
from sentence_transformers import TransformerEmbeddings

# ==========================================
# 0. 页面基础配置与全局 UI 质感优化
# ==========================================
st.set_page_config(page_title="新传考研5W智能学习系统", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    .stProgress .st-bo { background-color: #4CAF50; }
    .theory-card { padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; margin-bottom: 12px; background-color: #ffffff; box-shadow: 0 2px 4px rgba(0,0,0,0.02); }
    .history-box { padding: 20px; border-radius: 10px; border-left: 5px solid #c05621; background-color: #fffaf0; margin-bottom: 15px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 新传考研 5W 智能全能学习系统 [动态进化版]")
st.caption("集成 5W深度拆解、新闻史编年体、热点实战阅卷与高阶 RAG 知识感应引擎")

# ==========================================
# 1. 安全的 API 密钥获取机制 (支持云端保险箱)
# ==========================================
MY_DEEPSEEK_API_KEY = ""
try:
    MY_DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    pass

base_url = "https://api.deepseek.com/v1"

# ==========================================
# 2. 本地免流量向量化类
# ==========================================
@st.cache_resource(show_spinner=False)
def get_embeddings():
    class LocalSentenceEmbeddings(Embeddings):
        def __init__(self):
            # 采用轻量且强大的多语言模型，本地运行不耗费流量
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        def embed_documents(self, texts):
            return self.model.encode(texts).tolist()
        def embed_query(self, text):
            return self.model.encode(text).tolist()
    return LocalSentenceEmbeddings()

# 初始化全局状态机 (实现跨页面状态保持与动态进化)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "flip_state" not in st.session_state:
    st.session_state.flip_state = {}
if "custom_theory" not in st.session_state:
    st.session_state.custom_theory = None
if "custom_history" not in st.session_state:
    st.session_state.custom_history = None

# ==========================================
# 3. 侧边栏：资料库投喂与知识进化中枢
# ==========================================
with st.sidebar:
    st.header("⚙️ 系统中枢")
    if MY_DEEPSEEK_API_KEY:
        st.success("✅ 云端专属 API 密钥已自动挂载")
    else:
        st.warning("⚠️ 未检测到云端密钥")
        MY_DEEPSEEK_API_KEY = st.text_input("请临时输入 DeepSeek API Key:", type="password")
    
    st.markdown("---")
    st.header("📂 私有知识库投喂")
    st.caption("支持投喂你的历年真题、个人背诵笔记 (PDF/DOCX/TXT)")
    uploaded_files = st.file_uploader("拖拽笔记文件至此", accept_multiple_files=True)
    
    if uploaded_files and st.button("🚀 1. 解析资料并重构大脑"):
        all_text = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, f in enumerate(uploaded_files):
            status_text.text(f"正在读取: {f.name}...")
            file_text = ""
            try:
                if f.name.endswith('.pdf'):
                    pdf_reader = PdfReader(f)
                    for page in pdf_reader.pages:
                        if page.extract_text(): file_text += page.extract_text() + "\n"
                elif f.name.endswith('.docx'):
                    file_text = docx2txt.process(f)
                elif f.name.endswith('.txt'):
                    file_text = f.read().decode("utf-8")
                if file_text.strip(): all_text.append(file_text)
            except Exception as e:
                st.error(f"解析 {f.name} 失败: {e}")
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
        if all_text:
            status_text.text("正在将知识转化为语义向量...")
            chunks = []
            for text in all_text:
                for i in range(0, len(text), 300):
                    chunks.append(text[i:i+400])
            st.session_state.vector_store = FAISS.from_texts(chunks, get_embeddings())
            status_text.text("✅ 基础私有库构建完毕！")
            st.toast("资料已加载，可以开始第2步进化了！")
        else:
            status_text.text("❌ 未能提取有效文本")

    # 🔥 新增功能：让上传的资料直接进化到前端页面的核心引擎
    if st.session_state.vector_store:
        st.markdown("---")
        st.header("🧠 2. 知识动态进化")
        st.caption("让 AI 深度理解你刚才上传的笔记，并直接重构右侧的【5W表格】和【新闻史时间轴】")
        if st.button("🪄 融合资料至系统功能面"):
            if not MY_DEEPSEEK_API_KEY:
                st.error("请先填入 API Key 才能调用进化引擎！")
            else:
                with st.spinner("AI 正在深度重写系统数据，这需要小勾勒一些时间..."):
                    try:
                        client = OpenAI(api_key=MY_DEEPSEEK_API_KEY, base_url=base_url)
                        # 检索私库里最相关的学术名词与历史发展片段
                        docs = st.session_state.vector_store.similarity_search("新闻史核心时间线 传播学经典理论5W要素", k=6)
                        context = "\n".join([d.page_content for d in docs])
                        
                        prompt = f"请精读以下用户上传的复习资料片段：\n{context}\n\n" + """
                        你的任务是帮用户做高度结构化的整理。请严格输出一个 JSON 格式的对象（不要包含任何 markdown 块或多余解释）。
                        期望格式如下：
                        {
                          "theories": {
                            "从资料提取的硬核理论名": {
                              "5w": ["Who控制分析","Says What内容分析","In Which Channel媒介分析","To Whom受众分析","With What Effect效果分析"],
                              "clues": ["核心挖空背诵线索1","核心挖空背诵线索2","核心挖空背诵线索3"]
                            }
                          },
                          "history": [
                            {"time": "年份/时期", "title": "事件/报刊名", "person": "核心人物", "tag": "高频核心名词解释踩分点", "significance": "直接抄到论述题的高分金句语料"}
                          ]
                        }
                        注意：抽取出的内容必须完全基于资料，如果没有，可以根据新传考研通识进行专业补全。纪律：行文中绝对禁止使用‘极其’一词，一律替换为‘非常’、‘极度’、‘十分’等。
                        """
                        response = client.chat.completions.create(
                            model="deepseek-chat",
                            messages=[{"role": "user", "content": prompt}],
                            response_format={ 'type': 'json_object' }
                        )
                        
                        res_json = json.loads(response.choices[0].message.content)
                        if "theories" in res_json and res_json["theories"]:
                            st.session_state.custom_theory = res_json["theories"]
                        if "history" in res_json and res_json["history"]:
                            st.session_state.custom_history = res_json["history"]
                            
                        st.success("🎉 系统进化成功！功能页面已装载你的独家笔记！")
                        st.balloons()
                    except Exception as e:
                        st.error(f"提取融合失败，可能网络波动，请重试: {e}")

# ==========================================
# 4. 默认内置的基础数据库 (未上传资料时显示)
# ==========================================
DEFAULT_THEORIES = {
    "议程设置理论": {
        "5w": ["麦库姆斯/肖 (延续控制分析)", "媒介议程影响公众议程 (属性/网络议程)", "传统大众媒介->算法分发时代", "非完全被动受众，认知受框架限制", "认知层面的强效果论复兴"],
        "clues": ["源于李普曼的‘拟态环境’概念", "基本观点是媒介不能决定人们怎么想，但能决定人们想什么", "第二层侧重属性属性议程，第三层侧重网络议程建构"]
    },
    "沉默的螺旋": {
        "5w": ["诺尔-诺依曼 (社会心理学)", "优势意见的扩大与劣势意见的隐藏", "大众传播的复调性、累积性与遍在性", "害怕孤立的受众 (准感官统计)", "舆论的社会控制机制生成"],
        "clues": ["微观基础是人类趋同行为与害怕孤立的心理", "大众媒介营造出双重意见气候，诱发螺旋式沉默", "互联网时代由于匿名性与温床效应，常出现中坚分子引发的反向螺旋"]
    }
}

# ==========================================
# 5. 主界面布局：四大旗舰模块舱 (Tabs)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 5W 连贯带背", 
    "📜 新闻史编年体", 
    "🔥 热点题库实战", 
    "🤖 专属 AI 导师"
])

# ------------------------------------------
# Tab 1: 5W 连贯带背舱 (支持动态接管)
# ------------------------------------------
with tab1:
    st.header("🧠 模块化理论拆解与连贯带背")
    
    # 动态切换数据源：如果用户合成了私库知识，优先展示私库理论
    current_source = st.session_state.custom_theory if st.session_state.custom_theory else DEFAULT_THEORIES
    
    selected_theory = st.selectbox("选择今天攻克的理论内核：", list(current_source.keys()))
    
    st.subheader("🧭 5W 全景拓扑视图")
    t_data = current_source[selected_theory]["5w"]
    cols = st.columns(5)
    labels = ["Who (控制分析)", "Says What (内容分析)", "In Which Channel (媒介)", "To Whom (受众分析)", "With What Effect (效果)"]
    for i in range(5):
        cols[i].markdown(f"<div class='theory-card'><b>{labels[i]}</b><br/><br/><small>{t_data[i]}</small></div>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("⛓️ 逻辑链条挖空带背 (主动召回训练)")
    st.info("💡 看着下面的核心线索，尝试在脑海中还原完整的专业话语表述。")
    
    clues = current_source[selected_theory]["clues"]
    for idx, clue in enumerate(clues):
        col_btn, col_txt = st.columns([1, 9])
        btn_key = f"clue_{selected_theory}_{idx}"
        if btn_key not in st.session_state.flip_state:
            st.session_state.flip_state[btn_key] = False
            
        with col_btn:
            if st.button("👁️ 显 / 隐", key=f"btn_{btn_key}"):
                st.session_state.flip_state[btn_key] = not st.session_state.flip_state[btn_key]
                st.rerun()
        with col_txt:
            if st.session_state.flip_state[btn_key]:
                st.success(clue)
            else:
                st.warning("🔒 核心得分关键词已被遮挡，请默背冲关...")

# ------------------------------------------
# Tab 2: 新闻史编年体纵横线 (支持动态接管)
# ------------------------------------------
with tab2:
    st.header("🕰️ 中外新闻史高分串联体系")
    
    if st.session_state.custom_history:
        st.subheader("📁 从你的资料库中自动重构出的独家历史考点轴")
        for item in st.session_state.custom_history:
            with st.container():
                st.markdown(f"""
                <div class='history-box'>
                    <h4>⏱️ 时期/年份：{item.get('time', '未知')} | 《{item.get('title', '未命名事件')}》</h4>
                    <p><b>👤 核心人物：</b> {item.get('person', '暂无')}</p>
                    <p><b>⚠️ 高频名解踩分点：</b> <span style='color:#c05621; font-weight:bold;'>{item.get('tag', '暂无')}</span></p>
                    <p><b>📝 论述题高分语料金句：</b> <i>“{item.get('significance', '暂无')}”</i></p>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.subheader("📌 默认内置通识串联线 (上传并融合私库笔记可直接替换此处)")
        history_mode = st.radio("切换展示视角：", ["横向时间横切（同代中外事件碰撞）", "纵向专题史脉络演进"], horizontal=True)
        
        if "横向" in history_mode:
            with st.expander("⏱️ 19世纪末20世纪初：中国维新改革 vs 美国商业煽情", expanded=True):
                h_col1, h_col2 = st.columns(2)
                h_col1.markdown("#### 🇨🇳 中国：维新派办报高潮\n- **领军人物：** 梁启超、康有为\n- **核心报刊：** 《时务报》《国闻报》\n- **高频名解：** 时务文体、去塞求通、耳目喉舌论\n- **高分金句：** 开启政论报刊先河，使新闻媒介深度嵌入政治改良改良进程。")
                h_col2.markdown("#### 🇺🇸 外国：黄色新闻大战\n- **领军人物：** 普利策 vs 赫斯特\n- **核心报刊：** 《世界报》vs《纽约日报》\n- **高频名解：** 黄色新闻、煽情主义、美西战争\n- **高分金句：** 展现了自由主义报业市场化走向极端的异化反思，直接催生了后来的客观性报道规范。")
        else:
            with st.expander("🔥 专题：中国共产党党报体制演进线", expanded=True):
                st.markdown("""
                1. **苏区孕育期：** 《红色中华》，奠定了密切联系群众、阶级立场鲜明的基本底色。
                2. **延安成熟期：** 1942年《解放日报》改版。**核心踩分点**：正式确立党性、群众性、战斗性、组织性四大原则。
                3. **社会主义建设探索期：** 1956年新闻工作改革。**核心踩分点**：探讨新闻规律，倡导“同栏不同音”，反公式化、教条化文风。
                """)

# ------------------------------------------
# Tab 3: 热点题库与 AI 智能判卷
# ------------------------------------------
with tab3:
    st.header("⚔️ 实时时事舆论场 × 三大题型解剖室")
    hot_topics = ["AI大模型技术引发的‘数字拟态环境’真相危机", "微短剧下沉市场背后的‘情感劳动’与用户成瘾心理", "网红塌房舆论事件中的‘群体极化’与情感动员机制"]
    current_hot = st.selectbox("选择本周重点防御的焦点热点：", hot_topics)
    
    st.markdown("### 📝 题型自动化转换效果")
    t1, t2, t3 = st.columns(3)
    t1.error("🔥 【名词解释转化】\n请阐释该热点中的底层概念核心。要求150字，精准击中采分点词组。")
    t2.warning("🔥 【简答题转化】\n请简述该现象的产生机制及背后多方主体的利益合谋。要求分点作答。")
    t3.success("🔥 【论述题转化】\n结合马克思主义新闻观、批判学派异化视角，论述该现象的现实危害及治理路径。")
    
    st.markdown("---")
    st.markdown("### 🧑‍⚖️ 严苛阅卷官全真模拟系统")
    student_ans = st.text_area("在此粘贴或撰写你的大纲/全文（接受考研标准审判）：", height=150, placeholder="例如：首先，该热点反映了算法黑箱对公众认知阶层的精准建构……")
    
    if st.button("提交答卷进行机器判分"):
        if not MY_DEEPSEEK_API_KEY:
            st.error("密钥缺失，阅卷官拒绝阅卷。")
        elif len(student_ans) < 15:
            st.warning("字数严重不足，请认真对待考场模拟！")
        else:
            with st.spinner("阅卷组正在从站位、学术深度、案例贴切度多维度阅卷..."):
                try:
                    client = OpenAI(api_key=MY_DEEPSEEK_API_KEY, base_url=base_url)
                    prompt = f"请作为新闻传播学考研专业课阅卷组长，针对热点【{current_hot}】，评判考生的作答：\n{student_ans}\n评判标准：1.给出满分30分下的明确得分；2.指出缺少哪些核心高分专业词汇；3.给出一份可供直接背诵的高分示范大纲。必须使用细化梯度的表达替换‘极其’。"
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.markdown("### 📋 官方详细判卷报告")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"阅卷官罢工，调用失败: {e}")

# ------------------------------------------
# Tab 4: 专属 AI RAG 问答导师
# ------------------------------------------
with tab4:
    st.header("🤖 全能型 AI 问答与私库抽题大厅")
    ai_mode = st.radio("配置导师执教风格：", ["☕ 围炉煮茶 (温和基础答疑)", "🌪️ 苏格拉底风暴 (多轮连环追问，逼迫思考)", "🎯 私库魔鬼突击抽题 (基于你解析过的资料)"], horizontal=True)
    
    st.write("---")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])
            
    u_input = st.chat_input("向导师发问，或者配合语音输入进行回答...")
    u_audio = st.audio_input("Or 开启麦克风，直接进行语音背诵/提问：")
    
    final_query = u_input if u_input else ("【收到语音提问，请结合上下文以及私有库进行学术质询或反馈】" if u_audio else "")
    
    if final_query:
        if not MY_DEEPSEEK_API_KEY:
            st.error("尚未配置系统密钥，AI 导师处于离线状态。")
        else:
            with st.chat_message("user"): st.write(final_query)
            st.session_state.messages.append({"role": "user", "content": final_query})
            
            # 高阶 RAG 混合检索
            context_str = ""
            if st.session_state.vector_store and ("私库" in ai_mode or "煮茶" in ai_mode):
                docs = st.session_state.vector_store.similarity_search(final_query, k=3)
                if docs:
                    with st.expander("🔍 关联到的本地私库核心线索源 (RAG)"):
                        for idx, d in enumerate(docs): st.caption(f"片段 {idx+1}: {d.page_content}")
                    context_str = "\n【必须参考的用户个人笔记片段如下】:\n" + "\n".join([d.page_content for d in docs])
            elif "私库" in ai_mode and not st.session_state.vector_store:
                st.warning("你还未在左侧边栏成功上传并解析文件，系统会自动退回至通用答疑状态。")
                
            # 严格组织 System Prompt
            sys_prompt = "你是辅导新传考研的资深导师。分析理论必须熟练应用 5W 框架。彻底禁用‘极其’一词，视语境使用‘非常’‘十分’‘相当’‘极度’等。"
            if "苏格拉底" in ai_mode:
                sys_prompt += "不要直接给正确答案，请每次只抛出一个带有漏洞或更深层的学术疑问，一步步榨干用户的思考。"
            elif "私库" in ai_mode:
                sys_prompt += "你是最严厉的监考官，请根据【必须参考的用户笔记片段如下】中包含的知识点，随机挑选考点，以充满压迫感的口吻对用户进行抽题或者改错。"
                
            payload = [{"role": "system", "content": sys_prompt + context_str}]
            payload.extend(st.session_state.messages[-6:]) # 保持 6 轮对话流
            
            try:
                client = OpenAI(api_key=MY_DEEPSEEK_API_KEY, base_url=base_url)
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
                st.session_state.messages.append({"role": "assistant", "content": reply})
            except Exception as e:
                st.error(f"连接 DeepSeek 发生阻碍: {e}")
