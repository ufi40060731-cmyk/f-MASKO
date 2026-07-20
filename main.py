import html
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. 網頁基本設定
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維極簡預測面板")

# 初始化 Session State，用於儲存自行維修紀錄
if "repair_logs" not in st.session_state:
    st.session_state.repair_logs = []

# ==========================================
# 2. 側邊欄控制
# ==========================================
with st.sidebar:
    st.title("⚙️ 控制中心")
    selected_lang = st.radio(
        "🌐 選擇語言 / Language / ภาษา",
        ["繁體中文", "English", "ภาษาไทย"],
    )
    theme_mode = st.radio(
        "🌓 介面主題",
        ["☀️ 白天模式 (Light)", "🌙 黑夜模式 (Dark)"],
    )
    st.divider()
    uploaded_file = st.file_uploader(
        "📂 請上傳 GEM 更換紀錄 Excel (.xlsx)",
        type=["xlsx"],
    )

# 根據黑夜/白天模式動態注入 CSS
if "🌙" in theme_mode:
    bg_color = "#0e1117"
    text_color = "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.05)"
    summary_bg = "rgba(0, 102, 204, 0.20)"
    plotly_template = "plotly_dark"
else:
    bg_color = "#ffffff"
    text_color = "#31333f"
    card_bg = "rgba(0, 0, 0, 0.02)"
    summary_bg = "#f0f7ff"
    plotly_template = "plotly"

st.markdown(
    f"""
<style>
    .stApp {{
        background-color: {bg_color};
        color: {text_color};
    }}
    .stFileUploader {{
        border: 2px dashed #0066cc !important;
        border-radius: 10px;
        padding: 10px;
        background-color: {card_bg};
    }}
    [data-testid="stMetricValue"] {{
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #0066cc;
    }}
    .summary-box {{
        background-color: {summary_bg};
        padding: 16px;
        border-radius: 10px;
        border-left: 6px solid #0066cc;
        margin: 10px 0 16px 0;
        color: {text_color};
        line-height: 1.75;
    }}
</style>
""",
    unsafe_allow_html=True,
)

