import html
from datetime import datetime
from pathlib import Path
from uuid import uuid4

import pandas as pd
import plotly.express as px
import streamlit as st

# ==========================================
# 1. 網頁基本設定
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維極簡預測面板")

# 自行維修紀錄會儲存在程式同層的 data/manual_maintenance_records.csv
DATA_DIR = Path(__file__).resolve().parent / "data"
MANUAL_RECORDS_FILE = DATA_DIR / "manual_maintenance_records.csv"
REPAIR_LOG_COLUMNS = ["id", "time", "machine", "problem", "action", "status", "note"]


def load_saved_repair_logs():
    """讀取已儲存的自行維修紀錄；檔案不存在時回傳空清單。"""
    if not MANUAL_RECORDS_FILE.exists():
        return []

    try:
        saved_df = pd.read_csv(MANUAL_RECORDS_FILE, dtype=str).fillna("")
    except (OSError, pd.errors.EmptyDataError, pd.errors.ParserError):
        return []

    records = []
    for item in saved_df.to_dict("records"):
        record = {column: str(item.get(column, "")) for column in REPAIR_LOG_COLUMNS}
        if not record["id"]:
            record["id"] = uuid4().hex
        records.append(record)
    return records


def save_repair_logs():
    """將目前的自行維修紀錄寫入 CSV，讓新增與刪除結果可以保留。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    save_df = pd.DataFrame(st.session_state.repair_logs)
    save_df = save_df.reindex(columns=REPAIR_LOG_COLUMNS)
    save_df.to_csv(MANUAL_RECORDS_FILE, index=False, encoding="utf-8-sig")


# 初始化 Session State，優先載入已保存的自行維修紀錄
if "repair_logs" not in st.session_state:
    st.session_state.repair_logs = load_saved_repair_logs()

# 相容舊版紀錄：補上唯一識別碼，避免同名紀錄刪錯
_repair_log_migrated = False
for _repair_log in st.session_state.repair_logs:
    if not _repair_log.get("id"):
        _repair_log["id"] = uuid4().hex
        _repair_log_migrated = True
if _repair_log_migrated:
    save_repair_logs()

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
    .glance-hero {{
        padding: 20px 22px;
        border-radius: 14px;
        margin: 8px 0 18px 0;
        border: 1px solid rgba(128, 128, 128, 0.22);
    }}
    .glance-critical {{
        background: rgba(220, 53, 69, 0.12);
        border-left: 8px solid #dc3545;
    }}
    .glance-warning {{
        background: rgba(255, 152, 0, 0.14);
        border-left: 8px solid #ff9800;
    }}
    .glance-normal {{
        background: rgba(25, 135, 84, 0.12);
        border-left: 8px solid #198754;
    }}
    .glance-label {{
        font-size: 0.86rem;
        opacity: 0.72;
        margin-bottom: 4px;
    }}
    .glance-status {{
        font-size: 1.75rem;
        font-weight: 800;
        margin-bottom: 10px;
    }}
    .glance-action {{
        font-size: 1.08rem;
        font-weight: 650;
        line-height: 1.55;
    }}
    .key-card {{
        min-height: 132px;
        padding: 16px;
        border-radius: 12px;
        background-color: {card_bg};
        border: 1px solid rgba(128, 128, 128, 0.22);
        margin-bottom: 12px;
    }}
    .key-card-title {{
        font-size: 0.88rem;
        opacity: 0.72;
        margin-bottom: 8px;
        font-weight: 700;
    }}
    .key-card-value {{
        font-size: 1.42rem;
        font-weight: 800;
        line-height: 1.25;
        margin-bottom: 7px;
    }}
    .key-card-note {{
        font-size: 0.90rem;
        line-height: 1.35;
        opacity: 0.82;
    }}
    .compact-strip {{
        padding: 13px 16px;
        border-radius: 10px;
        background-color: {summary_bg};
        border-left: 5px solid #0066cc;
        line-height: 1.55;
        margin: 7px 0;
    }}

    .issue-repair-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin: 12px 0 18px 0;
    }}
    .summary-panel {{
        padding: 18px;
        border-radius: 14px;
        border: 1px solid rgba(128, 128, 128, 0.24);
        background-color: {card_bg};
        min-height: 330px;
    }}
    .problem-panel {{ border-top: 7px solid #dc3545; }}
    .repair-panel {{ border-top: 7px solid #198754; }}
    .panel-title {{
        font-size: 1.28rem;
        font-weight: 850;
        margin-bottom: 13px;
    }}
    .point-row {{
        padding: 12px 13px;
        margin: 9px 0;
        border-radius: 10px;
        background: rgba(128, 128, 128, 0.08);
        border-left: 5px solid rgba(128, 128, 128, 0.50);
        line-height: 1.45;
    }}
    .point-row strong {{ font-size: 1.04rem; }}
    .point-red {{ border-left-color: #dc3545; }}
    .point-orange {{ border-left-color: #ff9800; }}
    .point-green {{ border-left-color: #198754; }}
    .point-blue {{ border-left-color: #0066cc; }}
    .priority-line {{
        padding: 15px 18px;
        border-radius: 12px;
        background: rgba(220, 53, 69, 0.10);
        border: 1px solid rgba(220, 53, 69, 0.35);
        margin: 8px 0 16px 0;
        font-size: 1.10rem;
        line-height: 1.55;
    }}
    .one-look-title {{
        font-size: 1.05rem;
        font-weight: 800;
        margin: 18px 0 8px 0;
    }}
    @media (max-width: 900px) {{
        .issue-repair-grid {{ grid-template-columns: 1fr; }}
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
        "tab_summary": "🔧 維修重點＆問題點",
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
        "repair_manage_title": "🗑️ 選取並刪除維修紀錄",
        "repair_manage_help": "在表格左側勾選要刪除的紀錄，可一次刪除多筆。",
        "repair_select_col": "選取刪除",
        "repair_delete_btn": "🗑️ 刪除選取紀錄",
        "repair_delete_none": "請先勾選至少一筆維修紀錄。",
        "repair_delete_success": "已刪除 {count} 筆維修紀錄。",
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
        "summary_title": "📝 主管重點整理分析",
        "summary_desc": "系統自動整理高風險零件、故障熱點、未結案工單與 PM 優先事項，讓主管快速掌握目前狀況。",
        "summary_total_records": "歷史維修紀錄",
        "summary_risk_parts": "30 天內需處理",
        "summary_top_issue": "最高頻故障原因",
        "summary_backlog_rate": "未結案率",
        "summary_conclusion": "📌 系統重點結論",
        "summary_priority_title": "🚨 優先處理清單",
        "summary_no_risk": "目前沒有預估 30 天內需更換或已逾期的零件。",
        "summary_pm_focus": "📅 PM 執行重點",
        "summary_self_repair": "🧾 自行維修紀錄狀態",
        "summary_no_issue": "無故障原因資料",
        "summary_line_risk": "目前有 {count} 項零件預估於 30 天內到期或已逾期，應列為優先處理。",
        "summary_line_hotspot": "更換頻率最高的設備／零件為「{part}」，歷史共 {count} 次。",
        "summary_line_reason": "最常見的故障原因為「{reason}」，共 {count} 筆。",
        "summary_line_backlog": "未結案工單共 {count} 件，占全部紀錄 {rate:.1f}%。",
        "summary_line_pm": "建議 PM 配置：每週 {weekly} 項、每月 {monthly} 項、每季 {quarterly} 項、每半年 {semi} 項。",
        "summary_line_self": "自行維修紀錄共 {total} 筆，其中已完成 {completed} 筆、待追蹤 {pending} 筆。",
        "summary_col_status": "風險狀態",
        "summary_col_part": "設備／零件",
        "summary_col_count": "歷史次數",
        "summary_col_mtbf": "平均週期 (天)",
        "summary_col_days": "距預估更換 (天)",
        "summary_overdue": "🔴 已逾期",
        "summary_due_soon": "🟠 30 天內到期",
        "glance_title": "👀 一眼重點",
        "glance_caption": "紅色先做、橘色排程、綠色正常。",
        "overall_status": "目前整體狀態",
        "status_critical": "🔴 立即處理",
        "status_warning": "🟠 需要注意",
        "status_normal": "🟢 狀況正常",
        "main_action": "最優先動作",
        "focus_header": "主管只需要先看這 4 件事",
        "focus_urgent": "第一優先",
        "focus_hotspot": "高頻故障零件",
        "focus_issue": "最常見故障",
        "focus_backlog": "未結案工單",
        "no_urgent_action": "目前沒有逾期或 30 天內到期的零件。",
        "urgent_action_template": "先處理「{part}」，距預估更換日剩 {days} 天。",
        "overdue_action_template": "立即處理「{part}」，已逾期 {days} 天。",
        "hotspot_template": "歷史更換 {count} 次",
        "issue_template": "共出現 {count} 筆",
        "backlog_template": "占全部紀錄 {rate:.1f}%",
        "pm_quick": "📅 PM 重點：每週 {weekly} 項｜每月 {monthly} 項｜每季 {quarterly} 項｜每半年 {semi} 項",
        "self_repair_quick": "🧾 自行維修：完成 {completed} 筆｜待追蹤 {pending} 筆",
        "latest_pending": "最新待追蹤：{machine}｜{problem}",
        "no_pending_repairs": "目前沒有待追蹤的自行維修紀錄。",
        "details_expander": "🔍 查看完整分析與優先處理明細",
        "priority_action": "建議動作",
        "action_replace_now": "立即確認並安排更換",
        "action_schedule_7d": "7 天內安排點檢／備料",
        "action_schedule_30d": "本月安排點檢",
    },
    "English": {
        "title": "🛠️ F-mask Machine PM & Part Prediction Dashboard",
        "tab_dashboard": "📊 Monthly Tracking Dashboard",
        "tab_prediction": "🔮 Part Prediction Mechanism",
        "tab_pm_schedule": "📅 Master PM Schedule Plan",
        "tab_summary": "🔧 Maintenance & Issues",
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
        "repair_manage_title": "🗑️ Select and Delete Repair Records",
        "repair_manage_help": "Tick the records in the left column. Multiple records can be deleted at once.",
        "repair_select_col": "Select",
        "repair_delete_btn": "🗑️ Delete Selected Records",
        "repair_delete_none": "Select at least one repair record first.",
        "repair_delete_success": "Deleted {count} repair record(s).",
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
        "summary_title": "📝 Management Key Summary",
        "summary_desc": "The system automatically summarizes high-risk parts, failure hotspots, open work orders, and PM priorities for quick review.",
        "summary_total_records": "Maintenance Records",
        "summary_risk_parts": "Due Within 30 Days",
        "summary_top_issue": "Top Failure Cause",
        "summary_backlog_rate": "Open-Order Rate",
        "summary_conclusion": "📌 Key Findings",
        "summary_priority_title": "🚨 Priority Action List",
        "summary_no_risk": "No parts are currently overdue or predicted to require replacement within 30 days.",
        "summary_pm_focus": "📅 PM Execution Focus",
        "summary_self_repair": "🧾 Self-Repair Record Status",
        "summary_no_issue": "No failure-cause data",
        "summary_line_risk": "{count} parts are overdue or predicted to be due within 30 days and should be prioritized.",
        "summary_line_hotspot": "The most frequently replaced machine/part is “{part}”, with {count} historical records.",
        "summary_line_reason": "The most common failure cause is “{reason}”, appearing in {count} records.",
        "summary_line_backlog": "There are {count} open work orders, representing {rate:.1f}% of all records.",
        "summary_line_pm": "Recommended PM allocation: weekly {weekly}, monthly {monthly}, quarterly {quarterly}, and semi-annually {semi} items.",
        "summary_line_self": "There are {total} self-repair records: {completed} completed and {pending} pending/under monitoring.",
        "summary_col_status": "Risk Status",
        "summary_col_part": "Machine / Part",
        "summary_col_count": "Historical Count",
        "summary_col_mtbf": "Average Cycle (Days)",
        "summary_col_days": "Days to Predicted Change",
        "summary_overdue": "🔴 Overdue",
        "summary_due_soon": "🟠 Due Within 30 Days",
        "glance_title": "👀 At-a-Glance Summary",
        "glance_caption": "Red means act now, orange means schedule, and green means normal.",
        "overall_status": "Overall Status",
        "status_critical": "🔴 Act Now",
        "status_warning": "🟠 Attention Needed",
        "status_normal": "🟢 Normal",
        "main_action": "Top Priority",
        "focus_header": "The four items management should check first",
        "focus_urgent": "First Priority",
        "focus_hotspot": "Frequent-Failure Part",
        "focus_issue": "Most Common Failure",
        "focus_backlog": "Open Work Orders",
        "no_urgent_action": "No parts are overdue or due within 30 days.",
        "urgent_action_template": "Handle “{part}” first; {days} days remain before the predicted change date.",
        "overdue_action_template": "Handle “{part}” immediately; it is {days} days overdue.",
        "hotspot_template": "{count} historical replacements",
        "issue_template": "Appeared in {count} records",
        "backlog_template": "{rate:.1f}% of all records",
        "pm_quick": "📅 PM focus: weekly {weekly} | monthly {monthly} | quarterly {quarterly} | semi-annually {semi}",
        "self_repair_quick": "🧾 Self-repair: {completed} completed | {pending} pending",
        "latest_pending": "Latest pending: {machine} | {problem}",
        "no_pending_repairs": "No self-repair records are currently pending.",
        "details_expander": "🔍 View Full Analysis and Priority Details",
        "priority_action": "Recommended Action",
        "action_replace_now": "Verify and replace immediately",
        "action_schedule_7d": "Inspect and prepare parts within 7 days",
        "action_schedule_30d": "Schedule inspection this month",
    },
    "ภาษาไทย": {
        "title": "🛠️ แดชบอร์ดซ่อมบำรุงเชิงป้องกันและคาดการณ์อะไหล่ F-mask",
        "tab_dashboard": "📊 แดชบอร์ดติดตามรายเดือน",
        "tab_prediction": "🔮 กลไกการคาดการณ์อายุอะไหล่",
        "tab_pm_schedule": "📅 แผนตาราง PM มาตรฐาน",
        "tab_summary": "🔧 จุดซ่อมและปัญหา",
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
        "repair_manage_title": "🗑️ เลือกและลบบันทึกการซ่อม",
        "repair_manage_help": "ทำเครื่องหมายรายการทางซ้าย สามารถลบหลายรายการพร้อมกันได้",
        "repair_select_col": "เลือกเพื่อลบ",
        "repair_delete_btn": "🗑️ ลบรายการที่เลือก",
        "repair_delete_none": "กรุณาเลือกบันทึกการซ่อมอย่างน้อยหนึ่งรายการ",
        "repair_delete_success": "ลบบันทึกการซ่อมแล้ว {count} รายการ",
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
        "summary_title": "📝 สรุปประเด็นสำคัญสำหรับผู้บริหาร",
        "summary_desc": "ระบบสรุปอะไหล่ความเสี่ยงสูง จุดเสียบ่อย งานที่ยังไม่ปิด และลำดับความสำคัญของ PM โดยอัตโนมัติ",
        "summary_total_records": "ประวัติการซ่อม",
        "summary_risk_parts": "ต้องจัดการภายใน 30 วัน",
        "summary_top_issue": "สาเหตุเสียที่พบบ่อยที่สุด",
        "summary_backlog_rate": "อัตรางานค้าง",
        "summary_conclusion": "📌 ข้อสรุปสำคัญ",
        "summary_priority_title": "🚨 รายการที่ต้องดำเนินการก่อน",
        "summary_no_risk": "ขณะนี้ไม่มีอะไหล่ที่เกินกำหนดหรือคาดว่าต้องเปลี่ยนภายใน 30 วัน",
        "summary_pm_focus": "📅 จุดเน้นในการทำ PM",
        "summary_self_repair": "🧾 สถานะบันทึกการซ่อมด้วยตนเอง",
        "summary_no_issue": "ไม่มีข้อมูลสาเหตุการเสีย",
        "summary_line_risk": "มีอะไหล่ {count} รายการที่เกินกำหนดหรือคาดว่าจะถึงกำหนดภายใน 30 วัน ควรดำเนินการก่อน",
        "summary_line_hotspot": "เครื่องจักร/อะไหล่ที่เปลี่ยนบ่อยที่สุดคือ “{part}” รวม {count} ครั้ง",
        "summary_line_reason": "สาเหตุการเสียที่พบบ่อยที่สุดคือ “{reason}” จำนวน {count} รายการ",
        "summary_line_backlog": "มีใบงานที่ยังไม่ปิด {count} รายการ คิดเป็น {rate:.1f}% ของทั้งหมด",
        "summary_line_pm": "ข้อเสนอ PM: รายสัปดาห์ {weekly} รายการ รายเดือน {monthly} รายการ รายไตรมาส {quarterly} รายการ และทุกครึ่งปี {semi} รายการ",
        "summary_line_self": "บันทึกการซ่อมด้วยตนเองทั้งหมด {total} รายการ เสร็จแล้ว {completed} รายการ และรอติดตาม {pending} รายการ",
        "summary_col_status": "สถานะความเสี่ยง",
        "summary_col_part": "เครื่องจักร / อะไหล่",
        "summary_col_count": "จำนวนครั้งในอดีต",
        "summary_col_mtbf": "รอบเฉลี่ย (วัน)",
        "summary_col_days": "วันถึงกำหนดเปลี่ยน",
        "summary_overdue": "🔴 เกินกำหนด",
        "summary_due_soon": "🟠 ถึงกำหนดภายใน 30 วัน",
        "glance_title": "👀 สรุปแบบมองครั้งเดียว",
        "glance_caption": "สีแดงให้ทำทันที สีส้มให้วางแผน และสีเขียวคือปกติ",
        "overall_status": "สถานะโดยรวม",
        "status_critical": "🔴 ดำเนินการทันที",
        "status_warning": "🟠 ต้องติดตาม",
        "status_normal": "🟢 ปกติ",
        "main_action": "งานสำคัญที่สุด",
        "focus_header": "4 เรื่องที่ผู้บริหารควรดูก่อน",
        "focus_urgent": "ลำดับแรก",
        "focus_hotspot": "อะไหล่เสียบ่อย",
        "focus_issue": "ปัญหาที่พบบ่อย",
        "focus_backlog": "ใบงานที่ยังไม่ปิด",
        "no_urgent_action": "ไม่มีอะไหล่เกินกำหนดหรือถึงกำหนดภายใน 30 วัน",
        "urgent_action_template": "จัดการ “{part}” ก่อน เหลือ {days} วันถึงกำหนดเปลี่ยน",
        "overdue_action_template": "จัดการ “{part}” ทันที เกินกำหนดแล้ว {days} วัน",
        "hotspot_template": "เปลี่ยนมาแล้ว {count} ครั้ง",
        "issue_template": "พบทั้งหมด {count} รายการ",
        "backlog_template": "คิดเป็น {rate:.1f}% ของทั้งหมด",
        "pm_quick": "📅 จุดเน้น PM: รายสัปดาห์ {weekly} | รายเดือน {monthly} | รายไตรมาส {quarterly} | ครึ่งปี {semi}",
        "self_repair_quick": "🧾 ซ่อมด้วยตนเอง: เสร็จแล้ว {completed} | รอติดตาม {pending}",
        "latest_pending": "งานติดตามล่าสุด: {machine} | {problem}",
        "no_pending_repairs": "ไม่มีบันทึกซ่อมด้วยตนเองที่ต้องติดตาม",
        "details_expander": "🔍 ดูการวิเคราะห์และรายละเอียดลำดับความสำคัญ",
        "priority_action": "แนวทางดำเนินการ",
        "action_replace_now": "ตรวจสอบและเปลี่ยนทันที",
        "action_schedule_7d": "ตรวจและเตรียมอะไหล่ภายใน 7 วัน",
        "action_schedule_30d": "จัดตารางตรวจภายในเดือนนี้",
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


def get_repair_log_dataframe(include_id=False):
    """將 Session State 內的維修紀錄轉成顯示用 DataFrame。"""
    if not st.session_state.repair_logs:
        return pd.DataFrame()

    repair_df = pd.DataFrame(st.session_state.repair_logs)
    display_columns = ["time", "machine", "problem", "action", "status", "note"]
    if include_id:
        display_columns = ["id"] + display_columns
    repair_df = repair_df.reindex(columns=display_columns)

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
    summary_risk_rows = []

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
                summary_risk_rows.append(
                    {
                        "name": name,
                        "count": count,
                        "mtbf": round(mtbf, 1),
                        "days_left": days_left,
                    }
                )

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
    # 6. 四大分頁架構
    # ==========================================
    tab1, tab2, tab3, tab4 = st.tabs(
        [
            L["tab_dashboard"],
            L["tab_prediction"],
            L["tab_pm_schedule"],
            L["tab_summary"],
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
                        "id": uuid4().hex,
                        "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "machine": repair_machine.strip(),
                        "problem": repair_problem.strip(),
                        "action": repair_action.strip(),
                        "status": repair_status,
                        "note": repair_note.strip(),
                    },
                )
                save_repair_logs()
                st.success(L["repair_success"])
                st.rerun()
            else:
                st.warning(L["repair_required"])

        if st.session_state.repair_logs:
            # ==========================================
            # 維修紀錄管理：勾選後可一次刪除多筆
            # ==========================================
            st.markdown(f"#### {L['repair_manage_title']}")
            st.caption(L["repair_manage_help"])

            delete_table = get_repair_log_dataframe(include_id=True)
            select_column = L["repair_select_col"]
            delete_table.insert(0, select_column, False)

            if "repair_delete_editor_version" not in st.session_state:
                st.session_state.repair_delete_editor_version = 0
            if st.session_state.get("repair_delete_flash"):
                st.success(st.session_state.pop("repair_delete_flash"))

            delete_editor_key = (
                f"repair_delete_editor_{st.session_state.repair_delete_editor_version}"
            )
            edited_delete_table = st.data_editor(
                delete_table,
                use_container_width=True,
                hide_index=True,
                disabled=[
                    "id",
                    L["table_time"],
                    L["table_machine"],
                    L["table_problem"],
                    L["table_action"],
                    L["table_status"],
                    L["table_note"],
                ],
                column_config={
                    "id": None,
                    select_column: st.column_config.CheckboxColumn(
                        select_column,
                        help=L["repair_manage_help"],
                        default=False,
                    ),
                },
                key=delete_editor_key,
            )

            selected_ids = edited_delete_table.loc[
                edited_delete_table[select_column] == True, "id"  # noqa: E712
            ].astype(str).tolist()

            if st.button(
                L["repair_delete_btn"],
                type="primary",
                disabled=not selected_ids,
                key="repair_delete_button",
            ):
                selected_id_set = set(selected_ids)
                before_count = len(st.session_state.repair_logs)
                st.session_state.repair_logs = [
                    item
                    for item in st.session_state.repair_logs
                    if str(item.get("id", "")) not in selected_id_set
                ]
                deleted_count = before_count - len(st.session_state.repair_logs)
                save_repair_logs()
                st.session_state.repair_delete_editor_version += 1
                st.session_state.repair_delete_flash = L[
                    "repair_delete_success"
                ].format(count=deleted_count)
                st.rerun()

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

    # --- TAB 4: 維修重點與問題點（主管一眼版） ---
    with tab4:
        total_records = len(df)
        backlog_rate = (
            uncompleted_count / total_records * 100
            if total_records
            else 0.0
        )

        # 故障問題統計
        if "อาการเสีย / ปัญหา" in df.columns:
            issue_series = (
                df["อาการเสีย / ปัญหา"]
                .dropna()
                .astype(str)
                .str.strip()
            )
            issue_series = issue_series[issue_series != ""]
            issue_counts_all = issue_series.value_counts()
        else:
            issue_counts_all = pd.Series(dtype="int64")

        if not issue_counts_all.empty:
            top_issue = str(issue_counts_all.index[0])
            top_issue_count = int(issue_counts_all.iloc[0])
        else:
            top_issue = L["summary_no_issue"]
            top_issue_count = 0

        # 自行維修狀態
        total_repairs = len(st.session_state.repair_logs)
        completed_repairs = sum(
            1
            for item in st.session_state.repair_logs
            if str(item.get("status", "")).startswith("✅")
        )
        pending_repairs = total_repairs - completed_repairs

        # PM 分類數量
        cycle_counts = (
            pm_df["📅 建議點檢週期"].value_counts()
            if not pm_df.empty
            else pd.Series(dtype="int64")
        )
        weekly_count = int(cycle_counts.get("每週 (Weekly)", 0))
        monthly_count = int(cycle_counts.get("每月 (Monthly)", 0))
        quarterly_count = int(cycle_counts.get("每季 (Quarterly)", 0))
        semi_count = int(cycle_counts.get("每半年 (Semi-Annually)", 0))

        risk_df_base = (
            pd.DataFrame(summary_risk_rows).sort_values("days_left", ascending=True)
            if summary_risk_rows
            else pd.DataFrame()
        )

        def get_quick_sop(part_name):
            # 依設備名稱帶出最直接的維修方向
            part_lower = str(part_name).lower()
            if "กระบอก" in part_lower or "cylinder" in part_lower:
                return L["sop_c1"]
            if "ปั๊ม" in part_lower or "pump" in part_lower:
                return L["sop_c2"]
            if (
                "สาย" in part_lower
                or "cable" in part_lower
                or "chain" in part_lower
                or "sensor" in part_lower
            ):
                return L["sop_c3"]
            return L["sop_c4"]

        # 最優先維修事項
        if not risk_df_base.empty:
            first_risk = risk_df_base.iloc[0]
            first_part = str(first_risk["name"])
            first_days = int(first_risk["days_left"])
            if first_days < 0:
                priority_text = f"🔴 先修『{first_part}』：已超過預估更換日 {abs(first_days)} 天。"
                priority_action = "立即停機確認、備料並安排更換。"
            elif first_days <= 7:
                priority_text = f"🟠 先檢查『{first_part}』：預估 {first_days} 天內需更換。"
                priority_action = "7 天內完成點檢、備料與更換排程。"
            else:
                priority_text = f"🟡 本月處理『{first_part}』：距預估更換日剩 {first_days} 天。"
                priority_action = "本月完成點檢並確認備品庫存。"
        elif uncompleted_count > 0:
            first_part = str(top_part)
            priority_text = f"🟠 先追蹤未結案工單：目前共有 {uncompleted_count} 件。"
            priority_action = "確認負責人、預計完成日與卡關原因。"
        else:
            first_part = str(top_part)
            priority_text = "🟢 目前沒有 30 天內到期或逾期零件。"
            priority_action = "依 PM 週期持續點檢，並追蹤高頻故障設備。"

        hotspot_sop = get_quick_sop(top_part)

        pending_log = next(
            (
                item
                for item in st.session_state.repair_logs
                if not str(item.get("status", "")).startswith("✅")
            ),
            None,
        )
        if pending_log:
            pending_log_text = (
                f"{pending_log.get('machine', '—')}｜"
                f"{pending_log.get('problem', '—')}"
            )
        else:
            pending_log_text = "目前沒有待追蹤的自行維修紀錄"

        st.markdown("### 🔧 維修重點與問題點")
        st.caption("左邊看發生什麼問題，右邊直接看要怎麼修、先修哪一個。")

        st.markdown(
            f'''<div class="priority-line">
                <strong>{html.escape(priority_text)}</strong><br>
                維修動作：{html.escape(priority_action)}
            </div>''',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'''<div class="issue-repair-grid">
                <div class="summary-panel problem-panel">
                    <div class="panel-title">⚠️ 問題點</div>
                    <div class="point-row point-red">
                        <strong>30 天內需處理：{overdue_count} 項</strong><br>
                        已逾期或接近預估更換日，需優先排程。
                    </div>
                    <div class="point-row point-orange">
                        <strong>最常出問題的設備：{html.escape(str(top_part))}</strong><br>
                        歷史共發生／更換 {int(top_count)} 次。
                    </div>
                    <div class="point-row point-orange">
                        <strong>最常見故障：{html.escape(str(top_issue))}</strong><br>
                        共出現 {top_issue_count} 筆。
                    </div>
                    <div class="point-row point-blue">
                        <strong>未結案工單：{uncompleted_count} 件</strong><br>
                        占全部紀錄 {backlog_rate:.1f}%。
                    </div>
                </div>
                <div class="summary-panel repair-panel">
                    <div class="panel-title">🛠️ 維修重點</div>
                    <div class="point-row point-red">
                        <strong>第一優先：{html.escape(str(first_part))}</strong><br>
                        {html.escape(priority_action)}
                    </div>
                    <div class="point-row point-green">
                        <strong>高頻設備維修方向</strong><br>
                        {html.escape(str(hotspot_sop))}
                    </div>
                    <div class="point-row point-blue">
                        <strong>工單／自行維修追蹤</strong><br>
                        未結案 {uncompleted_count} 件；自行維修待追蹤 {pending_repairs} 筆。<br>
                        最新待追蹤：{html.escape(pending_log_text)}
                    </div>
                    <div class="point-row point-green">
                        <strong>PM 安排</strong><br>
                        每週 {weekly_count} 項｜每月 {monthly_count} 項｜每季 {quarterly_count} 項｜每半年 {semi_count} 項
                    </div>
                </div>
            </div>''',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="one-look-title">📌 問題 → 維修動作對照</div>',
            unsafe_allow_html=True,
        )
        quick_rows = []

        if not risk_df_base.empty:
            for _, row in risk_df_base.head(3).iterrows():
                days = int(row["days_left"])
                part_name = str(row["name"])
                if days < 0:
                    problem_text = f"預估更換已逾期 {abs(days)} 天"
                    repair_text = "立即確認狀態、備料並安排更換"
                    level = "🔴 立即"
                elif days <= 7:
                    problem_text = f"預估 {days} 天內需更換"
                    repair_text = "7 天內完成點檢與備料"
                    level = "🟠 優先"
                else:
                    problem_text = f"預估 {days} 天內需更換"
                    repair_text = "本月安排點檢與更換排程"
                    level = "🟡 排程"
                quick_rows.append(
                    {
                        "優先級": level,
                        "設備／零件": part_name,
                        "問題點": problem_text,
                        "維修動作": repair_text,
                    }
                )

        quick_rows.append(
            {
                "優先級": "🟠 高頻",
                "設備／零件": str(top_part),
                "問題點": f"歷史發生／更換 {int(top_count)} 次",
                "維修動作": hotspot_sop,
            }
        )
        quick_rows.append(
            {
                "優先級": "🔵 追蹤",
                "設備／零件": "未結案工單",
                "問題點": f"共 {uncompleted_count} 件，未結案率 {backlog_rate:.1f}%",
                "維修動作": "確認負責人、原因與預計完成日",
            }
        )

        st.dataframe(
            pd.DataFrame(quick_rows).head(5),
            use_container_width=True,
            hide_index=True,
        )

        with st.expander("🔍 查看完整高風險零件與分析明細"):
            if not risk_df_base.empty:
                detail_df = risk_df_base.copy()
                detail_df["風險狀態"] = detail_df["days_left"].apply(
                    lambda value: "🔴 已逾期" if value < 0 else "🟠 30 天內到期"
                )
                detail_df["建議維修動作"] = detail_df.apply(
                    lambda row: get_quick_sop(row["name"]),
                    axis=1,
                )
                detail_df = detail_df.rename(
                    columns={
                        "name": "設備／零件",
                        "count": "歷史次數",
                        "mtbf": "平均週期（天）",
                        "days_left": "距預估更換（天）",
                    }
                )
                st.dataframe(
                    detail_df[
                        [
                            "風險狀態",
                            "設備／零件",
                            "距預估更換（天）",
                            "歷史次數",
                            "平均週期（天）",
                            "建議維修動作",
                        ]
                    ],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.success("目前沒有 30 天內到期或逾期的零件。")

else:
    st.info(L["upload_hint"])
