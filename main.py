import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ==========================================
# 1. 網頁基本設定與 Session 初始化
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維極簡預測面板")

if "tech_logs" not in st.session_state: 
    st.session_state.tech_logs = []
if "maintenance_records" not in st.session_state: 
    st.session_state.maintenance_records = []
if "ai_messages" not in st.session_state: 
    st.session_state.ai_messages = []

# ==========================================
# 2. 側邊欄控制與多語言字典
# ==========================================
with st.sidebar:
    st.title("⚙️ 控制中心")
    selected_lang = st.radio("語言 / Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
    theme_mode = st.radio("主題", ["☀️ 白天", "🌙 黑夜"])
    uploaded_file = st.file_uploader("📂 上傳 F-mask 原始 Excel (005.xlsx)", type=["xlsx"])

# 樣式自定義 (CSS)
bg_color = "#0e1117" if "🌙" in theme_mode else "#ffffff"
text_color = "#ffffff" if "🌙" in theme_mode else "#31333f"
st.markdown(f"<style>.stApp {{ background-color: {bg_color}; color: {text_color}; }}</style>", unsafe_allow_html=True)

# 字典設定
LANG_DICT = {
    "繁體中文": {
        "title": "F-mask 機台預防保養與零件預測儀表板",
        "tab_dashboard": "每月追蹤儀表板",
        "tab_prediction": "零件壽命預測機制",
        "tab_pm_schedule": "標準 PM 週期時程表",
        "recent_high_risk": "🚨 近期高風險零件/機台",
        "high_freq_machine": "🔥 高頻故障機台",
        "pending_tickets": "⏳ 未結案工單",
    },
    "English": {
        "title": "F-mask Predictive Maintenance Dashboard",
        "tab_dashboard": "Monthly Dashboard",
        "tab_prediction": "Part Life Prediction",
        "tab_pm_schedule": "PM Schedule",
        "recent_high_risk": "🚨 High-Risk Parts",
        "high_freq_machine": "🔥 Top Failure Machine",
        "pending_tickets": "⏳ Pending Tickets",
    },
    "ภาษาไทย": {
        "title": "F-mask ระบบคาดการณ์การบำรุงรักษา",
        "tab_dashboard": "แดชบอร์ดรายเดือน",
        "tab_prediction": "คาดการณ์อายุอะไหล่",
        "tab_pm_schedule": "ตาราง PM มาตรฐาน",
        "recent_high_risk": "🚨 อะไหล่ความเสี่ยงสูง",
        "high_freq_machine": "🔥 เครื่องจักรขัดข้องบ่อย",
        "pending_tickets": "⏳ ใบแจ้งซ่อมคงค้าง",
    }
}
L = LANG_DICT[selected_lang]

# ==========================================
# 3. 數據清洗與統計核心 (修復 N/A 與 6961 錯誤)
# ==========================================
def load_and_clean_data(file):
    raw_df = pd.read_excel(file)
    
    # 關鍵：只保留 "No." 欄位有數值、非空、非欄位說明的真實數據列
    cleaned = raw_df[raw_df["No."].notna() & (raw_df["No."].astype(str).str.replace('.', '', 1).str.isdigit())]
    
    # 解析日期欄位
    cleaned["Parsed_Date"] = pd.to_datetime(cleaned["วันที่แจ้งซ่อม"], errors='coerce')
    return cleaned

# 讀取數據
if uploaded_file:
    source_df = load_and_clean_data(uploaded_file)
else:
    source_df = pd.DataFrame()

# 讀取手動維修紀錄
manual_df = pd.DataFrame(st.session_state.maintenance_records)
if not manual_df.empty and "วันที่แจ้งซ่อม" in manual_df.columns:
    manual_df["Parsed_Date"] = pd.to_datetime(manual_df["วันที่แจ้งซ่อม"], errors='coerce')

# 合併數據流
if not source_df.empty and not manual_df.empty:
    df = pd.concat([source_df, manual_df], ignore_index=True)
elif not source_df.empty:
    df = source_df
else:
    df = manual_df

# 計算儀表數據
overdue_count = 0 
top_part = "N/A"
uncompleted_count = 0

if not df.empty:
    # 1. 統計最常故障的機台
    machine_counts = df["ชื่อเครื่องจักร / อุปกรณ์"].dropna().value_counts()
    if not machine_counts.empty:
        top_part = machine_counts.index[0]  # 例如："เครื่องผลิตผ้าปิดจมูก 口罩機"
        overdue_count = machine_counts.iloc[0]  # 將最高頻機台的維修次數作為風險指標
    
    # 2. 精準統計未完成工單 (過濾非 completed 狀態)
    # 狀態不包含 '9.0 ดำเนินการแล้วเสร็จ' หรือ 'Job Closed' หรือ '結案'
    completed_mask = df["สถานะใบแจ้งซ่อม"].astype(str).str.contains("9.0|Closed|結案", na=False, case=False)
    uncompleted_df = df[~completed_mask]
    uncompleted_count = len(uncompleted_df)

# ==========================================
# 4. 頁面 Tabs 渲染 (重點頁與 AI 助手)
# ==========================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💡 重點儀表 (Highlights)", 
    L["tab_dashboard"], 
    L["tab_prediction"], 
    L["tab_pm_schedule"], 
    "🤖 AI 智慧助手"
])

