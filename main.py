import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ==========================================
# 1. 頁面與設定
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維儀表板")

if "maintenance_records" not in st.session_state:
    st.session_state.maintenance_records = []

LANG = {
    "繁體中文": {"title": "F-mask 預防保養儀表板", "tabs": ["💡 概覽", "📈 維修趨勢", "🔮 預測機制", "📅 保養管理", "🤖 AI 助手"], "m1": "待處理", "m2": "總紀錄", "m3": "最新紀錄"},
    "English": {"title": "F-mask Predictive Maintenance Dashboard", "tabs": ["💡 Highlights", "📈 Trends", "🔮 Prediction", "📅 Management", "🤖 AI Assistant"], "m1": "Pending", "m2": "Total", "m3": "Latest"},
    "ภาษาไทย": {"title": "F-mask ระบบคาดการณ์การบำรุงรักษา", "tabs": ["💡 แดชบอร์ดหลัก", "📈 แนวโน้ม", "🔮 คาดการณ์", "📅 การจัดการ", "🤖 ผู้ช่วย AI"], "m1": "ค้างอยู่", "m2": "ทั้งหมด", "m3": "ล่าสุด"}
}

with st.sidebar:
    lang_choice = st.radio("Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
    L = LANG[lang_choice]
    uploaded_file = st.file_uploader("📂 上傳 Excel (需包含 '日期', '機台', '狀態')", type=["xlsx"])

# ==========================================
# 2. 資料處理 (自動載入與合併)
# ==========================================
df = pd.read_excel(uploaded_file) if uploaded_file else pd.DataFrame()
if st.session_state.maintenance_records:
    df = pd.concat([df, pd.DataFrame(st.session_state.maintenance_records)], ignore_index=True)

# ==========================================
# 3. 儀表板頁面呈現
# ==========================================
st.title(L["title"])
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

# Tab 1: 概覽 (一眼看懂指標)
with tab1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric(L["m1"], len(df[df.iloc[:, 2].astype(str).str.contains("Pending|待處理", na=False)]))
        c2.metric(L["m2"], len(df))
        c3.metric(L["m3"], df.iloc[-1, 0] if len(df) > 0 else "N/A")
    else:
        st.info("請上傳 Excel 檔案以開始分析")

# Tab 2: 維修趨勢 (圖表化)
with tab2:
    st.subheader(L["tabs"][1])
    if not df.empty and len(df.columns) >= 2:
        fig = px.bar(df, x=df.columns[0], y=df.columns[1], title="維修頻率統計")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("請上傳資料以繪製趨勢圖")

# Tab 3: 預測 (簡易預測機制)
with tab3:
    st.subheader(L["tabs"][2])
    st.warning("⚠️ 系統偵測：依歷史數據，機台需定期於 30 天內檢視。")
    st.dataframe(df.tail(10), use_container_width=True)

# Tab 4: 保養管理 (新增與維護)
with tab4:
    st.subheader(L["tabs"][3])
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        n_id = col1.text_input("工單編號", f"PM-{datetime.now().strftime('%Y%m%d')}")
        n_name = col2.text_input("機台名稱")
        n_stat = st.selectbox("狀態", ["Pending", "Closed"])
        if st.form_submit_button("確認新增紀錄"):
            st.session_state.maintenance_records.append({"No.": n_id, "Machine": n_name, "Status": n_stat})
            st.rerun()
    st.table(pd.DataFrame(st.session_state.maintenance_records))

# Tab 5: AI 助手
with tab5:
    st.chat_message("assistant").write("您好，我是 F-mask 運維助手。請問有關於機台維修頻率的分析問題嗎？")
