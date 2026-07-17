import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ==========================================
# 1. 網頁基本設定與 Session 初始化
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維儀表板")

if "maintenance_records" not in st.session_state: 
    st.session_state.maintenance_records = []
if "ai_messages" not in st.session_state: 
    st.session_state.ai_messages = []

# ==========================================
# 2. 語言字典 (Language Dictionary)
# ==========================================
LANG_DICT = {
    "繁體中文": {
        "title": "F-mask 機台預防保養儀表板",
        "tab1": "💡 重點儀表", "tab2": "📈 維修趨勢", "tab3": "🔮 預測", "tab4": "📅 維修管理", "tab5": "🤖 AI 助手",
        "del_btn": "🗑️ 刪除", "add_btn": "確認新增", "add_expander": "➕ 新增手動維修日誌",
        "machine_label": "機台名稱", "status_label": "狀態", "id_label": "工單編號", "desc_label": "異常描述"
    },
    "English": {
        "title": "F-mask Predictive Maintenance Dashboard",
        "tab1": "💡 Highlights", "tab2": "📈 Trends", "tab3": "🔮 Prediction", "tab4": "📅 Management", "tab5": "🤖 AI Assistant",
        "del_btn": "🗑️ Delete", "add_btn": "Submit", "add_expander": "➕ Add Manual Log",
        "machine_label": "Machine Name", "status_label": "Status", "id_label": "Running No", "desc_label": "Failure Detail"
    },
    "ภาษาไทย": {
        "title": "F-mask ระบบคาดการณ์การบำรุงรักษา",
        "tab1": "💡 แดชบอร์ดหลัก", "tab2": "📈 แนวโน้มการซ่อม", "tab3": "🔮 คาดการณ์", "tab4": "📅 การจัดการ", "tab5": "🤖 ผู้ช่วย AI",
        "del_btn": "🗑️ ลบ", "add_btn": "ยืนยัน", "add_expander": "➕ เพิ่มบันทึกการซ่อม",
        "machine_label": "ชื่อเครื่องจักร", "status_label": "สถานะ", "id_label": "หมายเลขเอกสาร", "desc_label": "รายละเอียด"
    }
}

# 側邊欄語言選擇
with st.sidebar:
    selected_lang = st.radio("選擇語言 / Select Language / เลือกภาษา", ["繁體中文", "English", "ภาษาไทย"])
    L = LANG_DICT[selected_lang]
    uploaded_file = st.file_uploader("📂 上傳 Excel (005.xlsx)", type=["xlsx"])

# ==========================================
# 3. 資料處理
# ==========================================
def load_and_clean_data(file):
    raw_df = pd.read_excel(file)
    return raw_df[raw_df["No."].notna() & (raw_df["No."].astype(str).str.replace('.', '', 1).str.isdigit())]

source_df = load_and_clean_data(uploaded_file) if uploaded_file else pd.DataFrame()
manual_df = pd.DataFrame(st.session_state.maintenance_records)
df = pd.concat([source_df, manual_df], ignore_index=True) if not source_df.empty or not manual_df.empty else pd.DataFrame()

# ==========================================
# 4. 頁面渲染
# ==========================================
st.title(L["title"])
tab1, tab2, tab3, tab4, tab5 = st.tabs([L["tab1"], L["tab2"], L["tab3"], L["tab4"], L["tab5"]])

with tab1:
    col1, col2 = st.columns(2)
    # 這裡加入簡單的統計邏輯... (略過細節以保持結構)
    st.write("📊 目前數據概覽")

with tab4:
    st.subheader(L["tab4"])
    with st.expander(L["add_expander"]):
        with st.form("manual_entry"):
            new_id = st.text_input(L["id_label"], f"MES-{datetime.now().strftime('%y%m%d%H%M')}")
            new_machine = st.text_input(L["machine_label"])
            new_status = st.selectbox(L["status_label"], ["4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง", "9.0 ดำเนินการแล้วเสร็จ"])
            new_detail = st.text_area(L["desc_label"])
            if st.form_submit_button(L["add_btn"]):
                st.session_state.maintenance_records.append({
                    "ลำดับเอกสาร": new_id, "ชื่อเครื่องจักร / อุปกรณ์": new_machine,
                    "สถานะใบแจ้งซ่อม": new_status, "รายละเอียดที่ต้องการดำเนินการ": new_detail
                })
                st.rerun()

    if st.session_state.maintenance_records:
        for i, record in enumerate(st.session_state.maintenance_records):
            cols = st.columns([5, 1])
            cols[0].text(f"[{record['ลำดับเอกสาร']}] {record['ชื่อเครื่องจักร / อุปกรณ์']}")
            if cols[1].button(L["del_btn"], key=f"del_{i}"):
                st.session_state.maintenance_records.pop(i)
                st.rerun()
