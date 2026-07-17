import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ==========================================
# 1. 網頁設定與 Session 初始化
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維儀表板")

if "maintenance_records" not in st.session_state: 
    st.session_state.maintenance_records = []
if "ai_messages" not in st.session_state: 
    st.session_state.ai_messages = []

# ==========================================
# 2. 語言設定
# ==========================================
LANG_DICT = {
    "繁體中文": {
        "title": "F-mask 機台預防保養儀表板",
        "t1": "💡 重點儀表", "t2": "📈 維修趨勢", "t3": "🔮 預測", "t4": "📅 維修管理", "t5": "🤖 AI 助手",
        "del": "🗑️ 刪除", "sub": "確認新增", "add": "➕ 新增手動維修日誌",
        "m_name": "機台名稱", "status": "狀態", "id": "工單編號", "desc": "異常描述"
    },
    "English": {
        "title": "F-mask Predictive Maintenance Dashboard",
        "t1": "💡 Highlights", "t2": "📈 Trends", "t3": "🔮 Prediction", "t4": "📅 Management", "t5": "🤖 AI Assistant",
        "del": "🗑️ Delete", "sub": "Submit", "add": "➕ Add Manual Log",
        "m_name": "Machine Name", "status": "Status", "id": "Running No", "desc": "Failure Detail"
    },
    "ภาษาไทย": {
        "title": "F-mask ระบบคาดการณ์การบำรุงรักษา",
        "t1": "💡 แดชบอร์ดหลัก", "t2": "📈 แนวโน้ม", "t3": "🔮 คาดการณ์", "t4": "📅 การจัดการ", "t5": "🤖 ผู้ช่วย AI",
        "del": "🗑️ ลบ", "sub": "ยืนยัน", "add": "➕ เพิ่มบันทึกการซ่อม",
        "m_name": "ชื่อเครื่องจักร", "status": "สถานะ", "id": "หมายเลขเอกสาร", "desc": "รายละเอียด"
    }
}

with st.sidebar:
    lang_choice = st.radio("Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
    L = LANG_DICT[lang_choice]
    uploaded_file = st.file_uploader("📂 上傳 Excel", type=["xlsx"])

# ==========================================
# 3. 資料讀取與處理
# ==========================================
def load_clean(file):
    df = pd.read_excel(file)
    return df[df["No."].notna() & (df["No."].astype(str).str.replace('.', '', 1).str.isdigit())]

source_df = load_clean(uploaded_file) if uploaded_file else pd.DataFrame()
manual_df = pd.DataFrame(st.session_state.maintenance_records)
df = pd.concat([source_df, manual_df], ignore_index=True) if not source_df.empty or not manual_df.empty else pd.DataFrame()

# ==========================================
# 4. 介面呈現
# ==========================================
st.title(L["title"])
tab1, tab2, tab3, tab4, tab5 = st.tabs([L["t1"], L["t2"], L["t3"], L["t4"], L["t5"]])

with tab1:
    st.markdown("### 📊 關鍵數據概覽")
    if not df.empty:
        col1, col2, col3 = st.columns(3)
        top = df["ชื่อเครื่องจักร / อุปกรณ์"].mode()[0] if not df["ชื่อเครื่องจักร / อุปกรณ์"].empty else "N/A"
        pending = len(df[~df["สถานะใบแจ้งซ่อม"].astype(str).str.contains("9.0|Closed|結案", na=False)])
        col1.metric("🔥 高頻機台", top)
        col2.metric("⏳ 未結案工單", f"{pending} 件")
        col3.metric("📊 總紀錄", len(df))
    else:
        st.info("請上傳資料")

with tab4:
    st.subheader(L["t4"])
    with st.expander(L["add"]):
        with st.form("entry"):
            nid = st.text_input(L["id"], f"MES-{datetime.now().strftime('%y%m%d%H%M')}")
            mname = st.text_input(L["m_name"])
            stat = st.selectbox(L["status"], ["4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง", "9.0 ดำเนินการแล้วเสร็จ"])
            desc = st.text_area(L["desc"])
            if st.form_submit_button(L["sub"]):
                st.session_state.maintenance_records.append({"ลำดับเอกสาร": nid, "ชื่อเครื่องจักร / อุปกรณ์": mname, "สถานะใบแจ้งซ่อม": stat, "รายละเอียดที่ต้องการดำเนินการ": desc})
                st.rerun()
    
    for i, r in enumerate(st.session_state.maintenance_records):
        cols = st.columns([5, 1])
        cols[0].text(f"[{r['ลำดับเอกสาร']}] {r['ชื่อเครื่องจักร / อุปกรณ์']}")
        if cols[1].button(L["del"], key=f"d_{i}"):
            st.session_state.maintenance_records.pop(i)
            st.rerun()

with tab5:
    st.markdown("### 🤖 AI 助手")
    msg = st.chat_input("詢問異常...")
    if msg:
        st.session_state.ai_messages.append({"role": "user", "content": msg})
        st.session_state.ai_messages.append({"role": "assistant", "content": "收到，請依 SOP 處理。"})
    for m in st.session_state.ai_messages:
        with st.chat_message(m["role"]): st.write(m["content"])
