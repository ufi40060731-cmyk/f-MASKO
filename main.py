import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ==========================================
# 1. 網頁基本設定
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維極簡預測面板")

if "tech_logs" not in st.session_state: st.session_state.tech_logs = []
if "maintenance_records" not in st.session_state: st.session_state.maintenance_records = []
if "ai_messages" not in st.session_state: st.session_state.ai_messages = []

# ==========================================
# 2. 側邊欄控制
# ==========================================
with st.sidebar:
    st.title("⚙️ 控制中心")
    selected_lang = st.radio("語言", ["繁體中文", "English", "ภาษาไทย"])
    theme_mode = st.radio("主題", ["☀️ 白天", "🌙 黑夜"])
    uploaded_file = st.file_uploader("📂 上傳 Excel", type=["xlsx"])

# 樣式定義 (CSS)
bg_color = "#0e1117" if "🌙" in theme_mode else "#ffffff"
text_color = "#ffffff" if "🌙" in theme_mode else "#31333f"
st.markdown(f"<style>.stApp {{ background-color: {bg_color}; color: {text_color}; }}</style>", unsafe_allow_html=True)

# 字典定義 (LANG_DICT 請維持您原本的完整內容)
# ... (此處省略字典設定，請保留您原本的 LANG_DICT) ...
L = LANG_DICT[selected_lang]

# ==========================================
# 3. 資料處理
# ==========================================
def load_data(file):
    df = pd.read_excel(file)
    df["Parsed_Date"] = pd.to_datetime(df["วันที่แจ้งซ่อม"], errors='coerce')
    return df

source_df = load_data(uploaded_file) if uploaded_file else pd.DataFrame()
manual_df = pd.DataFrame(st.session_state.maintenance_records)
df = pd.concat([source_df, manual_df], ignore_index=True) if not manual_df.empty else source_df

# 計算儀表板數據
overdue_count = 0 
top_part, top_count = "N/A", 0
uncompleted_count = 0
if not df.empty:
    counts_series = df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts()
    top_part = counts_series.index[0] if not counts_series.empty else "N/A"
    top_count = counts_series.iloc[0] if not counts_series.empty else 0
    uncompleted_count = len(df[~df["สถานะใบแจ้งซ่อม"].astype(str).str.contains("Completed", na=False)])

# ==========================================
# 4. 主畫面架構 (整合 AI 與重點頁)
# ==========================================
st.title(L["title"])

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 重點儀表 (Highlights)", 
    L["tab_dashboard"], 
    L["tab_prediction"], 
    L["tab_pm_schedule"], 
    "🤖 AI 智慧助手"
])

# --- TAB 1: 重點儀表 ---
with tab1:
    st.markdown("### 📊 關鍵維護指標總覽")
    col1, col2, col3 = st.columns(3)
    col1.metric("🚨 近期高風險零件", f"{overdue_count} 項")
    col2.metric("🔥 高頻故障機台", f"{top_part}")
    col3.metric("⏳ 未結案工單", f"{uncompleted_count} 件")
    st.divider()
    st.info("系統正處於實時分析狀態，若資料未更新，請確認 Excel 或手動紀錄。")

# --- TAB 2, 3, 4: 原有邏輯 ---
with tab2: # 儀表板邏輯
    # ... (請貼上您原本 tab1 的邏輯內容)
with tab3: # 預測邏輯
    # ... (請貼上您原本 tab2 的邏輯內容)
with tab4: # 維修紀錄邏輯
    # ... (請貼上您原本 tab4 的邏輯內容)

# --- TAB 5: AI 智慧助手 ---
with tab5:
    st.markdown("### 🤖 F-mask 維修 AI 智慧助手")
    user_q = st.chat_input("輸入機台異常描述 (例如: 氣缸漏氣)...")
    if user_q:
        st.session_state.ai_messages.append({"role": "user", "content": user_q})
        resp = "根據 F-mask SOP：請檢查密封圈並確認潤滑狀態。" if "漏氣" in user_q else "請描述具體現象以獲取 SOP。"
        st.session_state.ai_messages.append({"role": "assistant", "content": resp})

    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
