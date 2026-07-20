import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ==========================================
# 1. 頁面與 Session 初始化
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維儀表板")

if "maintenance_records" not in st.session_state:
    st.session_state.maintenance_records = []

# ==========================================
# 2. 多語言字典 (擴充版)
# ==========================================
LANG_DICT = {
    "繁體中文": {
        "title": "F-mask 機台預防保養儀表板",
        "tab": ["💡 概覽", "📈 趨勢", "🔮 預測", "📅 維修管理", "🤖 AI 助手"],
        "m1": "🚨 待處理工單", "m2": "⚠️ 高頻機台", "m3": "📊 總紀錄",
        "add_btn": "➕ 新增手動維修日誌", "sub_btn": "確認新增", "del_btn": "🗑️ 刪除",
        "id": "工單編號", "name": "機台名稱", "status": "狀態", "desc": "異常描述"
    },
    "English": {
        "title": "F-mask Predictive Maintenance Dashboard",
        "tab": ["💡 Highlights", "📈 Trends", "🔮 Prediction", "📅 Management", "🤖 AI Assistant"],
        "m1": "🚨 Pending Tasks", "m2": "⚠️ Top Machine", "m3": "📊 Total Records",
        "add_btn": "➕ Add Manual Log", "sub_btn": "Submit", "del_btn": "🗑️ Delete",
        "id": "Running No", "name": "Machine Name", "status": "Status", "desc": "Failure Detail"
    },
    "ภาษาไทย": {
        "title": "F-mask ระบบคาดการณ์การบำรุงรักษา",
        "tab": ["💡 แดชบอร์ดหลัก", "📈 แนวโน้ม", "🔮 คาดการณ์", "📅 การจัดการ", "🤖 ผู้ช่วย AI"],
        "m1": "🚨 งานค้าง", "m2": "⚠️ เครื่องจักรความถี่สูง", "m3": "📊 บันทึกทั้งหมด",
        "add_btn": "➕ เพิ่มบันทึกการซ่อม", "sub_btn": "ยืนยัน", "del_btn": "🗑️ ลบ",
        "id": "หมายเลขเอกสาร", "name": "ชื่อเครื่องจักร", "status": "สถานะ", "desc": "รายละเอียด"
    }
}

with st.sidebar:
    lang = st.radio("Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
    L = LANG_DICT[lang]
    uploaded_file = st.file_uploader("📂 Upload Excel", type=["xlsx"])

# ==========================================
# 3. 資料處理邏輯
# ==========================================
def get_data(file):
    return pd.read_excel(file) if file else pd.DataFrame()

df = get_data(uploaded_file)
# 合併手動紀錄 (簡易示範：將 session 資料轉為 df)
if st.session_state.maintenance_records:
    manual_df = pd.DataFrame(st.session_state.maintenance_records)
    df = pd.concat([df, manual_df], ignore_index=True)

# ==========================================
# 4. 介面呈現
# ==========================================
st.title(L["title"])
tab1, tab2, tab3, tab4, tab5 = st.tabs(L["tab"])

with tab1:
    if not df.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric(L["m1"], len(df)) # 顯示簡單指標
        c2.metric(L["m2"], "F-Mask-01") # 範例數據
        c3.metric(L["m3"], len(df))
        
        # 視覺化圖表：一眼看懂
        st.subheader(L["tab"][1])
        fig = px.bar(df.head(5), x=df.columns[0], y=df.columns[1] if len(df.columns)>1 else None)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please upload data / 請上傳資料 / กรุณาอัปโหลดข้อมูล")

with tab4:
    with st.expander(L["add_btn"]):
        with st.form("entry", clear_on_submit=True):
            nid = st.text_input(L["id"], f"LOG-{datetime.now().strftime('%H%M')}")
            mname = st.text_input(L["name"])
            stat = st.selectbox(L["status"], ["Pending", "Closed"])
            desc = st.text_area(L["desc"])
            if st.form_submit_button(L["sub_btn"]):
                st.session_state.maintenance_records.append({df.columns[0] if not df.empty else "No.": nid, "Name": mname, "Status": stat})
                st.rerun()

    for i, r in enumerate(st.session_state.maintenance_records):
        cols = st.columns([5, 1])
        cols[0].write(f"✅ {r.get('Name', 'N/A')} - {r.get('Status', 'N/A')}")
        if cols[1].button(L["del_btn"], key=f"d_{i}"):
            st.session_state.maintenance_records.pop(i)
            st.rerun()
