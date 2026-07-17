import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ==========================================
# 1. 網頁基本設定與 Session 初始化
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維極簡預測面板")

if "maintenance_records" not in st.session_state: 
    st.session_state.maintenance_records = []
if "ai_messages" not in st.session_state: 
    st.session_state.ai_messages = []

# ==========================================
# 2. 數據清洗與統計核心 (修復 Excel 翻譯列導致的錯誤)
# ==========================================
def load_and_clean_data(file):
    raw_df = pd.read_excel(file)
    # 過濾：只保留 "No." 欄位有有效數字的資料列
    cleaned = raw_df[raw_df["No."].notna() & (raw_df["No."].astype(str).str.replace('.', '', 1).str.isdigit())]
    return cleaned

# 側邊欄上傳
with st.sidebar:
    st.title("⚙️ 控制中心")
    uploaded_file = st.file_uploader("📂 上傳 F-mask 原始 Excel (005.xlsx)", type=["xlsx"])

# 處理數據
source_df = load_and_clean_data(uploaded_file) if uploaded_file else pd.DataFrame()
manual_df = pd.DataFrame(st.session_state.maintenance_records)
df = pd.concat([source_df, manual_df], ignore_index=True) if not source_df.empty or not manual_df.empty else pd.DataFrame()

# 計算指標
top_part = "N/A"
uncompleted_count = 0
uncompleted_df = pd.DataFrame()

if not df.empty:
    machine_counts = df["ชื่อเครื่องจักร / อุปกรณ์"].dropna().value_counts()
    if not machine_counts.empty:
        top_part = machine_counts.index[0]
    
    # 篩選未完成 (排除 "9.0 ดำเนินการแล้วเสร็จ", "Job Closed", "結案")
    completed_mask = df["สถานะใบแจ้งซ่อม"].astype(str).str.contains("9.0|Closed|結案", na=False, case=False)
    uncompleted_df = df[~completed_mask]
    uncompleted_count = len(uncompleted_df)

# ==========================================
# 3. 頁面 Tabs 渲染
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs(["💡 重點儀表", "📈 追蹤儀表", "🔮 預測", "📅 管理", "🤖 AI 助手"])

with tab1:
    st.markdown("### 📊 關鍵維護指標總覽")
    col1, col2, col3 = st.columns(3)
    col1.metric("🚨 高風險故障機台", top_part)
    col2.metric("⏳ 未結案工單", f"{uncompleted_count} 件")
    col3.metric("📊 總維修紀錄數", len(df))
    
    if not uncompleted_df.empty:
        st.markdown("##### ⏳ 待處理工單列表")
        st.dataframe(uncompleted_df[["ลำดับเอกสาร", "ชื่อเครื่องจักร / อุปกรณ์", "สถานะใบแจ้งซ่อม"]], use_container_width=True)

with tab2:
    st.subheader("📈 維修趨勢")
    if not df.empty:
        fig = px.bar(df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts().head(10).reset_index(), x="ชื่อเครื่องจักร / อุปกรณ์", y="count")
        st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("📅 維修管理")
    with st.expander("➕ 新增手動維修日誌"):
        with st.form("manual_entry_form"):
            new_id = st.text_input("工單編號", f"MES-{datetime.now().strftime('%y%m%d%H%M')}")
            new_machine = st.text_input("機台名稱", value=top_part if top_part != "N/A" else "")
            new_status = st.selectbox("狀態", ["4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง", "9.0 ดำเนินการแล้วเสร็จ"])
            new_detail = st.text_area("異常描述")
            if st.form_submit_button("確認新增"):
                st.session_state.maintenance_records.append({
                    "ลำดับเอกสาร": new_id, "ชื่อเครื่องจักร / อุปกรณ์": new_machine,
                    "สถานะใบแจ้งซ่อม": new_status, "รายละเอียดที่ต้องการดำเนินการ": new_detail
                })
                st.rerun()

    if st.session_state.maintenance_records:
        for i, record in enumerate(st.session_state.maintenance_records):
            cols = st.columns([5, 1])
            cols[0].text(f"[{record['ลำดับเอกสาร']}] {record['ชื่อเครื่องจักร / อุปกรณ์']}")
            if cols[1].button("🗑️ 刪除", key=f"del_{i}"):
                st.session_state.maintenance_records.pop(i)
                st.rerun()

with tab5:
    st.markdown("### 🤖 AI 智慧助手")
    user_q = st.chat_input("請描述機台異常...")
    if user_q:
        st.session_state.ai_messages.append({"role": "user", "content": user_q})
        response = "🛠️ **SOP 建議：** 請優先檢查氣路或電路，並登錄至工單系統。"
        st.session_state.ai_messages.append({"role": "assistant", "content": response})
        for msg in st.session_state.ai_messages:
            with st.chat_message(msg["role"]): st.write(msg["content"])
