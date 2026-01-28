import streamlit as st
import datetime
import requests
import json
import os

# ================= 配置区 =================
# ⚠️ 请将你的 DeepSeek API Key 填入下方
API_KEY = "sk-3634d85ee9194fe784aa22b8e8b33087"  
API_URL = "https://api.deepseek.com/chat/completions"

# 页面基础设置
st.set_page_config(
    page_title="🐱 喵喵少女日记本",
    page_icon="🐱",
    layout="centered"
)

# 自定义一些可爱的CSS样式
st.markdown("""
<style>
    .stApp {background-color: #FFF0F5;}
    .stButton>button {background-color: #FFB7B2; color: white; border-radius: 10px; border: none;}
    .stTextInput>div>div>input {border-radius: 10px;}
    h1, h2, h3 {color: #5D4037;}
</style>
""", unsafe_allow_html=True)

# ================= 数据处理 =================
# 注意：在云端简易模式下，数据保存在 session_state 中
# 如果要永久保存不丢失，需要连接数据库（这对初学者略难，目前版本刷新网页数据会重置，适合体验树洞）

if "todos" not in st.session_state:
    st.session_state.todos = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "你好呀！我是你的树洞精灵，有什么心事都可以告诉我哦~ 🐱"}
    ]

# ================= 侧边栏 =================
with st.sidebar:
    st.image("https://img.icons8.com/doodle/96/000000/cat--v1.png", width=100)
    st.title("设置")
    theme = st.selectbox("选择主题颜色", ["猫咪粉", "薄荷蓝"])
    if theme == "薄荷蓝":
        st.markdown("""<style>.stApp {background-color: #E0F7FA;}</style>""", unsafe_allow_html=True)
    st.info("💡 这是一个云端日记本，你可以随时随地访问！")

# ================= 主界面 =================
st.title("🐱 喵喵少女日记本")

# 创建标签页
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📖 日记本", "🌸 小幸福", "📝 待办", "⏳ 倒计时", "🌳 树洞小咪"])

# --- 模块 1: 日记 ---
with tab1:
    st.header("喵喵~今天的心情怎么样？")
    mood = st.radio("心情", ["😸 开心", "😿 难过", "😾 生气", "🐱 平淡"], horizontal=True, label_visibility="collapsed")
    
    diary_content = st.text_area("写下今天的故事...", height=150)
    
    if st.button("✨ 保存日记"):
        if diary_content:
            date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            st.success(f"已记录！\n时间：{date_str}\n心情：{mood}\n内容：{diary_content}")
            # 这里实际开发中需要写入数据库
        else:
            st.warning("日记不能为空喵")

# --- 模块 2: 小确幸 ---
with tab2:
    st.header("今日五件幸福小事 ✨")
    for i in range(5):
        st.text_input(f"第 {i+1} 件小幸福", key=f"happy_{i}")
    if st.button("💾 保存幸福"):
        st.balloons()  # 放飞气球特效
        st.success("喵~幸福已确认！要天天开心喵~")

# --- 模块 3: 待办 ---
with tab3:
    st.header("📝 待办清单")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        new_todo = st.text_input("添加新任务", label_visibility="collapsed")
    with col2:
        if st.button("添加"):
            if new_todo:
                st.session_state.todos.append(new_todo)
                st.rerun() # 刷新页面

    st.write("---")
    for i, todo in enumerate(st.session_state.todos):
        col_a, col_b = st.columns([4, 1])
        with col_a:
            st.write(f"⬜ {todo}")
        with col_b:
            if st.button("完成", key=f"del_{i}"):
                st.session_state.todos.pop(i)
                st.rerun()

# --- 模块 4: 倒计时 ---
with tab4:
    st.header("⏳ 重要日子倒计时")
    target_date = st.date_input("选择日期", datetime.date(2026, 6, 7))
    event_name = st.text_input("事件名称", "重要日子")
    
    today = datetime.date.today()
    delta = target_date - today
    
    st.metric(label=f"距离 {event_name}", value=f"{delta.days} 天")

# --- 模块 5: 树洞 (DeepSeek) ---
with tab5:
    st.header("🌳 树洞精灵")
    st.caption("接入 小猫咪")

    # 显示历史消息
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🐱" if msg["role"] == "assistant" else "👤"):
            st.write(msg["content"])

    # 输入框
    if prompt := st.chat_input("喵~和我说说悄悄话..."):
        # 用户消息
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="👤"):
            st.write(prompt)

        # AI 回复
        with st.chat_message("assistant", avatar="🐱"):
            message_placeholder = st.empty()
            message_placeholder.markdown("正在思考喵...")
            
            try:
                headers = {"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "你是一只温柔、治愈的猫咪树洞精灵。你和用户是好朋友。你的名字叫'小颖咪'。请用可爱、同理心强的语气回复用户的烦恼或分享，治愈用户，经常使用颜文字。"},
                    ] + [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_history],
                    "stream": False
                }
                response = requests.post(API_URL, headers=headers, json=payload)
                
                if response.status_code == 200:
                    ai_content = response.json()['choices'][0]['message']['content']
                    message_placeholder.markdown(ai_content)
                    st.session_state.chat_history.append({"role": "assistant", "content": ai_content})
                else:
                    message_placeholder.markdown(f"树洞连接失败了... ({response.status_code})")
            except Exception as e:
                message_placeholder.markdown(f"网络出错了喵: {e}")
