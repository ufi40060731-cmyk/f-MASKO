import pandas as pd
import streamlit as st
import plotly.express as px
import io

st.set_page_config(layout="wide")

selected_lang = st.sidebar.radio("🌐 選擇語言 / Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
theme_mode = st.sidebar.radio("🌓 介面主題", ["☀️ 白天模式 (Light)", "🌙 黑夜模式 (Dark)"])

# 🔧 精準 CSS 修正：徹底解決黑夜模式下 Tabs 標籤頁字體太暗的問題
if "🌙 黑夜模式 (Dark)" in theme_mode:
    plotly_template = "plotly_dark"
    st.markdown('''
        <style>
            /* 1. 主畫面與側邊欄背景塗黑 */
            .stApp, [data-testid="stSidebar"], [data-testid="stSidebarContent"] { background-color: #0E1117 !important; color: #FAFAFA !important; } 

            /* 🌟 核心修正：強力覆蓋標籤頁 (Tabs) 的文字顏色，讓未選中的按鈕變清晰的亮灰色 */
            [data-testid="stTabs"] button p { color: #E2E8F0 !important; font-size: 16px !important; font-weight: 500 !important; }
            [data-testid="stTabs"] button[aria-selected="true"] p { color: #FF4B4B !important; font-weight: bold !important; }

            /* 3. 精準指定：側邊欄的單選按鈕文字變亮白 */
            [data-testid="stSidebar"] div[data-testid="stRadio"] label p { color: #FAFAFA !important; font-weight: bold !important; font-size: 15px !important; }
            [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #FAFAFA !important; }

            /* 4. 側邊欄所有元件的標題、小字、欄位標籤強制變亮 */
            [data-testid="stSidebar"] label p, [data-testid="stSidebar"] .stMarkdown p { color: #FAFAFA !important; font-weight: 500 !important; }
            [data-testid="stSidebar"] div[data-testid="stCaptionContainer"] { color: #E2E8F0 !important; }

            /* 5. 主畫面的上傳文字標題強制變亮白 */
            div[data-testid="stFileUploader"] > label p { color: #FAFAFA !important; font-size: 16px !important; font-weight: 500 !important; }

            /* 6. 底部提示資訊框文字變亮白 */
            .stAlert p { color: #E2E8F0 !important; font-size: 15px !important; }
        </style>
    ''', unsafe_allow_html=True)
else:
    plotly_template = "plotly"
    st.markdown('''
        <style>
            /* 1. 主畫面與側邊欄維持白天白底 */
            .stApp, [data-testid="stSidebar"], [data-testid="stSidebarContent"] { background-color: #FFFFFF !important; color: #31333F !important; } 
            [data-testid="stTabs"] button p { font-size: 16px; }

            /* 2. 白天模式文字顏色規範 */
            [data-testid="stSidebar"] div[data-testid="stRadio"] label p { color: #1E293B !important; font-weight: 500 !important; font-size: 15px !important; }
            [data-testid="stSidebar"] label p, [data-testid="stSidebar"] .stMarkdown p { color: #31333F !important; }
            div[data-testid="stFileUploader"] > label p { color: #31333F !important; font-size: 16px !important; }
            .stAlert p { color: #1E293B !important; font-size: 15px !important; }
        </style>
    ''', unsafe_allow_html=True)

LANG_DICT = {
    "繁體中文": {
        "title": "🛠️ F-mask 機台預防保養(PM)與零件預測儀表板",
        "subtitle": "核心目標：分析 F-mask 維護歷史，建立簡易預測機制，供 ME 每月檢查與主管呈報使用。",
        "upload_label": "請選擇上傳維修數據 Excel 檔案 (.xlsx)",
        "base_date_lbl": "📅 設定當前模擬基準日 (系統已自動定位至最新日期，您可彈性調整)",
        "t_me": "👷 ME 每月檢查與近期工作 (Next 30 Days)",
        "t_analysis": "🔍 零件失效根源與維修對策 (Root Cause & SOP)",
        "t_dashboard": "📊 每月歷史數據追蹤 (Dashboard)",
        "t_pm": "📅 預防保養週期總表 (Master PM Schedule)",
        "t_ai": "🤖 AI 智慧運維助手 (AI Assistant)",
        "focus_title": "🎯 核心維運痛點與風險診斷報告",
        "kpi_total": "總列管零件品項",
        "kpi_overdue": "🚨 目前逾期待換數量",
        "kpi_warning": "⚠️ 兩週內緊迫更換件",
        "filter_title": "🔍 篩選條件 (Filters)",
        "filter_year": "選擇年份",
        "filter_month": "選擇月份",
        "filter_status": "選擇案件狀態",
        "table_title": "📋 原始設備維護歷史明細 (與上方過濾器連動)",
        "col_part": "設備零件名稱",
        "col_remain": "剩餘壽命 (天)",
        "col_next": "預估下次更換日",
        "col_status": "風險狀態",
        "dl_btn": "📥 下載 ME 每月檢查與預測報告 (Excel)",
        "info_tip": "💡 提示：請先上傳 Excel 維修歷史數據檔案以解鎖數據分析功能。"
    },
    "English": {
        "title": "🛠️ F-mask Machine PM & Part Prediction System",
        "subtitle": "Objective: Analyze maintenance history and build predictions for ME monthly check & management reporting.",
        "upload_label": "Upload Maintenance Excel File (.xlsx)",
        "base_date_lbl": "📅 Set Baseline Date (Auto-detected latest date, adjustable)",
        "t_me": "👷 ME Monthly Inspection (Next 30 Days)",
        "t_analysis": "🔍 Root Cause & SOP Analysis",
        "t_dashboard": "📊 Monthly Tracking Dashboard",
        "t_pm": "📅 Master PM Schedule Plan",
        "t_ai": "🤖 AI Assistant & Summary",
        "focus_title": "🎯 Executive Insight Summary",
        "kpi_total": "Total Monitored Parts",
        "kpi_overdue": "🚨 Currently Overdue",
        "kpi_warning": "⚠️ Urgent in 2 Weeks",
        "filter_title": "🔍 Filters",
        "filter_year": "Select Year",
        "filter_month": "Select Month",
        "filter_status": "Select Status",
        "table_title": "📋 Raw Equipment Maintenance History (Filtered)",
        "col_part": "Component Name",
        "col_remain": "Remaining Days",
        "col_next": "Est. Next Replace Date",
        "col_status": "Risk Status",
        "dl_btn": "📥 Download ME Monthly Report (Excel)",
        "info_tip": "💡 Tip: Please upload the Excel file first."
    },
    "ภาษาไทย": {
        "title": "🛠️ ระบบวางแผน PM และคาดการณ์อะไหล่ F-mask",
        "subtitle": "เป้าหมาย: วิเคราะห์ประวัติซ่อมบำรุง สร้างระบบคาดการณ์สําหรับ ME ประจำเดือนและรายงานผู้บริหาร",
        "upload_label": "กรุณาอัปโหลดไฟล์ Excel ข้อมูลการซ่อมบำรุง (.xlsx)",
        "base_date_lbl": "📅 ตั้งเกณฑ์วันที่ปัจจุบัน (ระบบเลือกวันล่าสุดให้ อัปเดตอัตโนมัติ)",
        "t_me": "👷 รายการงานของ ME (30 วันข้างหน้า)",
        "t_analysis": "🔍 การวิเคราะห์สาเหตุและ SOP (Root Cause & SOP)",
        "t_dashboard": "📊 แดชบอร์ดติดตามข้อมูลรายเดือน",
        "t_pm": "📅 ตารางแผน PM รวม (Master PM Schedule)",
        "t_ai": "🤖 ผู้ช่วย AI ประจำเครื่องจักร",
        "focus_title": "🎯 สรุปผลรายงานและการวิเคราะห์ความเสี่ยง",
        "kpi_total": "รายการอะไหล่ทั้งหมด",
        "kpi_overdue": "🚨 อะไหล่ที่เกินกำหนดเปลี่ยน",
        "kpi_warning": "⚠️ อะไหล่ที่ต้องเปลี่ยน in 2 สัปดาห์",
        "filter_title": "🔍 เงื่อนไขการกรอง (Filters)",
        "filter_year": "เลือกปี",
        "filter_month": "เลือกเดือน",
        "filter_status": "เลือกสถานะ",
        "table_title": "📋 รายละเอียดประวัติการซ่อมบำรุงอุปกรณ์ (เชื่อมโยงตามตัวกรอง)",
        "col_part": "ชื่ออุปกรณ์/อะไหล่",
        "col_remain": "จำนวนวันที่เหลือ",
        "col_next": "วันที่คาดว่าต้องเปลี่ยนถัดไป",
        "col_status": "สถานะความเสี่ยง",
        "dl_btn": "📥 ดาวน์โหลดรายงานประจำเดือนของ ME (Excel)",
        "info_tip": "💡 คำแนะนำ: กรุณาอัปโหลดไฟล์ Excel ด้านบนเพื่อเริ่มใช้งาน"
    }
}
L = LANG_DICT[selected_lang]

STATUS_MAP = {
    "9.0 ดำเนินการแล้วเสร็จ": {"繁體中文": "9.0 已完成 (Completed)", "English": "9.0 Completed",
                               "ภาษาไทย": "9.0 ดำเนินการแล้วเสร็จ"},
    "8.2 ผู้แจ้งซ่อมไม่ยอมรับงานซ่อม": {"繁體中文": "8.2 退單/拒絕 (Rejected)", "English": "8.2 Rejected",
                                        "ภาษาไทย": "8.2 ผู้แจ้งซ่อมไม่ยอมรับงานซ่อม"},
    "8.1 รอการตรวจสอบจากผู้แจ้งซ่อม": {"繁體中文": "8.1 等待驗收 (Pending Check)", "English": "8.1 Pending Check",
                                       "ภาษาไทย": "8.1 รอการตรวจสอบจากผู้แจ้งซ่อม"},
    "4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง": {"繁體中文": "4.1 檢修中 (Troubleshooting)",
                                                "English": "4.1 Troubleshooting",
                                                "ภาษาไทย": "4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง"},
    "6.1 รอช่างสั่งอะไหล่": {"繁體中文": "6.1 待叫修備件 (Ordering)", "English": "6.1 Ordering",
                             "ภาษาไทย": "6.1 รอช่างสั่งอะไหล่"},
    "6.3 รออะไหล่": {"繁體中文": "6.3 缺件/等候備件 (Awaiting)", "English": "6.3 Awaiting Parts",
                     "ภาษาไทย": "6.3 รออะไหล่"},
    "6.4 รอฝ่ายผลิตหยุดเครื่องจักรเพื่อซ่อม": {"繁體中文": "6.4 待停機安排 (Waiting Prod)",
                                               "English": "6.4 Waiting Production",
                                               "ภาษาไทย": "6.4 รอฝ่ายผลิตหยุดเครื่องจักรเพื่อซ่อม"},
    "7.0 ดำเนินการซ่อมและรายงานผลปฏิบัติงาน": {"繁體中文": "7.0 維修執行中 (Repairing)", "English": "7.0 Repairing",
                                               "ภาษาไทย": "7.0 ดำเนินการซ่อม和รายงานผลปฏิบัติงาน"},
}

SOP_DATABASE = {
    "เครื่องซีลสาย": {"cause": "【反應應力/機械疲勞】拖鏈彎曲半徑設計不良，高頻率來回擺動導致內部銅線斷裂或短路。",
                      "sop": "1. 機台停機並執行 Lockout/Tagout 安全程序。2. 拆卸舊零件，使用扭力板手緊固新件，並進行單動作動測試。"},
    "เครื่อง AUTO (BODY) 口罩機": {"cause": "【常規機械磨損】達到零件材料疲勞壽命上限，需定期進行硬體潤滑與預防性更換。",
                                   "sop": "1. 機台停機並執行 Lockout/Tagout 安全程序。2. 進行滑軌無塵布清理，塗抹指定潤滑脂。"},
    "ปั๊มลม 空壓機": {"cause": "【常規機械磨損】高負荷連續運轉導致葉片磨損，外部進氣過濾網未清造成內部負壓過載。",
                      "sop": "1. 機台停機斷電。2. 更換進氣濾網並使用專用排氣閥排空水分，測試運轉壓力。"},
    "เครื่อง ดึงยาง 口罩機": {"cause": "【常規機械磨損】拉伸機構反覆作動造成彈簧鬆弛或皮帶磨損。",
                              "sop": "1. 執行 LOTO 程序。2. 檢查皮帶張緊度，更換拉伸彈簧並校正行程參數。"}
}

st.title(L["title"])
st.write(L["subtitle"])

uploaded_file = st.file_uploader(L["upload_label"], type=["xlsx"])


@st.cache_data
def load_and_clean_data(file):
    df = pd.read_excel(file)
    if "ลำดับเอกสาร" in df.columns:
        df = df[df["ลำดับเอกสาร"].notna()]
        df = df[df["ลำดับเอกสาร"].astype(str).str.strip() != "(Running No)"]
    if "ระยะเวลา (วัน)" in df.columns:
        df["ระยะเวลา (วัน)"] = pd.to_numeric(df["ระยะเวลา (วัน)"], errors="coerce")

    if "วันที่แจ้งซ่อม" in df.columns:
        df["Parsed_Date"] = pd.to_datetime(df["วันที่แจ้งซ่อม"], format="%d/%m/%Y %H:%M:%S", errors='coerce')
        mask = df["Parsed_Date"].isna()
        df.loc[mask, "Parsed_Date"] = pd.to_datetime(df.loc[mask, "วันที่แจ้งซ่อม"], errors='coerce')

        def extract_year(x):
            val = str(x).strip()
            if "/" in val:
                return val.split("/")[-1].split()[0]
            elif "-" in val:
                return val.split("-")[0]
            return "Unknown"

        df["年份_data"] = df["วันที่แจ้งซ่อม"].apply(extract_year).astype(str)
        df["月份_data"] = df["Parsed_Date"].apply(lambda dt: f"{dt.month:02d}" if pd.notna(dt) else "Unknown").astype(
            str)
    else:
        df["Parsed_Date"], df["年份_data"], df["月份_data"] = pd.NaT, "Unknown", "Unknown"
    return df


if uploaded_file is not None:
    try:
        df = load_and_clean_data(uploaded_file)

        if "สถานะใบแจ้งซ่อม" in df.columns:
            df["狀態_display"] = df["สถานะใบแจ้งซ่อม"].apply(
                lambda x: STATUS_MAP.get(str(x).strip(), {}).get(selected_lang, x) if pd.notna(x) else x)
        else:
            df["狀態_display"] = "Unknown"

        if "ชื่อเครื่องจักร / อุปกรณ์" in df.columns and not df["Parsed_Date"].isna().all():
            max_date_in_data = df["Parsed_Date"].max()
            st.sidebar.markdown(f"### {L['filter_title']}")
            base_date = st.sidebar.date_input(L["base_date_lbl"], value=max_date_in_data.date())
            base_date_t = pd.Timestamp(base_date)

            available_years = sorted([y for y in df["年份_data"].unique().tolist() if y not in ["Unknown", ""]])
            available_months = sorted([m for m in df["月份_data"].unique().tolist() if m not in ["Unknown", ""]])
            available_status = df["狀態_display"].dropna().unique().tolist()

            selected_years = st.sidebar.multiselect(L["filter_year"], options=available_years,
                                                    default=available_years[:1] if available_years else [])
            selected_months = st.sidebar.multiselect(L["filter_month"], options=available_months,
                                                     default=available_months)
            selected_status = st.sidebar.multiselect(L["filter_status"], options=available_status,
                                                     default=available_status)

            if not selected_years: selected_years = available_years
            if not selected_months: selected_months = available_months
            if not selected_status: selected_status = available_status

            filtered_df = df[
                df["年份_data"].isin(selected_years) & df["月份_data"].isin(selected_months) & df["狀態_display"].isin(
                    selected_status)]

            predict_data = []
            grouped = df.dropna(subset=["Parsed_Date"]).groupby("ชื่อเครื่องจักร / อุปกรณ์")

            for name, group in grouped:
                group = group.sort_values("Parsed_Date")
                count = len(group)

                if count > 1:
                    mtbf = group["Parsed_Date"].diff().dt.days.dropna().mean()
                else:
                    mtbf = 90
                if pd.isna(mtbf) or mtbf <= 0: mtbf = 90

                last_repair = group["Parsed_Date"].max()
                next_replace = last_repair + pd.Timedelta(days=int(mtbf))
                remaining_days = (next_replace - base_date_t).days

                if remaining_days < 0:
                    status = "🚨 已逾期 (Overdue)"
                elif remaining_days <= 14:
                    status = "⚠️ 高風險 (🚨 Next 2 Weeks)"
                else:
                    status = "✅ 正常 (Safe)"

                sop_info = SOP_DATABASE.get(name, {
                    "cause": "【常規機械磨損】達到零件材料疲勞壽命上限，需定期進行硬體潤滑與預防性更換。",
                    "sop": "1. 機台停機並執行 Lockout/Tagout 安全程序。2. 拆卸舊零件，更換新備件並進行功能驗證。"
                })

                predict_data.append({
                    L["col_part"]: name,
                    "歷史更換次數": count,
                    "預估壽命週期 (MTBF天)": int(round(mtbf, 0)),
                    "前次更換維修日": last_repair.strftime('%Y-%m-%d'),
                    L["col_next"]: next_replace.strftime('%Y-%m-%d'),
                    L["col_remain"]: remaining_days,
                    L["col_status"]: status,
                    "失效根源原因分析 (Root Cause)": sop_info["cause"],
                    "建議更換與保養方法 (SOP)": sop_info["sop"]
                })

            predict_df = pd.DataFrame(predict_data).sort_values(by=L["col_remain"])

            tab_me, tab_analysis, tab_dashboard, tab_pm, tab_ai = st.tabs([
                L["t_me"], L["t_analysis"], L["t_dashboard"], L["t_pm"], L["t_ai"]
            ])

            with tab_me:
                st.subheader(f"📅 未來 30 天內急需執行保養更換清單 (基準日: {base_date_t.strftime('%Y-%m-%d')})")
                st.write("此面板僅顯示「已過期」或「未來 30 天內壽命到期」的品項，供設備工程師排定本月工作。")

                me_action_df = predict_df[predict_df[L["col_remain"]] <= 30]

                if not me_action_df.empty:
                    display_cols = [L["col_part"], L["col_status"], L["col_remain"], L["col_next"], "前次更換維修日",
                                    "預估壽命週期 (MTBF天)"]
                    st.dataframe(me_action_df[display_cols], use_container_width=True, hide_index=True)

                    buffer = io.BytesIO()
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        me_action_df.to_excel(writer, index=False, sheet_name='ME_Monthly_Check')
                    buffer.seek(0)
                    st.download_button(label=L["dl_btn"], data=buffer,
                                       file_name=f"ME_Report_{base_date_t.strftime('%Y%m')}.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                else:
                    st.success("✅ 目前狀態良好，未來 30 天內無即將到期的零組件。")

            with tab_analysis:
                st.subheader(L["t_analysis"])
                st.write("此區塊直接連結對應的 SOP 安全程序，提供日常巡檢與工程師報告快速查閱。")
                analysis_display = predict_df[
                    [L["col_part"], L["col_status"], "失效根源原因分析 (Root Cause)", "建議更換與保養方法 (SOP)"]]
                st.dataframe(analysis_display, use_container_width=True, hide_index=True)

            with tab_dashboard:
                st.subheader(L["focus_title"])

                k1, k2, k3 = st.columns(3)
                with k1:
                    st.metric(L["kpi_total"], len(predict_df))
                with k2:
                    overdue_cnt = len(predict_df[predict_df[L["col_remain"]] < 0])
                    st.metric(L["kpi_overdue"], f"{overdue_cnt} 項",
                              delta=f"{overdue_cnt} 需立即處理" if overdue_cnt > 0 else None, delta_color="inverse")
                with k3:
                    warning_cnt = len(
                        predict_df[(predict_df[L["col_remain"]] >= 0) & (predict_df[L["col_remain"]] <= 14)])
                    st.metric(L["kpi_warning"], f"{warning_cnt} 項")

                st.write("---")
                g1, g2 = st.columns(2)
                with g1:
                    status_counts = predict_df[L["col_status"]].value_counts().reset_index()
                    status_counts.columns = ["風險等級", "零件品項數"]
                    fig_p = px.pie(status_counts, values="零件品項數", names="風險等級", title="🎯 整體零件風險比例分佈",
                                   hole=0.4, color_discrete_map={"🚨 已逾期 (Overdue)": "#FF4B4B",
                                                                 "⚠️ 高風險 (🚨 Next 2 Weeks)": "#FFA500",
                                                                 "✅ 正常 (Safe)": "#00B050"}, template=plotly_template)
                    st.plotly_chart(fig_p, use_container_width=True)
                with g2:
                    if "ชื่อเครื่องจักร / อุปกรณ์" in filtered_df.columns and not filtered_df.empty:
                        machine_counts = filtered_df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts().reset_index().head(10)
                        machine_counts.columns = ["設備零件名稱", "報修次數"]
                        fig_m = px.bar(machine_counts, x="報修次數", y="設備零件名稱", orientation="h",
                                       title="📌 篩選期間報修排行 Top 10", template=plotly_template)
                        fig_m.update_layout(yaxis={"categoryorder": "total ascending"})
                        st.plotly_chart(fig_m, use_container_width=True)

                st.write("---")
                st.subheader(L["table_title"])
                if not filtered_df.empty:
                    raw_cols_to_show = ["ลำดับเอกสาร", "วันที่แจ้งซ่อม", "ชื่อเครื่องจักร / อุปกรณ์", "狀態_display",
                                        "อาการเสีย/ปัญหาที่พบ", "ระยะเวลา (วัน)"]
                    existing_cols = [c for c in raw_cols_to_show if c in filtered_df.columns]
                    st.dataframe(filtered_df[existing_cols], use_container_width=True, hide_index=True)
                else:
                    st.warning("⚠️ 當前篩選條件下無歷史報修數據，請調整左側的年份或月份。")

            with tab_pm:
                st.subheader(L["t_pm"])
                st.write("完整的 F-mask 列管零組件動態 MTBF 壽命預估數據總庫：")
                st.dataframe(predict_df, use_container_width=True, hide_index=True)

            with tab_ai:
                ai_left, ai_right = st.columns([4, 6])
                with ai_left:
                    st.success(
                        f"### 📊 全上傳資料整理重點\n\n"
                        f"* 📈 **總列管品項**：共計算 **{len(predict_df)}** 核心零件。\n"
                        f"* 🚨 **當前逾期危機**：目前有 **{overdue_cnt}** 項已超出 MTBF 壽命。\n"
                        f"* 🏆 **篩選筆數總計**：目前過濾器範圍內共有 **{len(filtered_df)}** 筆報修紀錄。"
                    )
                with ai_right:
                    if "messages" not in st.session_state:
                        st.session_state.messages = [{"role": "assistant",
                                                      "content": "你好！我是 F-mask 智慧運維助手。原始數據與過濾圖表已在中間分頁完整復原，有任何關於報告內容的問題都可以問我！"}]

                    chat_box = st.container(height=350)
                    with chat_box:
                        for m in st.session_state.messages:
                            with st.chat_message(m["role"]): st.write(m["content"])

                    if user_in := st.chat_input("請輸入維修技術或報告相關問題..."):
                        with st.chat_message("user"): st.write(user_in)
                        st.session_state.messages.append({"role": "user", "content": user_in})

                        with st.chat_message("assistant"):
                            ans = f"收到！目前您上傳的原始維護歷史中共有 {len(df)} 筆總紀錄。篩選條件下顯示的故障機王已更新至『每月歷史數據追蹤』分頁下方，方便您隨時查閱或呈報主管。"
                            st.write(ans)
                            st.session_state.messages.append({"role": "assistant", "content": ans})
                        st.rerun()

        else:
            st.error(
                "❌ 上傳的 Excel 格式不符，找不到『ชื่อเครื่องจักร / อุปกรณ์』（設備名稱）或『วันที่แจ้งซ่อม』（報修日期）欄位。")
    except Exception as e:
        st.error(f"解析 Excel 時發生非預期錯誤: {e}")
else:
    st.info(L["info_tip"])