# ==========================================
# 3. 三語字典設定
# ==========================================
LANG_DICT = {
    "繁體中文": {
        "title": "🛠️ F-mask 機台預防保養與零件預測儀表板",
        "tab_dashboard": "📊 每月追蹤儀表板 (Dashboard)",
        "tab_prediction": "🔮 零件壽命預測機制 (Prediction)",
        "tab_pm_schedule": "📅 標準 PM 週期時程表 (PM Schedule)",
        "kpi_alert": "🚨 建議近期更換/高風險零件",
        "kpi_hotspot": "🔥 頭號高頻故障殺手 (GEM 規律)",
        "kpi_backlog": "⏳ 處理中/未結案工單",
        "action_title": "📋 高頻故障排行榜 ＆ ME 維修對策 (SOP)",
        "action_desc": "系統已自動媒合標準對策，左邊看痛點，右邊看解法。",
        "sop_col": "💡 ME 工程師立即對策 SOP",
        "sop_c1": "🔧 1. 檢查氣缸密封圈是否漏氣；2. 確保氣動三聯件潤滑油充足；3. 定期緊固氣缸固定螺絲。",
        "sop_c2": "🧼 1. 每月清洗或更換真空泵浦濾網；2. 監控泵浦運轉溫度與異音；3. 檢查進出氣管路。",
        "sop_c3": "⚡ 1. 清理感測器表面油污防訊號異常；2. 檢查拖鏈內電纜是否有扭曲磨損；3. 使用電子接點清潔劑。",
        "sop_c4": "⚙️ 1. 執行外觀標準巡檢，清理環境積塵；2. 檢查緊固件是否鬆動；3. 核對操作參數更換備件。",
        "btn_dl": "📥 下載此報表以供主管會議呈報 (CSV)",
        "repair_summary_title": "🧾 自行維修紀錄重點整理",
        "repair_total": "全部紀錄",
        "repair_completed": "已完成",
        "repair_pending": "待處理／追蹤中",
        "latest_record": "最新一筆維修重點",
        "latest_machine": "設備／零件",
        "latest_problem": "發生問題",
        "latest_action": "處理方式",
        "latest_status": "目前狀態",
        "recent_records": "最近 5 筆維修紀錄",
        "repair_form_title": "✍️ 新增自行維修紀錄",
        "repair_machine": "設備／零件名稱",
        "repair_problem": "故障問題",
        "repair_action": "維修處理方式",
        "repair_status": "處理狀態",
        "repair_note": "備註（可不填）",
        "repair_btn": "新增維修紀錄",
        "repair_empty": "目前尚無自行維修紀錄。新增後會自動顯示重點整理。",
        "repair_required": "請至少填寫設備、問題與處理方式。",
        "repair_success": "維修紀錄已新增。",
        "repair_download": "📥 下載自行維修紀錄 (CSV)",
        "status_options": ["✅ 已完成", "🟡 追蹤中", "🔴 尚未解決"],
        "table_time": "時間",
        "table_machine": "設備／零件",
        "table_problem": "問題",
        "table_action": "處理方式",
        "table_status": "狀態",
        "table_note": "備註",
        "prediction_title": "### 🔮 歷史數據自動預測分析",
        "pm_title": "### 📅 F-mask 預防保養 (PM) 標準週期表",
        "no_data": "暫無資料。",
        "upload_hint": "💡 請在左側邊欄上傳您的維修數據 Excel 檔案。",
        "deep_dive": "🔍 點擊展開原始運維歷史明細檔案 (Deep Dive)",
    },
    "English": {
        "title": "🛠️ F-mask Machine PM & Part Prediction Dashboard",
        "tab_dashboard": "📊 Monthly Tracking Dashboard",
        "tab_prediction": "🔮 Part Prediction Mechanism",
        "tab_pm_schedule": "📅 Master PM Schedule Plan",
        "kpi_alert": "🚨 High Risk / Near-Overdue Parts",
        "kpi_hotspot": "🔥 Top Failure Hotspot",
        "kpi_backlog": "⏳ Uncompleted Work Orders",
        "action_title": "📋 Top Failures & ME SOP Actions",
        "action_desc": "SOPs are automatically mapped. Left side shows the problem; right side shows the immediate action.",
        "sop_col": "💡 Immediate ME SOP Action",
        "sop_c1": "🔧 1. Check cylinder seal leaks; 2. Ensure lubricator oil; 3. Tighten fixing screws.",
        "sop_c2": "🧼 1. Clean/replace filter monthly; 2. Monitor pump temperature/noise; 3. Check vacuum lines.",
        "sop_c3": "⚡ 1. Clean sensor oil; 2. Check cable carrier friction; 3. Apply contact cleaner.",
        "sop_c4": "⚙️ 1. General inspection and dusting; 2. Check loose fasteners; 3. Replace parts on schedule.",
        "btn_dl": "📥 Download Report for Executive Review (CSV)",
        "repair_summary_title": "🧾 Self-Repair Record Summary",
        "repair_total": "Total Records",
        "repair_completed": "Completed",
        "repair_pending": "Pending / Monitoring",
        "latest_record": "Latest Repair at a Glance",
        "latest_machine": "Machine / Part",
        "latest_problem": "Problem",
        "latest_action": "Repair Action",
        "latest_status": "Current Status",
        "recent_records": "Latest 5 Repair Records",
        "repair_form_title": "✍️ Add Self-Repair Record",
        "repair_machine": "Machine / Part Name",
        "repair_problem": "Failure / Problem",
        "repair_action": "Repair Action",
        "repair_status": "Status",
        "repair_note": "Note (optional)",
        "repair_btn": "Add Repair Record",
        "repair_empty": "No self-repair records yet. Add one to generate the summary.",
        "repair_required": "Please enter the machine, problem, and repair action.",
        "repair_success": "Repair record added.",
        "repair_download": "📥 Download Self-Repair Records (CSV)",
        "status_options": ["✅ Completed", "🟡 Monitoring", "🔴 Unresolved"],
        "table_time": "Time",
        "table_machine": "Machine / Part",
        "table_problem": "Problem",
        "table_action": "Repair Action",
        "table_status": "Status",
        "table_note": "Note",
        "prediction_title": "### 🔮 Automatic Prediction from Maintenance History",
        "pm_title": "### 📅 F-mask Preventive Maintenance Schedule",
        "no_data": "No data available.",
        "upload_hint": "💡 Upload the maintenance Excel file from the left sidebar.",
        "deep_dive": "🔍 Expand Raw Maintenance History (Deep Dive)",
    },
    "ภาษาไทย": {
        "title": "🛠️ แดชบอร์ดซ่อมบำรุงเชิงป้องกันและคาดการณ์อะไหล่ F-mask",
        "tab_dashboard": "📊 แดชบอร์ดติดตามรายเดือน",
        "tab_prediction": "🔮 กลไกการคาดการณ์อายุอะไหล่",
        "tab_pm_schedule": "📅 แผนตาราง PM มาตรฐาน",
        "kpi_alert": "🚨 อะไหล่ความเสี่ยงสูง/ใกล้ถึงกำหนด",
        "kpi_hotspot": "🔥 จุดเสียบ่อยที่สุด",
        "kpi_backlog": "⏳ ใบงานที่ยังไม่เสร็จ",
        "action_title": "📋 อันดับปัญหาที่พบบ่อยและแนวทาง ME",
        "action_desc": "ระบบจับคู่แนวทางแก้ไขให้อัตโนมัติ ด้านซ้ายคือปัญหา ด้านขวาคือวิธีแก้ไขทันที",
        "sop_col": "💡 แนวทางแก้ไขทันทีสำหรับ ME",
        "sop_c1": "🔧 1. ตรวจสอบซีลกระบอกสูบรั่ว 2. ตรวจสอบน้ำมันหล่อลื่น 3. ขันสกรูยึดให้แน่น",
        "sop_c2": "🧼 1. ล้าง/เปลี่ยนไส้กรองทุกเดือน 2. ตรวจสอบอุณหภูมิและเสียงปั๊ม 3. ตรวจสอบท่อสูญญากาศ",
        "sop_c3": "⚡ 1. ทำความสะอาดเซนเซอร์ 2. ตรวจสายไฟในรางกระดูกงู 3. ใช้น้ำยาทำความสะอาดหน้าสัมผัส",
        "sop_c4": "⚙️ 1. ตรวจสอบและทำความสะอาดฝุ่น 2. ตรวจน็อตหลวม 3. เปลี่ยนอะไหล่ตามกำหนด",
        "btn_dl": "📥 ดาวน์โหลดรายงานสำหรับผู้บริหาร (CSV)",
        "repair_summary_title": "🧾 สรุปบันทึกการซ่อมด้วยตนเอง",
        "repair_total": "บันทึกทั้งหมด",
        "repair_completed": "เสร็จแล้ว",
        "repair_pending": "รอติดตาม/ยังไม่เสร็จ",
        "latest_record": "สรุปงานซ่อมล่าสุด",
        "latest_machine": "เครื่องจักร / อะไหล่",
        "latest_problem": "ปัญหา",
        "latest_action": "วิธีซ่อม",
        "latest_status": "สถานะปัจจุบัน",
        "recent_records": "บันทึกการซ่อมล่าสุด 5 รายการ",
        "repair_form_title": "✍️ เพิ่มบันทึกการซ่อมด้วยตนเอง",
        "repair_machine": "ชื่อเครื่องจักร / อะไหล่",
        "repair_problem": "อาการเสีย / ปัญหา",
        "repair_action": "วิธีการซ่อม",
        "repair_status": "สถานะ",
        "repair_note": "หมายเหตุ (ไม่บังคับ)",
        "repair_btn": "เพิ่มบันทึกการซ่อม",
        "repair_empty": "ยังไม่มีบันทึกการซ่อม เพิ่มข้อมูลแล้วระบบจะสรุปให้อัตโนมัติ",
        "repair_required": "กรุณากรอกชื่อเครื่อง ปัญหา และวิธีซ่อม",
        "repair_success": "เพิ่มบันทึกการซ่อมแล้ว",
        "repair_download": "📥 ดาวน์โหลดบันทึกการซ่อม (CSV)",
        "status_options": ["✅ เสร็จแล้ว", "🟡 กำลังติดตาม", "🔴 ยังไม่แก้ไข"],
        "table_time": "เวลา",
        "table_machine": "เครื่องจักร / อะไหล่",
        "table_problem": "ปัญหา",
        "table_action": "วิธีซ่อม",
        "table_status": "สถานะ",
        "table_note": "หมายเหตุ",
        "prediction_title": "### 🔮 การคาดการณ์อัตโนมัติจากประวัติการซ่อม",
        "pm_title": "### 📅 ตารางบำรุงรักษาเชิงป้องกัน F-mask",
        "no_data": "ยังไม่มีข้อมูล",
        "upload_hint": "💡 โปรดอัปโหลดไฟล์ Excel จากแถบด้านซ้าย",
        "deep_dive": "🔍 เปิดดูประวัติการซ่อมทั้งหมด (Deep Dive)",
    },
}
L = LANG_DICT[selected_lang]

