import streamlit as st
import os
import time
from openai import OpenAI
from pypdf import PdfReader
import docx2txt
from langchain_community.vectorstores import FAISS
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer

# ==========================================
# 0. 页面基础配置与全局 CSS 优化
# ==========================================
st.set_page_config(page_title="新传考研5W智能学习系统", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

# 自定义 CSS 让界面更有质感
st.markdown("""
    <style>
    .stProgress .st-bo { background-color: #4CAF50; }
    .theory-card { padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🎓 新传考研 5W 智能全能学习系统 [旗舰版]")
st.caption("集成 5W深度拆解、新闻史编年体、热点实战阅卷与高阶 RAG 私有资料库导师")

# ==========================================
# 1. 安全的 API 密钥获取机制
# ==========================================
# 逻辑：先尝试从 Streamlit 云端的 Secrets 读取。如果没有，再让用户手动输入。
# 这样在本地你可以手动输，部署到云端后会自动读取保险箱，代码里绝对没有明文密码！
MY_DEEPSEEK_API_KEY = ""
try:
    MY_DEEPSEEK_API_KEY = st.secrets["DEEPSEEK_API_KEY"]
except:
    pass

# ==========================================
# 2. 核心大模型与本地向量库初始化
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

# 初始化所有 Session State (状态保持)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "flip_state" not in st.session_state:
    st.session_state.flip_state = {}

# ==========================================
# 3. 侧边栏：配置与私人资料库投喂中心
# ==========================================
with st.sidebar:
    st.header("⚙️ 系统中枢")
    if MY_DEEPSEEK_API_KEY:
        st.success("✅ 云端专属 API 密钥已自动挂载")
    else:
        st.warning("⚠️ 未检测到云端密钥")
        MY_DEEPSEEK_API_KEY = st.text_input("请临时输入 DeepSeek API Key:", type="password")
    
    base_url = "https://api.deepseek.com/v1"
    
    st.markdown("---")
    st.header("📂 私有知识库 (RAG)")
    st.caption("支持投喂你的历年真题、个人背诵笔记 (PDF/DOCX/TXT)，AI 将据此对你进行拷问。")
    uploaded_files = st.file_uploader("拖拽文件至此", accept_multiple_files=True)
    
    chunk_size = st.slider("精准度调节 (文本切片字数)", 200, 800, 400, step=100)
    
    if uploaded_files and st.button("🚀 深度解析并重构大脑"):
        all_text = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for idx, f in enumerate(uploaded_files):
            status_text.text(f"正在解析: {f.name}...")
            file_text = ""
            try:
                if f.name.endswith('.pdf'):
                    pdf_reader = PdfReader(f)
                    for page in pdf_reader.pages:
                        if page.extract_text():
                            file_text += page.extract_text() + "\n"
                elif f.name.endswith('.docx'):
                    file_text = docx2txt.process(f)
                elif f.name.endswith('.txt'):
                    file_text = f.read().decode("utf-8")
                
                if file_text.strip():
                    all_text.append(file_text)
            except Exception as e:
                st.error(f"解析文件 {f.name} 时遭遇异常: {e}")
            progress_bar.progress((idx + 1) / len(uploaded_files))
            
        if all_text:
            status_text.text("正在进行向量化降维处理...")
            chunks = []
            for text in all_text:
                for i in range(0, len(text), chunk_size - 100):
                    chunks.append(text[i:i+chunk_size])
            
            st.session_state.vector_store = FAISS.from_texts(chunks, get_embeddings())
            status_text.text("✅ 专属知识库构建完毕！")
            st.balloons()
        else:
            status_text.text("❌ 未能提取有效文本")

# ==========================================
# 4. 核心功能数据字典 (内置海量考点)
# ==========================================
THEORY_DB = {
    "议程设置理论": {
        "5w": ["麦库姆斯/肖 (延续控制分析)", "媒介议程影响公众议程 (属性/网络议程)", "传统大众媒介->算法分发时代", "非完全被动，但认知受框架限制", "认知层面的强效果复兴"],
        "clues": ["源于李普曼的拟态环境", "决定人们想什么，而非怎么想", "第二层属性议程设置", "第三层网络议程设置"]
    },
    "沉默的螺旋": {
        "5w": ["诺尔-诺依曼 (社会心理学)", "优势意见的扩大与劣势意见的隐藏", "大众传播的复调性与公开性", "害怕孤立的受众 (准感官统计)", "舆论的社会控制机制生成"],
        "clues": ["趋同心理与害怕孤立", "媒介的三大特性：共鸣、累积、遍在", "双重气候的感知", "互联网时代的中坚分子与反向螺旋"]
    },
    "数字劳动与异化": {
        "5w": ["数字资本/平台架构", "用户免费提供数据与注意力", "社交媒体/智能算法/内容农场", "产消合一者 (Prosumer)", "隐蔽的剩余价值剥削与平台资本积累"],
        "clues": ["斯迈兹的受众商品论延伸", "泰勒制在数字时代的复现", "玩工 (Playbour) 现象", "情感劳动与算法黑箱"]
    }
}

# ==========================================
# 5. 主界面布局：四大旗舰模块
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 5W 连贯带背", 
    "📜 新闻史编年体", 
    "🔥 热点题库实战", 
    "🤖 专属 AI 导师"
])

# ------------------------------------------
# 模块一：5W 连贯带背舱
# ------------------------------------------
with tab1:
    st.header("🧠 模块化理论拆解与网状记忆")
    selected_theory = st.selectbox("选择攻克目标：", list(THEORY_DB.keys()))
    
    st.subheader("🧭 5W 全景拓扑视图")
    t_data = THEORY_DB[selected_theory]["5w"]
    cols = st.columns(5)
    labels = ["Who (控制者)", "Says What (内容)", "In Which Channel (媒介)", "To Whom (受众)", "With What Effect (效果)"]
    for i in range(5):
        cols[i].markdown(f"<div class='theory-card'><b>{labels[i]}</b><br/><br/>{t_data[i]}</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("⛓️ 逻辑链条挖空带背")
    st.info("请尝试根据以下线索，用自己的语言把理论串联起来。")
    
    clues = THEORY_DB[selected_theory]["clues"]
    for idx, clue in enumerate(clues):
        col_btn, col_txt = st.columns([1, 9])
        btn_key = f"clue_{selected_theory}_{idx}"
        if btn_key not in st.session_state.flip_state:
            st.session_state.flip_state[btn_key] = False
            
        with col_btn:
            if st.button("👁️ 显示" if not st.session_state.flip_state[btn_key] else "🙈 隐藏", key=f"btn_{btn_key}"):
                st.session_state.flip_state[btn_key] = not st.session_state.flip_state[btn_key]
                st.rerun()
                
        with col_txt:
            if st.session_state.flip_state[btn_key]:
                st.success(clue)
            else:
                st.warning("核心考点线索已被隐藏，请回想...")

# ------------------------------------------
# 模块二：新闻史编年体纵横线
# ------------------------------------------
with tab2:
    st.header("🕰️ 中外新闻史高分串联体系")
    history_mode = st.radio("切换历史视角：", ["横向时间轴（同代中外事件碰撞）", "纵向专题史（脉络演进）"], horizontal=True)
    
    if "横向" in history_mode:
        with st.expander("📌 19世纪末20世纪初：中国维新 vs 美国煽情", expanded=True):
            h_col1, h_col2 = st.columns(2)
            h_col1.markdown("#### 🇨🇳 维新派办报高潮\n- **领军人物：** 梁启超、康有为、严复\n- **核心报刊：** 《时务报》《国闻报》\n- **高频名解：** 时务文体、去塞求通、耳目喉舌论\n- **历史意义：** 开启政论报刊先河，资产阶级新闻思想萌芽。")
            h_col2.markdown("#### 🇺🇸 黄色新闻大战\n- **领军人物：** 普利策 vs 赫斯特\n- **核心报刊：** 《世界报》vs《纽约日报》\n- **高频名解：** 黄色新闻、煽情主义、美西战争\n- **历史意义：** 商业化新闻的顶峰，直接促发了后期的客观性报道反思。")
            
        with st.expander("📌 20世纪初：五四时期报刊改革 vs 麦克卢汉的降生"):
            st.write("此部分待用户自定义补充...")
    else:
        with st.expander("🔥 专题一：中国共产党党报理论发展史", expanded=True):
            st.markdown("""
            1. **孕育期 (大革命与苏区)：** 《向导》《红色中华》，确立阶级立场。
            2. **成熟期 (延安时期)：** 1942年《解放日报》改版。**核心考点**：确立党性、群众性、战斗性、组织性。
            3. **探索期 (建国初期)：** 1956年新闻改革。**核心考点**：探讨业务规律，倡导“同栏不同音”，反教条主义。
            """)

# ------------------------------------------
# 模块三：热点题库与 AI 智能判卷
# ------------------------------------------
with tab3:
    st.header("⚔️ 真题模拟与热点防御阵地")
    
    hot_topics = ["AI大模型时代的‘数字拟态环境’危机", "微短剧爆火背后的‘情感劳动’与‘下沉市场’", "饭圈文化与网络暴力的‘群体极化’机制"]
    current_hot = st.selectbox("选择本周突击热点：", hot_topics)
    
    st.markdown("### 📝 题型转换阵列")
    t1, t2, t3 = st.columns(3)
    t1.error("【名词解释】\n请解释该事件涉及的底层核心概念。要求150字，精准命中踩分点。")
    t2.warning("【简答题】\n请简述该现象的形成机制及媒介推手。要求分点作答，逻辑清晰。")
    t3.success("【论述题】\n结合马克思主义新闻观或批判学派，论述该现象的异化危机及治理路径。")
    
    st.markdown("---")
    st.markdown("### 🧑‍⚖️ 严苛阅卷官打分系统")
    student_ans = st.text_area("在此作答，接受 AI 导师的无情审判：", height=180, placeholder="在此敲入你的答题框架或全篇内容...")
    
    if st.button("提交试卷 (消耗 API 额度)"):
        if not MY_DEEPSEEK_API_KEY:
            st.error("请先在左侧边栏配置系统密钥！")
        elif len(student_ans) < 20:
            st.warning("字数太少，请认真对待模拟考！")
        else:
            with st.spinner("阅卷组正在进行多维度综合评分..."):
                try:
                    client = OpenAI(api_key=MY_DEEPSEEK_API_KEY, base_url=base_url)
                    prompt = f"""作为新传考研阅卷组长，针对热点“{current_hot}”，严格评判以下作答：
                    【作答内容】：{student_ans}
                    
                    【评判要求】：
                    1. 给出满分30分情况下的具体得分。
                    2. 犀利指出漏掉的“核心专业名词”或理论硬伤。
                    3. 给出一段极具学术网感的高分论述示范段落。
                    4. 纪律：绝对禁止使用‘极其’一词，视语境替换为‘十分’‘相当’‘极度’等。
                    """
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.markdown("### 📊 阅卷报告")
                    st.write(response.choices[0].message.content)
                except Exception as e:
                    st.error(f"调用阅卷官失败: {e}")

# ------------------------------------------
# 模块四：专属 AI RAG 问答导师
# ------------------------------------------
with tab4:
    st.header("🤖 智能伴学与私库拷问大厅")
    
    ai_mode = st.radio("导师人格设定：", ["☕ 围炉煮茶 (温和答疑)", "🌪️ 苏格拉底风暴 (多轮反问，逼迫思考)", "🎯 私库魔鬼抽题 (基于你上传的资料)"], horizontal=True)
    
    # 渲染历史记忆
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            
    # 双模态输入源
    u_input = st.chat_input("输入问题，或接受抽题指令...")
    u_audio = st.audio_input("或点击此处进行语音背诵/提问：")
    
    final_query = u_input if u_input else ("【收到语音】请结合上下文继续。" if u_audio else "")
    
    if final_query:
        if not MY_DEEPSEEK_API_KEY:
            st.error("密钥缺失，导师已离线。")
        else:
            with st.chat_message("user"): st.write(final_query)
            st.session_state.messages.append({"role": "user", "content": final_query})
            
            # RAG 混合检索逻辑
            context_str = ""
            if st.session_state.vector_store and ("私库" in ai_mode or "煮茶" in ai_mode):
                docs = st.session_state.vector_store.similarity_search(final_query, k=3)
                if docs:
                    with st.expander("🔍 AI 检索到的私库参考片段 (RAG)"):
                        for i, d in enumerate(docs):
                            st.caption(f"片段 {i+1}: {d.page_content}")
                    context_str = "\n【必须参考的用户笔记】：\n" + "\n".join([d.page_content for d in docs])
            elif "私库" in ai_mode and not st.session_state.vector_store:
                st.warning("你还没上传笔记，导师无法抽题！将退回普通模式。")
                
            # 严格构建 System Prompt
            sys_prompt = "你是辅导新闻传播学考研的AI导师。必须运用5W框架拆解理论。严禁使用‘极其’一词，请替换为‘十分’‘相当’‘很是’‘极度’等。"
            if "苏格拉底" in ai_mode:
                sys_prompt += "不要直接给完整答案，通过刁钻的反问榨干用户的知识储备。"
            elif "私库" in ai_mode:
                sys_prompt += "你现在是考官，请根据【必须参考的用户笔记】提取考点，对用户进行严厉拷问或纠错。"
                
            msgs_payload = [{"role": "system", "content": sys_prompt + context_str}]
            msgs_payload.extend(st.session_state.messages[-6:])
            
            try:
                client = OpenAI(api_key=MY_DEEPSEEK_API_KEY, base_url=base_url)
                with st.chat_message("assistant"):
                    reply_box = st.empty()
                    reply_text = ""
                    res = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=msgs_payload,
                        stream=True
                    )
                    for chunk in res:
                        if chunk.choices[0].delta.content:
                            reply_text += chunk.choices[0].delta.content
                            reply_box.markdown(reply_text + "▌")
                    reply_box.markdown(reply_text)
                st.session_state.messages.append({"role": "assistant", "content": reply_text})
            except Exception as e:
                st.error(f"连接深层网络失败: {e}")