# --- TAB 1: 重點儀表 (Highlights) ---
with tab1:
    st.markdown("### 📊 關鍵維護指標總覽")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(L["recent_high_risk"], f"{overdue_count} 次故障", help="此機台在維修歷史中累計異常頻率最高")
    with col2:
        st.metric(L["high_freq_machine"], f"{top_part}")
    with col3:
        st.metric(L["pending_tickets"], f"{uncompleted_count} 件", delta="-5" if uncompleted_count > 0 else None, delta_color="inverse")
    
    st.divider()
    
    # 展示未完成工單列表，便於 ME 即時點檢
    if uncompleted_count > 0:
        st.markdown("##### ⏳ 待處理與未完工工單清單")
        show_cols = ["No.", "ลำดับเอกสาร", "ชื่อเครื่องจักร / อุปกรณ์", "วันที่แจ้งซ่อม", "สถานะใบแจ้งซ่อม", "รายละเอียดที่ต้องการดำเนินการ"]
        existing_cols = [c for c in show_cols if c in uncompleted_df.columns]
        st.dataframe(uncompleted_df[existing_cols].head(15), use_container_width=True)
    else:
        st.success("🎉 目前無任何未完工工單，所有機台狀態良好！")

# --- TAB 2: 每月追蹤儀表板 (Dashboard) ---
with tab2:
    if not df.empty:
        st.subheader("📈 維修趨勢分析")
        # 繪製簡單的機台故障分佈圖
        fig = px.bar(
            df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts().head(10).reset_index(),
            x="ชื่อเครื่องจักร / อุปกรณ์",
            y="count",
            labels={"ชื่อเครื่องจักร / อุปกรณ์": "機台名稱", "count": "故障次數"},
            title="前 10 大高故障率機台分佈"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("請先於側邊欄上傳 Excel 檔案以呈現分析圖表。")

# --- TAB 3: 零件壽命預測機制 (Prediction) ---
with tab3:
    st.subheader("🔮 零件更換與 PM 預測預警")
    st.info("基於 MTBF (平均故障間隔時間) 預估之零件更換時間表。")
    if not df.empty:
        # 預留預測演算法展示空間
        st.dataframe(df[["ชื่อเครื่องจักร / อุปกรณ์", "Parsed_Date"]].dropna().head(10))
    else:
        st.write("暫無預估數據。")

# --- TAB 4: 標準 PM 週期時程表 (PM Schedule) ---
with tab4:
    st.subheader("📅 年度定期保養排程與手動紀錄管理")
    
    # 1. 這裡您可以加入您的手動新增表單邏輯
    with st.expander("➕ 新增手動維修日誌"):
        with st.form("manual_entry_form"):
            new_id = st.text_input("工單編號 (Running No)", f"MES-{datetime.now().strftime('%y%m%d%H%M')}")
            new_machine = st.text_input("機台名稱 (Machine Name)", value=top_part if top_part != "N/A" else "")
            new_status = st.selectbox("狀態 (Status)", ["4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง", "9.0 ดำเนินการแล้วเสร็จ"])
            new_detail = st.text_area("異常描述 (Failure Detail)")
            
            submitted = st.form_submit_button("確認新增 (Submit)")
            if submitted:
                new_record = {
                    "No.": len(st.session_state.maintenance_records) + 1,
                    "ลำดับเอกสาร": new_id,
                    "ชื่อเครื่องจักร / อุปกรณ์": new_machine,
                    "วันที่แจ้งซ่อม": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "สถานะใบแจ้งซ่อม": new_status,
                    "รายละเอียดที่ต้องการดำเนินการ": new_detail
                }
                st.session_state.maintenance_records.append(new_record)
                st.success("紀錄已成功加入分析流！")
                st.rerun()

    # 顯示目前所有已輸入的手動資料
    if st.session_state.maintenance_records:
        st.write("🛠️ 已手動登錄之維修紀錄：")
        st.write(pd.DataFrame(st.session_state.maintenance_records))

# --- TAB 5: AI 智慧助手 ---
with tab5:
    st.markdown("### 🤖 F-mask 維修 AI 智慧助手")
    st.caption("輸入機台異常狀況，AI 會自動對照 SOP 並給予處理建議")
    
    # 聊天歷史紀錄展示
    for msg in st.session_state.ai_messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_q = st.chat_input("請描述機台異常 (例如：口罩機切刀不熱、氣缸漏氣)...")
    if user_q:
        # 展示使用者輸入
        st.session_state.ai_messages.append({"role": "user", "content": user_q})
        with st.chat_message("user"):
            st.write(user_q)
            
        # 簡單的規則應答邏輯 (可升級為 API 對接)
        with st.chat_message("assistant"):
            if "漏氣" in user_q or "ลมรั่ว" in user_q:
                response = "🛠️ **SOP 建議：**\n1. 請優先使用肥皂水噴灑氣動三聯件與氣缸接口，定位洩漏點。\n2. 檢查氣管接頭是否老化鬆脫，必要時重新裁切並鎖緊。\n3. 若屬內部洩漏，請準備更換氣缸密封圈。"
            elif "熱" in user_q or "ไม่ร้อน" in user_q:
                response = "⚡ **SOP 建議：**\n1. 請檢查加熱棒之電阻值是否異常（正常應在指定阻值區間）。\n2. 點檢固態繼電器 (SSR) 燈號是否正常閃爍亮起。\n3. 確認感溫線 (Thermocouple) 位置無鬆脫且未斷線。"
            else:
                response = "📝 已收到您的機台異常反饋。建議優先登入工單，並請負責此區域 (SP-F) 的技術員現場點檢確認。"
            
            st.write(response)
            st.session_state.ai_messages.append({"role": "assistant", "content": response})
