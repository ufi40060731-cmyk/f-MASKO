import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# 頁面設定
st.set_page_config(layout="wide", page_title="F-mask 運維儀表板")

# Session State 初始化
if "maintenance_records" not in st.session_state: st.session_state.maintenance_records = []

# 多語言字典
LANG = {
    "繁體中文": {"title": "F-mask 預防保養儀表板", "tabs": ["💡 概覽", "📈 趨勢", "🔮 預測", "📅 管理", "🤖 AI"], "m1": "待處理", "m2": "總紀錄", "m3": "最新紀錄"},
    "English": {"title": "F-mask Maintenance Dashboard", "tabs": ["💡 Highlights", "📈 Trends", "🔮 Prediction", "📅 Management", "🤖 AI"], "m1": "Pending", "m2": "Total", "m3": "Latest"},
    "ภาษาไทย": {"title": "F-mask ระบบคาดการณ์การบำรุงรักษา", "tabs": ["💡 แดชบอร์ด", "📈 แนวโน้ม", "🔮 คาดการณ์", "📅 การจัดการ", "🤖 ผู้ช่วย AI"], "m1": "ค้างอยู่", "m2": "ทั้งหมด", "m3": "ล่าสุด"}
}

# 側邊欄
with st.sidebar:
    lang_choice = st.radio("Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
    L = LANG[lang_choice]
    uploaded_file = st.file_uploader("📂 上傳 Excel", type=["xlsx"])

# 資料讀取
df = pd.read_excel(uploaded_file) if uploaded_file else pd.DataFrame()
if st.session_state.maintenance_records:
    df = pd.concat([df, pd.DataFrame(st.session_state.maintenance_records)], ignore_index=True)

# 主畫面
st.title(L["title"])
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tabs"])

with tab1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric(L["m1"], len(df[df.iloc[:, 2] != "Closed"])) # 假設第三欄是狀態
        c2.metric(L["m2"], len(df))
        c3.metric(L["m3"], df.iloc[-1, 0] if len(df) > 0 else "N/A")
        st.success("儀表板已更新，系統運行正常。")
    else:
        st.info("請上傳 Excel 檔案")

with tab2:
    st.subheader(L["tabs"][1])
    if not df.empty:
        # 自動繪製趨勢圖，讓主管一眼看懂
        fig = px.bar(df.head(20), x=df.columns[0], y=df.columns[1] if len(df.columns) > 1 else None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("無數據可顯示")

with tab3:
    st.subheader(L["tabs"][2])
    st.warning("⚠️ 預測分析：系統將自動計算下一次保養區間 (需依實際 Excel 欄位設定)。")
    st.dataframe(df.tail(5), use_container_width=True)

with tab4:
    st.subheader(L["tabs"][3])
    with st.form("add_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        n_id = col1.text_input("工單編號", f"ID-{datetime.now().strftime('%Y%m%d')}")
        n_name = col2.text_input("機台名稱")
        n_stat = st.selectbox("狀態", ["Pending", "Closed"])
        if st.form_submit_button("新增紀錄"):
            st.session_state.maintenance_records.append({"No.": n_id, "Machine": n_name, "Status": n_stat})
            st.rerun()
    st.table(pd.DataFrame(st.session_state.maintenance_records))

with tab5:
    st.subheader(L["tabs"][4])
    st.chat_message("assistant").write("我是您的 AI 助手，請問有哪些機台異常需要處理？")
