# 1. 移除掉原本的 st.markdown 專案目標區塊 (第 140-146 行左右)

# 2. 修改 Tab 結構，加入 AI 助手與重點頁面
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 重點儀表 (Highlights)", 
    L["tab_dashboard"], 
    L["tab_prediction"], 
    L["tab_pm_schedule"], 
    "🤖 AI 智慧助手"
])

# --- 新增：TAB 1 重點儀表 ---
with tab1:
    st.markdown("### 📊 關鍵維護指標總覽")
    col1, col2, col3 = st.columns(3)
    col1.metric("🚨 近期高風險零件", f"{overdue_count} 項")
    col2.metric("🔥 高頻故障機台", f"{top_part}")
    col3.metric("⏳ 未結案工單", f"{uncompleted_count} 件")
    st.divider()
    st.markdown("這裡可以放置機台健康度趨勢圖，讓管理層一目了然。")

# --- 新增：TAB 5 AI 智慧助手 ---
with tab5:
    st.markdown("### 🤖 F-mask 維修 AI 智慧助手")
    st.info("您可以輸入機台故障現象，AI 將自動對應 SOP 並給予維修建議。")
    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = []
    
    # 簡單的對話介面
    user_q = st.chat_input("請輸入機台異常描述...")
    if user_q:
        st.session_state.ai_messages.append({"role": "user", "content": user_q})
        # 此處可對接您的 LLM 或邏輯判斷
        st.session_state.ai_messages.append({"role": "assistant", "content": f"根據 F-mask SOP，針對 '{user_q}' 的建議處置為：..."})

    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
