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

# 假設 LANG_DICT 結構，若您有現成檔案請確保此處能讀取
# L = LANG_DICT[selected_lang]
L = {"title": "F-mask 機台預防保養與零件預測儀表板", "tab_dashboard": "每月追蹤儀表板", "tab_prediction": "零件壽命預測機制", "tab_pm_schedule": "標準 PM 週期時程表"}

# ==========================================
# 3. 資料處理
# ==========================================
def load_data(file):
    df = pd.read_excel(file)
    df["Parsed_Date"] = pd.to_datetime(df.iloc[:, 0], errors='coerce') # 假設第一欄為日期
    return df

source_df = load_data(uploaded_file) if uploaded_file else pd.DataFrame()
manual_df = pd.DataFrame(st.session_state.maintenance_records)
df = pd.concat([source_df, manual_df], ignore_index=True) if not manual_df.empty else source_df

overdue_count, top_part, uncompleted_count = 0, "N/A", 0
if not df.empty:
    overdue_count = len(df) # 簡化範例
    uncompleted_count = len(df) # 簡化範例

# ==========================================
# 4. 主畫面架構
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
    st.info("系統已更新：已整合手動與 Excel 資料。")

# --- TAB 2, 3, 4: 預留區塊 (請在此補上您的業務邏輯) ---
with tab2:
    pass 
with tab3:
    pass
with tab4:
    pass

# --- TAB 5: AI 智慧助手 ---
with tab5:
    st.markdown("### 🤖 F-mask 維修 AI 智慧助手")
    user_q = st.chat_input("輸入機台異常描述...")
    if user_q:
        st.session_state.ai_messages.append({"role": "user", "content": user_q})
        resp = "根據 SOP：請確認氣缸壓力設定。" if "氣缸" in user_q else "請輸入故障狀況。"
        st.session_state.ai_messages.append({"role": "assistant", "content": resp})

    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
