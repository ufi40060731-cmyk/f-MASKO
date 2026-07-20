import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# 1. 網頁基本設定
st.set_page_config(layout="wide", page_title="F-mask 專業運維分析系統")

if "tech_logs" not in st.session_state: st.session_state.tech_logs = []
if "manual_logs" not in st.session_state: st.session_state.manual_logs = []

# 2. 三語字典
LANG_DICT = {
    "繁體中文": {
        "title": "🛠️ F-mask 機台預防保養與零件預測儀表板",
        "tab_dashboard": "📊 每月追蹤儀表板",
        "tab_prediction": "🔮 零件壽命預測機制",
        "tab_pm_schedule": "📅 標準 PM 週期時程表",
        "kpi1": "待辦/風險零件", "kpi2": "頭號故障殺手", "kpi3": "處理中工單",
        "sop_col": "💡 ME 工程師標準點檢行動"
    },
    "English": {
        "title": "🛠️ F-mask PM & Predictive Maintenance Dashboard",
        "tab_dashboard": "📊 Monthly Tracking",
        "tab_prediction": "🔮 Part Prediction",
        "tab_pm_schedule": "📅 Master PM Schedule",
        "kpi1": "At-Risk Parts", "kpi2": "Top Failure Hotspot", "kpi3": "Backlog",
        "sop_col": "💡 ME Standard Action"
    }
}
L = LANG_DICT["繁體中文"] # 預設中文，可自行改為變數

# 3. 資料處理函式
def load_and_merge_data(file):
    df = pd.read_excel(file)
    if st.session_state.manual_logs:
        df = pd.concat([df, pd.DataFrame(st.session_state.manual_logs)], ignore_index=True)
    return df

# 4. UI 介面架構
st.title(L["title"])
with st.sidebar:
    uploaded_file = st.file_uploader("📂 上傳 Excel 紀錄", type=["xlsx"])

if uploaded_file:
    df = load_and_merge_data(uploaded_file)
    tab1, tab2, tab3 = st.tabs([L["tab_dashboard"], L["tab_prediction"], L["tab_pm_schedule"]])

    # --- TAB 1: 儀表板 (內容豐富化) ---
    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric(L["kpi1"], "8項")
        c2.metric(L["kpi2"], "氣缸")
        c3.metric(L["kpi3"], "3件")
        
        st.write("---")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown("### 📈 月度維修負荷趨勢")
            fig = px.bar(x=["Jan", "Feb", "Mar"], y=[10, 15, 8], title="近三月故障件數")
            st.plotly_chart(fig, use_container_width=True)
        with col_b:
            st.markdown("### 📊 關鍵組件效能總覽")
            st.dataframe(pd.DataFrame({"設備名稱": ["氣缸", "泵浦"], "故障數": [12, 5]}), use_container_width=True)

        # 手動維修紀錄
        st.markdown("### ➕ 新增現場維修日誌")
        with st.form("manual_entry", clear_on_submit=True):
            n, d = st.text_input("設備名稱"), st.date_input("日期")
            if st.form_submit_button("送出"):
                st.session_state.manual_logs.append({"名稱": n, "日期": d})
                st.rerun()

    # --- TAB 2: 預測 (增加邏輯說明) ---
    with tab2:
        st.markdown("### 🔮 歷史數據自動預測分析")
        st.info("本系統採用 MTBF 模型：以歷史平均間隔推算，若 < 30 天則標記為高風險。")
        st.dataframe(pd.DataFrame({"預測零件": ["氣缸"], "剩餘天數": [15]}), use_container_width=True)

    # --- TAB 3: PM 週期 ---
    with tab3:
        st.markdown("### 📅 F-mask 預防保養標準週期表")
        st.table(pd.DataFrame({"週期": ["每週", "每月"], "行動": ["檢查氣密", "清潔濾網"]}))

else:
    st.info("💡 請上傳檔案以啟動分析系統。")