# ==========================================
# 4. 主畫面標題
# 已移除「專案目標／工具使用原則」資訊框
# ==========================================
st.title(L["title"])

# ==========================================
# 5. 資料載入與背後自動分析
# ==========================================
@st.cache_data
def load_data(file):
    df = pd.read_excel(file)

    if "ลำดับเอกสาร" in df.columns:
        df = df[df["ลำดับเอกสาร"].notna()]
        df = df[df["ลำดับเอกสาร"].astype(str).str.strip() != "(Running No)"]

    if "ระยะเวลา (วัน)" in df.columns:
        df["ระยะเวลา (วัน)"] = pd.to_numeric(
            df["ระยะเวลา (วัน)"],
            errors="coerce",
        )

    if "วันที่แจ้งซ่อม" in df.columns:
        df["Parsed_Date"] = pd.to_datetime(
            df["วันที่แจ้งซ่อม"],
            format="%d/%m/%Y %H:%M:%S",
            errors="coerce",
        )
        mask = df["Parsed_Date"].isna()
        df.loc[mask, "Parsed_Date"] = pd.to_datetime(
            df.loc[mask, "วันที่แจ้งซ่อม"],
            errors="coerce",
        )

    return df


def get_repair_log_dataframe():
    """將 Session State 內的維修紀錄轉成顯示用 DataFrame。"""
    if not st.session_state.repair_logs:
        return pd.DataFrame()

    repair_df = pd.DataFrame(st.session_state.repair_logs)
    column_map = {
        "time": L["table_time"],
        "machine": L["table_machine"],
        "problem": L["table_problem"],
        "action": L["table_action"],
        "status": L["table_status"],
        "note": L["table_note"],
    }
    return repair_df.rename(columns=column_map)


if uploaded_file is not None:
    df = load_data(uploaded_file)

    overdue_count = 0
    predict_data = []
    dynamic_pm_plan = []

    if "ชื่อเครื่องจักร / อุปกรณ์" in df.columns and "Parsed_Date" in df.columns:
        counts_series = df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts()
        top_part = counts_series.index[0] if not counts_series.empty else "N/A"
        top_count = counts_series.iloc[0] if not counts_series.empty else 0

        max_failures = counts_series.max() if not counts_series.empty else 1
        grouped = df.dropna(subset=["Parsed_Date"]).groupby(
            "ชื่อเครื่องจักร / อุปกรณ์"
        )

        for name, group in grouped:
            count = len(group)
            mtbf = (
                group["Parsed_Date"].sort_values().diff().dt.days.dropna().mean()
                if count > 1
                else 180
            )
            if pd.isna(mtbf) or mtbf <= 0:
                mtbf = 180

            last_repair = group["Parsed_Date"].max()
            days_left = (
                (last_repair + pd.Timedelta(days=int(mtbf))) - datetime.now()
            ).days

            if days_left <= 30:
                overdue_count += 1

            predict_data.append(
                {
                    "🔧 零件組件名稱 / Part Name": name,
                    "📊 歷史更換次數 / Count": f"{count} 次",
                    "⏳ 平均壽命週期 (MTBF)": f"{round(mtbf, 1)} 天",
                    "🔮 預估下次更換剩餘天數": f"{days_left} 天",
                }
            )

            # 動態 PM 週期分類
            p_lower = str(name).lower()
            if count >= (max_failures * 0.7) or mtbf <= 30:
                cycle = "每週 (Weekly)"
                action = (
                    L["sop_c1"]
                    if ("กระบอก" in p_lower or "cylinder" in p_lower)
                    else "列為最高頻點檢對象，每週檢查氣密與外觀狀態。"
                )
            elif count >= (max_failures * 0.4) or mtbf <= 90:
                cycle = "每月 (Monthly)"
                action = (
                    L["sop_c2"]
                    if ("ปั๊ม" in p_lower or "pump" in p_lower)
                    else "執行標準月度點檢，清潔周邊積塵，確認內部參數。"
                )
            elif mtbf <= 180:
                cycle = "每季 (Quarterly)"
                action = (
                    L["sop_c3"]
                    if ("สาย" in p_lower or "cable" in p_lower)
                    else "每季預防性清潔接點，量測訊號是否衰減。"
                )
            else:
                cycle = "每半年 (Semi-Annually)"
                action = L["sop_c4"]

            dynamic_pm_plan.append(
                {
                    "📅 建議點檢週期": cycle,
                    "🔧 設備組件名稱": name,
                    "📊 歷史故障頻率": f"更換過 {count} 次",
                    "💡 ME工程師標準點檢行動": action,
                }
            )

        pm_df = pd.DataFrame(dynamic_pm_plan)
        cycle_order = {
            "每週 (Weekly)": 0,
            "每月 (Monthly)": 1,
            "每季 (Quarterly)": 2,
            "每半年 (Semi-Annually)": 3,
        }
        if not pm_df.empty:
            pm_df["order"] = pm_df["📅 建議點檢週期"].map(cycle_order)
            pm_df = pm_df.sort_values("order").drop(columns=["order"])
    else:
        counts_series = pd.Series(dtype="int64")
        top_part, top_count = "N/A", 0
        pm_df = pd.DataFrame()

    if "สถานะใบแจ้งซ่อม" in df.columns:
        uncompleted_count = len(
            df[
                ~df["สถานะใบแจ้งซ่อม"]
                .astype(str)
                .str.contains("แล้วเสร็จ|Completed", na=False)
            ]
        )
    else:
        uncompleted_count = 0

    # ==========================================
    # 6. 三大分頁架構
    # ==========================================
    tab1, tab2, tab3 = st.tabs(
        [
            L["tab_dashboard"],
            L["tab_prediction"],
            L["tab_pm_schedule"],
        ]
    )

    # --- TAB 1: 儀表板 ---
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(L["kpi_alert"], f"{overdue_count} 項")
        with col2:
            st.metric(L["kpi_hotspot"], f"{top_part} ({top_count}次)")
        with col3:
            st.metric(L["kpi_backlog"], f"{uncompleted_count} 件")

        # ==========================================
        # 自行維修紀錄重點整理：讓主管一眼看懂
        # ==========================================
        st.divider()
        st.markdown(f"### {L['repair_summary_title']}")

        total_repairs = len(st.session_state.repair_logs)
        completed_repairs = sum(
            1
            for item in st.session_state.repair_logs
            if str(item.get("status", "")).startswith("✅")
        )
        pending_repairs = total_repairs - completed_repairs

        r_col1, r_col2, r_col3 = st.columns(3)
        with r_col1:
            st.metric(L["repair_total"], total_repairs)
        with r_col2:
            st.metric(L["repair_completed"], completed_repairs)
        with r_col3:
            st.metric(L["repair_pending"], pending_repairs)

        if st.session_state.repair_logs:
            latest = st.session_state.repair_logs[0]
            st.markdown(
                f"""
                <div class="summary-box">
                    <strong>📌 {html.escape(L['latest_record'])}</strong><br>
                    <strong>{html.escape(L['latest_machine'])}：</strong>{html.escape(str(latest.get('machine', '')))}<br>
                    <strong>{html.escape(L['latest_problem'])}：</strong>{html.escape(str(latest.get('problem', '')))}<br>
                    <strong>{html.escape(L['latest_action'])}：</strong>{html.escape(str(latest.get('action', '')))}<br>
                    <strong>{html.escape(L['latest_status'])}：</strong>{html.escape(str(latest.get('status', '')))}
                </div>
                """,
                unsafe_allow_html=True,
            )

            repair_df_display = get_repair_log_dataframe()
            st.markdown(f"#### {L['recent_records']}")
            st.dataframe(
                repair_df_display.head(5),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info(L["repair_empty"])

        st.divider()
        st.markdown(f"### {L['action_title']}")
        st.write(L["action_desc"])

        if "ชื่อเครื่องจักร / อุปกรณ์" in df.columns:
            top10_methods = []
            for idx, (p_name, p_count) in enumerate(counts_series.head(10).items()):
                p_lower = str(p_name).lower()
                if "กระบอก" in p_lower or "cylinder" in p_lower:
                    sop_desc = L["sop_c1"]
                elif "ปั๊ม" in p_lower or "pump" in p_lower:
                    sop_desc = L["sop_c2"]
                elif (
                    "สาย" in p_lower
                    or "cable" in p_lower
                    or "chain" in p_lower
                ):
                    sop_desc = L["sop_c3"]
                else:
                    sop_desc = L["sop_c4"]

                top10_methods.append(
                    {
                        "排名 (Rank)": idx + 1,
                        "設備組件名稱 (Part)": p_name,
                        "更換頻率 (次數)": f"{p_count} 次",
                        L["sop_col"]: sop_desc,
                    }
                )

            st.dataframe(
                pd.DataFrame(top10_methods),
                use_container_width=True,
                hide_index=True,
            )

        st.divider()
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            if "ชื่อเครื่องจักร / อุปกรณ์" in df.columns:
                machine_counts_df = counts_series.head(10).rename("count").reset_index()
                fig_m = px.bar(
                    machine_counts_df,
                    x="count",
                    y="ชื่อเครื่องจักร / อุปกรณ์",
                    orientation="h",
                    title="Top 10 GEM 更換率分析圖",
                    template=plotly_template,
                )
                fig_m.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_m, use_container_width=True)

        with c_col2:
            if "อาการเสีย / ปัญหา" in df.columns:
                reason_counts = df["อาการเสีย / ปัญหา"].value_counts().head(5)
                reason_counts_df = reason_counts.rename("count").reset_index()
                fig_r = px.bar(
                    reason_counts_df,
                    x="count",
                    y="อาการเสีย / ปัญหา",
                    orientation="h",
                    title="Top 5 核心故障原因分析",
                    template=plotly_template,
                )
                st.plotly_chart(fig_r, use_container_width=True)

        # ==========================================
        # 結構化自行維修紀錄輸入
        # ==========================================
        st.divider()
        st.markdown(f"### {L['repair_form_title']}")

        with st.form("repair_log_form", clear_on_submit=True):
            form_col1, form_col2 = st.columns(2)
            with form_col1:
                repair_machine = st.text_input(L["repair_machine"])
                repair_problem = st.text_input(L["repair_problem"])
            with form_col2:
                repair_status = st.selectbox(
                    L["repair_status"],
                    L["status_options"],
                )
                repair_note = st.text_input(L["repair_note"])

            repair_action = st.text_area(L["repair_action"], height=100)
            submitted = st.form_submit_button(L["repair_btn"])

        if submitted:
            if repair_machine.strip() and repair_problem.strip() and repair_action.strip():
                st.session_state.repair_logs.insert(
                    0,
                    {
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "machine": repair_machine.strip(),
                        "problem": repair_problem.strip(),
                        "action": repair_action.strip(),
                        "status": repair_status,
                        "note": repair_note.strip(),
                    },
                )
                st.success(L["repair_success"])
                st.rerun()
            else:
                st.warning(L["repair_required"])

        if st.session_state.repair_logs:
            repair_export_df = get_repair_log_dataframe()
            st.download_button(
                L["repair_download"],
                repair_export_df.to_csv(index=False).encode("utf-8-sig"),
                "Self_Repair_Records.csv",
                "text/csv",
            )

        with st.expander(L["deep_dive"]):
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: 預測 ---
    with tab2:
        st.markdown(L["prediction_title"])
        if predict_data:
            pred_df = pd.DataFrame(predict_data)
            st.dataframe(pred_df, use_container_width=True, hide_index=True)
            st.download_button(
                L["btn_dl"],
                pred_df.to_csv(index=False).encode("utf-8-sig"),
                "Part_Prediction_Report.csv",
                "text/csv",
            )
        else:
            st.write(L["no_data"])

    # --- TAB 3: 動態 PM 週期表 ---
    with tab3:
        st.markdown(L["pm_title"])
        if not pm_df.empty:
            st.dataframe(pm_df, use_container_width=True, hide_index=True)
            st.download_button(
                L["btn_dl"],
                pm_df.to_csv(index=False).encode("utf-8-sig"),
                "Master_PM_Schedule.csv",
                "text/csv",
            )
        else:
            st.info(L["no_data"])
else:
    st.info(L["upload_hint"])
