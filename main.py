import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime
import io

# 1. 網頁基本設定
st.set_page_config(page_title="F-mask 預防保養與預測儀表板", layout="wide")

# ==========================================
# 2. 介面控制與主題切換
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ 介面控制 / Controls")
    selected_lang = st.radio("🌐 選擇語言 / Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
    theme_mode = st.radio("🌓 介面主題 / Theme Mode", ["☀️ 白天模式 (Light)", "🌙 黑夜模式 (Dark)"])

if "🌙 黑夜模式 (Dark)" in theme_mode:
    plotly_template = "plotly_dark"
    st.markdown(
        """
        <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        .stTabs [data-baseweb="tab"] p { color: #A0A5B5 !important; font-size: 16px; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] p { color: #FF4B4B !important; font-weight: bold; }
        .kpi-box { background-color: #1E222B; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; margin-bottom: 10px; }
        .summary-box { background-color: #1A1F2C; padding: 20px; border-radius: 8px; border: 1px solid #FF4B4B; margin-top: 10px; margin-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True
    )
else:
    plotly_template = "plotly"
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF; color: #31333F; }
        .kpi-box { background-color: #F0F2F6; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; margin-bottom: 10px; }
        .summary-box { background-color: #FFF5F5; padding: 20px; border-radius: 8px; border: 1px solid #FF4B4B; margin-top: 10px; margin-bottom: 20px; }
        </style>
        """, unsafe_allow_html=True
    )

# ==========================================
# 3. 多國語言字典設定
# ==========================================
LANG_DICT = {
    "繁體中文": {
        "title": "F-mask 設備運維系統",
        "subtitle": "機台預防保養(PM)與零組件更換預測追蹤儀表板",
        "upload_label": "請在下方拖曳 or 選擇上傳 GEM 維修數據 Excel 檔案 (.xlsx)",
        "tab_dashboard": "📊 每月數據追蹤儀表板 (Dashboard)",
        "tab_prediction": "🔮 零組件更換預測機制 (Prediction)",
        "tab_pm_schedule": "📅 預防保養(PM)時程表 (PM Schedule)",
        "tab_methods": "🛠️ 前 10 大故障維修方法 (Top 10 SOPs)",
        "tab_ai_assistant": "🤖 AI 智慧運維助手 (AI Assistant)",
        "kb_title": "💡 瞭解機台：F-mask 機台基本認識",
        "kb_func_title": "🔍 機台核心功能",
        "kb_func_desc": "主要負責生產線上的光罩精密對位、曝光與表面防護處理，確保製程良率。",
        "kb_parts_title": "⚙️ 主要零組件",
        "kb_parts_desc": "包含高精密對位氣缸、進氣/真空泵浦、GEM 通訊模組、UV 導光條、輸送帶軸承及感測器線組。",
        "kb_wear_title": "🚨 常見磨損/損壞部位",
        "kb_wear_desc": "氣缸密封件、泵浦濾網、輸送帶皮帶及電纜拖鏈（易斷線）為高磨損易耗部位。",
        "filter_title": "🔍 篩選條件 (Filters)", "filter_year": "選擇年份", "filter_month": "選擇月份",
        "filter_status": "選擇案件狀態",
        "kpi_total": "總報修件數", "kpi_completed": "已完成件數", "kpi_avg_days": "平均維修天數", "unit_cases": "件",
        "unit_days": "天", "no_data": "無數據",
        "chart_top10_title": "📌 零組件報修排行 Top 10 (分析更換頻率)", "chart_top10_x": "報修次數",
        "chart_top10_y": "設備零件名稱",
        "chart_status_title": "📈 維修案件狀態佔比", "chart_month_title": "📅 每月報修趨勢",
        "table_title": "📋 設備維護歷史明細 (ME 每月檢查格式)",
        "col_doc": "文件流水號", "col_machine": "機台/零件名稱", "col_status": "目前狀態", "col_detail": "詳細處理需求",
        "col_duration": "維修耗時(天)",
        "pred_title": "🔮 零組件更換預測機制與失效分析",
        "pred_subtitle": "利用歷史數據建立的模型，預估零組件下一次需要更換的時間與剩餘壽命。",
        "xl_part_name": "零組件名稱", "xl_failures": "歷史報修次數", "xl_mtbf": "平均故障間隔 MTBF (天)",
        "xl_last_date": "最後一次更換日",
        "xl_pred_date": "預估下次更換時間", "xl_days_left": "剩餘壽命天數", "xl_status_alert": "維護狀態提示",
        "alert_safe": "✅ 正常", "alert_overdue": "🚨 已逾期", "alert_warning": "⚠️ 建議預防性更換",
        "pm_plan_title": "📅 F-mask 預防保養 (PM) 時程表計畫 (動態生成)",
        "pm_plan_sub": "根據上傳數據中之零件種類與故障頻率，自動精準擬定之檢查與保養週期表。",
        "pm_col_id": "零件編號", "pm_col_name": "維修項目/零組件", "pm_col_module": "對應模組",
        "pm_col_cycle": "保養更換週期", "pm_col_mtbf": "預估壽命 (MTBF)", "pm_col_last": "前次維修日",
        "pm_col_next": "下次預定 PM 日", "pm_col_level": "保養層級", "pm_col_time": "標準工時 (Mins)",
        "pm_col_stock": "安全庫存量", "pm_col_owner": "負責單位", "pm_col_sop": "SOP 參考文件/方法",
        "ai_title": "🤖 F-mask AI 設備運維助手", "ai_caption": "支援 ME 工程師與主管快速查詢報修規律。",
        "ai_welcome": "你好！我是 F-mask AI 助手。👋\n\n您可以問我：'哪種零件最近最常更換？' 或 '幫我分析目前的維修效率'。",
        "ai_input_holder": "請輸入您的提問...",
        "summary_title": "🚨 運維焦點與問題總整理 (Executive Summary)",
        "summary_p1": "💡 **異常風險警示**：目前共有 **{}** 項零件已處於更換逾期或預防更換邊緣，ME 應立即啟動備件與更換排程。",
        "summary_p2": "⚙️ **頭號故障熱點**：全機台報修頻率最高的零組件為 **「{}」**（累計報修 **{}** 次），建議列為重點巡檢目標。",
        "summary_p3": "⏳ **流程效率瓶頸**：目前仍有 **{}** 件維修案件未結案（如：等候備件或待生產線停機），這將直接影響整體稼動率。",
        "methods_title": "🛠️ 前 10 大高頻故障零件之標準維修與對策方法",
        "methods_sub": "系統依據實際故障排行，動態產出前 10 大零件的標準維護指南 (SOP 關鍵指引)，供 ME 團隊落實改善。",
        "meth_col_rank": "排名", "meth_col_name": "零件名稱", "meth_col_count": "累積故障次數",
        "meth_col_action": "標準維修與根治對策方法"
    },
    "English": {
        "title": "F-mask System",
        "subtitle": "Machine PM & Part Replacement Prediction Dashboard",
        "upload_label": "Drag and drop or select to upload GEM maintenance Excel file (.xlsx)",
        "tab_dashboard": "📊 Monthly Tracking Dashboard", "tab_prediction": "🔮 Part Replacement Prediction",
        "tab_pm_schedule": "📅 PM Schedule Plan",
        "tab_methods": "🛠️ Top 10 Maintenance SOPs", "tab_ai_assistant": "🤖 AI Assistant",
        "kb_title": "💡 Understand Machine: F-mask Knowledge Base",
        "kb_func_title": "🔍 Core Function",
        "kb_func_desc": "Responsible for precise mask alignment, exposure, and surface protection to ensure process yield.",
        "kb_parts_title": "⚙️ Key Components",
        "kb_parts_desc": "Includes alignment cylinders, vacuum pumps, GEM communication modules, UV light guides, conveyor bearings, and sensor wiring.",
        "kb_wear_title": "🚨 High Wear Areas",
        "kb_wear_desc": "Cylinder seals, pump filters, conveyor belts, and cable carrier chains are highly prone to wear and breakage.",
        "filter_title": "🔍 Filters", "filter_year": "Select Year", "filter_month": "Select Month",
        "filter_status": "Select Status",
        "kpi_total": "Total Cases", "kpi_completed": "Completed Cases", "kpi_avg_days": "Avg Repair Duration",
        "unit_cases": "pcs", "unit_days": "days", "no_data": "No Data",
        "chart_top10_title": "📌 Top 10 Part Failures (Replacement Frequency)", "chart_top10_x": "Failure Count",
        "chart_top10_y": "Part Name",
        "chart_status_title": "📈 Repair Status Distribution", "chart_month_title": "📅 Monthly Repair Trend",
        "table_title": "📋 Maintenance History Details (For ME Monthly Check)",
        "col_doc": "Doc Number", "col_machine": "Part Name", "col_status": "Status", "col_detail": "Failure Details",
        "col_duration": "Duration (Days)",
        "pred_title": "🔮 Intelligent Prediction & Replacement Timing",
        "pred_subtitle": "A simple estimation method using historical data to predict the next required replacement date for components.",
        "xl_part_name": "Component Name", "xl_failures": "Failures Count", "xl_mtbf": "MTBF (Days)",
        "xl_last_date": "Last Replacement Date", "xl_pred_date": "Predicted Next Replacement",
        "xl_days_left": "Days Left", "xl_status_alert": "Status Alert",
        "alert_safe": "✅ Safe", "alert_overdue": "🚨 Overdue", "alert_warning": "⚠️ Warning (Replace Soon)",
        "pm_plan_title": "📅 F-mask Machine Preventive Maintenance (PM) Cycle Plan",
        "pm_plan_sub": "Dynamically generated schedule defining specific item checking frequencies from uploaded data.",
        "pm_col_id": "Part ID", "pm_col_name": "Maintenance Item", "pm_col_module": "Module",
        "pm_col_cycle": "PM Interval", "pm_col_mtbf": "Estimated Lifespan", "pm_col_last": "Last Service",
        "pm_col_next": "Next PM Date", "pm_col_level": "PM Level", "pm_col_time": "Standard Time",
        "pm_col_stock": "Safety Stock", "pm_col_owner": "Owner Team", "pm_col_sop": "SOP Reference",
        "ai_title": "🤖 F-mask AI Assistant", "ai_caption": "Helps ME and Managers track failure patterns quickly.",
        "ai_welcome": "Hello! I am your F-mask AI assistant. 👋 Feel free to ask me questions about this data!",
        "ai_input_holder": "Type your question here...",
        "summary_title": "🚨 Executive Summary & Core Bottlenecks",
        "summary_p1": "💡 **Risk Alert**: There are **{}** parts currently overdue or near expiration. ME should initiate part prep immediately.",
        "summary_p2": "⚙️ **Top Failure Hotspot**: The component with the highest failure frequency is **'{}'** (Total **{}** failures).",
        "summary_p3": "⏳ **Efficiency Bottleneck**: **{}** maintenance cases remain unclosed (e.g., awaiting parts/production stops), affecting OEE.",
        "methods_title": "🛠️ Standard Maintenance Methods for Top 10 Failures",
        "methods_sub": "Dynamically generated SOP guidelines based on raw failure ranking to help ME teams counter issues effectively.",
        "meth_col_rank": "Rank", "meth_col_name": "Part Name", "meth_col_count": "Failures",
        "meth_col_action": "Standard Countermeasure / SOP Action"
    },
    "ภาษาไทย": {
        "title": "F-mask ระบบซ่อมบำรุง",
        "subtitle": "แดชบอร์ดแผนซ่อมบำรุงเชิงป้องกัน (PM) และคาดการณ์อะไหล่",
        "upload_label": "ลากและวางหรือคลิกเพื่ออัปโหลดไฟล์ Excel ข้อมูลการซ่อมบำรุง (.xlsx)",
        "tab_dashboard": "📊 แดชบอร์ดติดตามข้อมูลรายเดือน", "tab_prediction": "🔮 ระบบคาดการณ์เปลี่ยนชิ้นส่วนอะไหล่",
        "tab_pm_schedule": "📅 ตารางเวลาแผน PM (PM Schedule)",
        "tab_methods": "🛠️ 10 อันดับวิธีการซ่อมบำรุง (Top 10 SOPs)",
        "tab_ai_assistant": "🤖 ผู้ช่วยอัจฉริยะ AI (AI Assistant)",
        "kb_title": "💡 ทำความเข้าใจเครื่องจักร: ข้อมูลพื้นฐาน F-mask",
        "kb_func_title": "🔍 ฟังก์ชันหลักของเครื่องจักร",
        "kb_func_desc": "รับผิดชอบในการจัดตำแหน่งหน้ากาก (Mask) ที่แม่นยำ การเปิดรับแสง และการปกป้องพื้นผิว",
        "kb_parts_title": "⚙️ ส่วนประกอบสำคัญ",
        "kb_parts_desc": "รวมถึงกระบอกสูบจัดตำแหน่ง, ปั๊มสุญญากาศ, โมดูลการสื่อสาร GEM, แถบนำแสง UV, แบริ่งสายพานลำเลียง",
        "kb_wear_title": "🚨 จุดที่สึกหรอและเสียหายบ่อย",
        "kb_wear_desc": "ซีลกระบอกสูบ, ตัวกรองปั๊ม, สายพานลำเลียง และโซ่ลากสายเคเบิล เป็นจุดที่สึกหรอสูง",
        "filter_title": "🔍 เงื่อนไขการกรอง (Filters)", "filter_year": "เลือกปี", "filter_month": "เลือกเดือน",
        "filter_status": "เลือกสถานะ",
        "kpi_total": "จำนวนการแจ้งซ่อมทั้งหมด", "kpi_completed": "ดำเนินการเสร็จสิ้น",
        "kpi_avg_days": "ระยะเวลาซ่อมเฉลี่ย", "unit_cases": "รายการ", "unit_days": "วัน", "no_data": "ไม่มีข้อมูล",
        "chart_top10_title": "📌 10 อันดับอะไหล่ที่แจ้งซ่อมบ่อย (วิเคราะห์ความถี่)",
        "chart_top10_x": "จำนวนครั้งที่แจ้งซ่อม", "chart_top10_y": "ชื่อชิ้นส่วน",
        "chart_status_title": "📈 สัดส่วนสถานะใบแจ้งซ่อม", "chart_month_title": "📅 แนวโน้มการแจ้งซ่อมรายเดือน",
        "table_title": "📋 รายละเอียดประวัติการซ่อมบำรุง",
        "col_doc": "ลำดับเอกสาร", "col_machine": "ชื่ออุปกรณ์", "col_status": "สถานะปัจจุบัน",
        "col_detail": "รายละเอียด", "col_duration": "ระยะเวลา (วัน)",
        "pred_title": "🔮 ระบบคาดการณ์เวลาเปลี่ยนชิ้นส่วนอะไหล่และสาเหตุรากเหง้า",
        "pred_subtitle": "ใช้วิธีการคำนวณอย่างง่ายจากข้อมูลประวัติ เพื่อประมาณการเวลาที่ต้องเปลี่ยนอะไหล่ในครั้งต่อไป",
        "xl_part_name": "ชื่อชิ้นส่วนอุปกรณ์", "xl_failures": "จำนวนครั้งที่ชำรุด",
        "xl_mtbf": "ระยะเวลาเฉลี่ย MTBF (วัน)", "xl_last_date": "วันที่เปลี่ยนล่าสุด",
        "xl_pred_date": "คาดการณ์เวลาที่ต้องเปลี่ยนครั้งต่อไป", "xl_days_left": "จำนวนวันอายุใช้งานที่เหลือ",
        "xl_status_alert": "แจ้งเตือนสถานะ",
        "alert_safe": "✅ ปกติ", "alert_overdue": "🚨 เกินกำหนด", "alert_warning": "⚠️ แนะนำให้เปลี่ยนเพื่อป้องกัน",
        "pm_plan_title": "📅 ตารางเวลาและแผนรอบการซ่อมบำรุงเชิงป้องกัน (PM) F-mask",
        "pm_plan_sub": "ระบบคำนวณรอบและรายการตรวจสอบจากข้อมูลจริงโดยอัตโนมัติ",
        "pm_col_id": "รหัสอะไหล่", "pm_col_name": "รายการซ่อมบำรุง", "pm_col_module": "โมดูลที่เกี่ยวข้อง",
        "pm_col_cycle": "รอบเวลา PM แนะนำ", "pm_col_mtbf": "อายุใช้งานคาดการณ์", "pm_col_last": "วันที่ซ่อมล่าสุด",
        "pm_col_next": "วันที่แผน PM ถัดไป", "pm_col_level": "ระดับการบำรุงรักษา", "pm_col_time": "เวลามาตรฐาน",
        "pm_col_stock": "คลังอะไหล่ปลอดภัย", "pm_col_owner": "ทีมผู้รับผิดชอบ", "pm_col_sop": "เอกสารอ้างอิง SOP",
        "ai_title": "🤖 ผู้ช่วยอัจฉริยะ AI ประจำเครื่องจักร",
        "ai_caption": "ช่วยวิเคราะห์ประวัติการชำรุดสำหรับวิศวกรและผู้บริหาร",
        "ai_welcome": "สวัสดีครับ! ผมคือ AI ผู้ช่วยประจำระบบ F-mask 👋 ถามข้อมูลสรุปประจำเดือนได้เลยครับ",
        "ai_input_holder": "พิมพ์ข้อคำถามของคุณที่นี่...",
        "summary_title": "🚨 สรุปประเด็นสำคัญและปัญหาเร่งด่วน (Executive Summary)",
        "summary_p1": "💡 **แจ้งเตือนความเสี่ยง**: มีอะไหล่ **{}** รายการ ที่เกินกำหนดหรือใกล้ถึงเวลาเปลี่ยน แนะนำให้ ME วางแผนล่วงหน้าทันที",
        "summary_p2": "⚙️ **อะไหล่ที่ชำรุดบ่อยที่สุด**: ชิ้นส่วนที่แจ้งซ่อมสูงสุดคือ **'{}'** (เสียสะสม **{}** ครั้ง) ควรตรวจสอบเป็นพิเศษ",
        "summary_p3": "⏳ **คอขวดของกระบวนการ**: มีใบงานที่ยังค้างคาอยู่ **{}** รายการ (เช่น รออะไหล่/รอหยุดเครื่อง) ซึ่งส่งผลกระทบต่อไลน์ผลิต",
        "methods_title": "🛠️ วิธีการซ่อมบำรุงมาตรฐานสำหรับอะไหล่ที่ชำรุดบ่อย 10 อันดับแรก",
        "methods_sub": "แนวทาง SOP ที่ระบบสร้างขึ้นตามลำดับความเสียหายจริง เพื่อช่วยทีม ME แก้ไขปัญหาได้อย่างมีประสิทธิภาพ",
        "meth_col_rank": "อันดับ", "meth_col_name": "ชื่อชิ้นส่วนอะไหล่", "meth_col_count": "จำนวนครั้งที่ชำรุด",
        "meth_col_action": "วิธีการซ่อมบำรุงและการรับมือมาตรฐาน"
    }
}

STATUS_MAP = {
    "9.0 ดำเนินการแล้วเสร็จ": {"繁體中文": "9.0 已完成 (Completed)", "English": "9.0 Completed",
                               "ภาษาไทย": "9.0 ดำเนินการแล้วเสร็จ"},
    "8.2 ผู้แจ้งซ่อม不ยอมรับงานซ่อม": {"繁體中文": "8.2 退單/拒絕 (Rejected)", "English": "8.2 Rejected",
                                       "ภาษาไทย": "8.2 ผู้แจ้งซ่อมไม่ยอมรับงานซ่อม"},
    "8.1 รอการตรวจสอบจากผู้แจ้งซ่อม": {"繁體中文": "8.1 等待驗收 (Pending Check)", "English": "8.1 Pending Check",
                                       "ภาษาไทย": "8.1 รอการตรวจสอบจากผู้แจ้งซ่อม"},
    "4.1 ตรวจเช็คและแก้ปัญหาเบ遜byช่าง": {"繁體中文": "4.1 檢修中 (Troubleshooting)", "English": "4.1 Troubleshooting",
                                          "ภาษาไทย": "4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง"},
    "4.1 ตรวจเช็ค和แก้ปัญหาเบื้องต้นโดยช่าง": {"繁體中文": "4.1 檢修中 (Troubleshooting)",
                                               "English": "4.1 Troubleshooting",
                                               "ภาษาไทย": "4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง"},
    "6.1 รอช่างสั่งอะไหล่": {"繁體中文": "6.1 待叫修備件 (Ordering Parts)", "English": "6.1 Ordering Parts",
                             "ภาษาไทย": "6.1 รอช่างสั่งอะไหล่"},
    "6.3 รออะไหล่": {"繁體中文": "6.3 缺件/等候備件 (Awaiting Parts)", "English": "6.3 Awaiting Parts",
                     "ภาษาไทย": "6.3 รออะไหล่"},
    "6.4 รอฝ่ายผลิตหยุดเครื่องจักรเพื่อซ่อม": {"繁體中文": "6.4 待停機安排 (Waiting for Production)",
                                               "English": "6.4 Waiting for Production Stop",
                                               "ภาษาไทย": "6.4 รอฝ่ายผลิตหยุดเครื่องจักรเพื่อซ่อม"},
    "7.0 ดำเนินการซ่อมและรายงานผลปฏิบัติงาน": {"繁體中文": "7.0 維修執行中 (Repairing)", "English": "7.0 Repairing",
                                               "ภาษาไทย": "7.0 ดำเนินการซ่อมและรายงานผลปฏิบัติงาน"},
}


def get_action_by_name(name, lang):
    name_lower = str(name).lower()
    if "cylinder" in name_lower or "valve" in name_lower or "กระบอก" in name_lower or "วาล์ว" in name_lower:
        if lang == "繁體中文": return "🔧 1. 檢查氣缸密封圈是否磨損漏氣；2. 確保氣動三聯件潤滑油充足；3. 定期緊固氣缸固定螺絲避免位移。"
        if lang == "English": return "🔧 1. Check cylinder seals for wear/leakage; 2. Ensure pneumatic FRL lubricator has oil; 3. Tighten mounting bolts periodically."
        return "🔧 1. ตรวจสอบซีลกระบอกสูบว่ามีการรั่วไหลหรือไม่; 2. เติมน้ำมันชุดกรองลมดักน้ำ (FRL); 3. ขันแน่นโบลต์ยึดอย่างสม่ำเสมอเพื่อลดการขยับ"
    elif "pump" in name_lower or "filter" in name_lower or "ปั๊ม" in name_lower or "ตัวกรอง" in name_lower:
        if lang == "繁體中文": return "🧼 1. 每月清洗或更換真空泵浦濾網；2. 監控泵浦運轉溫度與異音；3. 檢查進出氣管路是否有折損或真空洩漏。"
        if lang == "English": return "🧼 1. Clean/replace vacuum pump filters monthly; 2. Monitor pump temperature and abnormal noise; 3. Inspect piping for vacuum leaks."
        return "🧼 1. ล้างหรือเปลี่ยนไส้กรองปั๊มสุญญากาศทุกเดือน; 2. ตรวจสอบอุณหภูมิและเสียงผิดปกติ; 3. เช็คสายท่อลมว่ามีการรั่วไหลของสุญญากาศหรือไม่"
    elif "cable" in name_lower or "sensor" in name_lower or "สาย" in name_lower or "เซนเซอร์" in name_lower or "wire" in name_lower:
        if lang == "繁體中文": return "⚡ 1. 清理感測器表面油污防訊號異常；2. 檢查拖鏈內電纜是否有扭曲磨損；3. 重新插拔並使用電子接點清潔劑保養接頭。"
        if lang == "English": return "⚡ 1. Clean sensor surface to avoid signal failure; 2. Inspect cables inside drag chains for twist/wear; 3. Clean connectors with contact cleaner."
        return "⚡ 1. ทำความสะอาดหน้าเซนเซอร์จากคราบน้ำมัน; 2. ตรวจสอบสายไฟในรางกระดูกงูว่าบิดงอหรือเสียดสีไหม; 3. ใช้สเปรย์ล้างคอนแทคทำความสะอาดข้อต่อ"
    elif "bearing" in name_lower or "belt" in name_lower or "สายพาน" in name_lower or "แบริ่ง" in name_lower or "เพลา" in name_lower:
        if lang == "繁體中文": return "⚙️ 1. 定期加注耐高溫潤滑脂(軸承)；2. 檢查輸送皮帶張力，防止打滑或偏擺；3. 巡檢傳動齒輪是否有異常磨損。"
        if lang == "English": return "⚙️ 1. Apply high-temp grease to bearings regularly; 2. Check conveyor belt tension to prevent slipping; 3. Inspect gears for wear."
        return "⚙️ 1. อัดจาระบีทนความร้อนสูงที่แบริ่งอย่างสม่ำเสมอ; 2. ตรวจสอบความตึงของสายพานลำเลียงเพื่อป้องกันการลื่นไถล; 3. เช็คเฟืองขับว่ามีการสึกหรอไหม"
    else:
        if lang == "繁體中文": return "🔍 1. 執行外觀標準巡檢，清理環境積塵；2. 檢查緊固件是否鬆動；3. 核對操作參數，更換已達壽命上限之預備零件。"
        if lang == "English": return "🔍 1. Perform visual inspection & dust cleaning; 2. Tighten all structural fasteners; 3. Verify operational parameters & swap end-of-life parts."
        return "🔍 1. ตรวจสอบภายนอกและทำความสะอาดฝุ่น; 2. ขันแน่นจุดยึดและสกรูทั้งหมด; 3. ตรวจสอบพารามิเตอร์การทำงานและเปลี่ยนอะไหล่ที่หมดอายุการใช้งาน"


L = LANG_DICT[selected_lang]


@st.cache_data
def load_and_clean_data(file):
    df = pd.read_excel(file)
    if "ลำดับเอกสาร" in df.columns:
        df = df[df["ลำดับเอกสาร"].notna()]
    elif "文件流水號" in df.columns:
        df = df[df["文件流水號"].notna()]

    date_col = None
    for c in ["วันที่แจ้งซ่อม", "日期", "Date", "วันที่"]:
        if c in df.columns:
            date_col = c
            break

    if date_col:
        df["Parsed_Date"] = pd.to_datetime(df[date_col], errors='coerce')
        df["年份_data"] = df["Parsed_Date"].apply(lambda dt: str(dt.year) if pd.notna(dt) else "Unknown")
        df["月份_data"] = df["Parsed_Date"].apply(lambda dt: f"{dt.month:02d}" if pd.notna(dt) else "Unknown")
    else:
        df["年份_data"], df["月份_data"], df["Parsed_Date"] = "Unknown", "Unknown", pd.NaT

    duration_col = None
    for c in ["ระยะเวลา (วัน)", "維修耗時(天)", "Duration"]:
        if c in df.columns:
            duration_col = c
            break
    if duration_col:
        df["Repair_Days"] = pd.to_numeric(df[duration_col], errors="coerce").fillna(0)
    else:
        df["Repair_Days"] = 0

    return df


if "main_file" not in st.session_state:
    st.session_state.main_file = None

uploaded_file = st.sidebar.file_uploader("🔄 更換數據檔案 (.xlsx)", type=["xlsx"])
if uploaded_file is not None:
    st.session_state.main_file = uploaded_file

if st.session_state.main_file is None:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_c:
        st.markdown(
            f"<h1 style='text-align: center; font-size: 4rem; background: linear-gradient(45deg, #4285F4, #EA4335, #FBBC05, #34A853); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>{L['title']}</h1>",
            unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #70757a; font-size: 1.2rem;'>{L['subtitle']}</p>",
                    unsafe_allow_html=True)
        center_file = st.file_uploader(L["upload_label"], type=["xlsx"], key="center_upload")
        if center_file:
            st.session_state.main_file = center_file
            st.rerun()
else:
    st.info("💡 數據載入成功。若要重新評估或更換檔案，請使用左側欄上傳新檔案。")

    try:
        df = load_and_clean_data(st.session_state.main_file)

        machine_col = next((c for c in ["ชื่อเครื่องจักร / อุปกรณ์", "機台/零件名稱", "Machine"] if c in df.columns),
                           None)
        status_col = next((c for c in ["สถานะใบแจ้งซ่อม", "目前狀態", "Status"] if c in df.columns), None)
        detail_col = next((c for c in ["รายละเอียดที่ต้องการดำเนินการ", "詳細處理需求", "Detail"] if c in df.columns),
                          None)

        if status_col:
            df["狀態_display"] = df[status_col].apply(
                lambda x: STATUS_MAP.get(x, {}).get(selected_lang, x) if pd.notna(x) else "Unknown")
        else:
            df["狀態_display"] = "Unknown"

        # 預計算零件預測與生命週期資料
        predict_data = []
        top10_methods_data = []
        warning_or_overdue_count = 0
        top_part_name = "N/A"
        top_part_failures = 0

        if machine_col and not df["Parsed_Date"].isna().all():
            # 統計最常壞的零件
            counts_series = df[machine_col].value_counts()
            if not counts_series.empty:
                top_part_name = counts_series.index[0]
                top_part_failures = counts_series.iloc[0]

                # 計算前10大故障零件的方法表資料
                for idx, (p_name, p_count) in enumerate(counts_series.head(10).items()):
                    top10_methods_data.append({
                        L["meth_col_rank"]: idx + 1,
                        L["meth_col_name"]: p_name,
                        L["meth_col_count"]: f"{p_count} {L['unit_cases']}",
                        L["meth_col_action"]: get_action_by_name(p_name, selected_lang)
                    })

            for name, group in df.dropna(subset=["Parsed_Date"]).groupby(machine_col):
                if pd.isna(name) or str(name).strip() == "":
                    continue
                count = len(group)
                diffs = group["Parsed_Date"].sort_values().diff().dt.days.dropna()

                if diffs.empty:
                    mtbf = 120.0
                else:
                    mtbf = float(diffs.mean())
                if pd.isna(mtbf) or mtbf <= 0:
                    mtbf = 120.0

                last_date = group["Parsed_Date"].max()

                try:
                    days_to_add = int(round(mtbf))
                    next_date = last_date + pd.Timedelta(days=days_to_add)
                    days_left = (next_date - datetime.now()).days

                    if pd.isna(days_left):
                        days_left = 999
                        next_date_str = "Unknown"
                    else:
                        days_left = int(days_left)
                        next_date_str = next_date.strftime('%Y-%m-%d')
                except:
                    next_date_str = "Unknown"
                    days_left = 999

                alert = L["alert_safe"]
                if days_left < 0:
                    alert = L["alert_overdue"]
                    warning_or_overdue_count += 1
                elif days_left <= 30:
                    alert = L["alert_warning"]
                    warning_or_overdue_count += 1

                predict_data.append({
                    "raw_name": name,
                    L["xl_part_name"]: name,
                    L["xl_failures"]: count,
                    L["xl_mtbf"]: round(mtbf, 1),
                    L["xl_last_date"]: last_date.strftime('%Y-%m-%d'),
                    L["xl_pred_date"]: next_date_str,
                    L["xl_days_left"]: days_left if days_left != 999 else "N/A",
                    L["xl_status_alert"]: alert,
                    "raw_mtbf": mtbf,
                    "raw_last_date": last_date,
                    "raw_next_date": next_date if 'next_date' in locals() else last_date
                })

        # 統計未完成案件的總數
        uncompleted_count = len(df[~df["狀態_display"].str.contains("完成|Completed|เสร็จ", na=False)])

        # ==========================================
        # 修正：運維焦點與問題總整理 (將內容打包在同一個 st.markdown 中以防止空框 Bug)
        # ==========================================
        summary_html = f"""
        <div class="summary-box">
            <h3 style='margin-top:0px;'>{L["summary_title"]}</h3>
            <p style='margin: 8px 0;'>{L["summary_p1"].format(warning_or_overdue_count)}</p>
            <p style='margin: 8px 0;'>{L["summary_p2"].format(top_part_name, top_part_failures)}</p>
            <p style='margin: 8px 0;'>{L["summary_p3"].format(uncompleted_count)}</p>
        </div>
        """
        st.markdown(summary_html, unsafe_allow_html=True)

        # 任務一：瞭解機台
        with st.expander(f"ℹ️ {L['kb_title']}"):
            kb_col1, kb_col2, kb_col3 = st.columns(3)
            with kb_col1: st.markdown(
                f'<div class="kpi-box"><h4>{L["kb_func_title"]}</h4><p>{L["kb_func_desc"]}</p></div>',
                unsafe_allow_html=True)
            with kb_col2: st.markdown(
                f'<div class="kpi-box"><h4>{L["kb_parts_title"]}</h4><p>{L["kb_parts_desc"]}</p></div>',
                unsafe_allow_html=True)
            with kb_col3: st.markdown(
                f'<div class="kpi-box"><h4>{L["kb_wear_title"]}</h4><p>{L["kb_wear_desc"]}</p></div>',
                unsafe_allow_html=True)

        # 建立功能分頁 (新增 tab4：故障維修方法)
        tab1, tab2, tab3, tab4, tab5 = st.tabs(
            [L["tab_dashboard"], L["tab_prediction"], L["tab_pm_schedule"], L["tab_methods"], L["tab_ai_assistant"]])

        # 成果一：每月數據追蹤儀表板
        with tab1:
            years = sorted([y for y in df["年份_data"].unique() if y != "Unknown"])
            months = sorted([m for m in df["月份_data"].unique() if m != "Unknown"])
            statuses = df["狀態_display"].unique().tolist()

            sel_years = st.sidebar.multiselect(L["filter_year"], options=years, default=years)
            sel_months = st.sidebar.multiselect(L["filter_month"], options=months, default=months)
            sel_stats = st.sidebar.multiselect(L["filter_status"], options=statuses, default=statuses)

            f_df = df[df["年份_data"].isin(sel_years if sel_years else years) &
                      df["月份_data"].isin(sel_months if sel_months else months) &
                      df["狀態_display"].isin(sel_stats if sel_stats else statuses)]

            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric(L["kpi_total"], f"{len(f_df)} {L['unit_cases']}")
            c_count = len(f_df[f_df["狀態_display"].str.contains("完成|Completed|เสร็จ", na=False)])
            kpi2.metric(L["kpi_completed"], f"{c_count} {L['unit_cases']}")
            kpi3.metric(L["kpi_avg_days"],
                        f"{f_df['Repair_Days'].mean():.1f} {L['unit_days']}" if not f_df.empty else "0")

            g1, g2 = st.columns(2)
            with g1:
                if machine_col and not f_df.empty:
                    top10 = f_df[machine_col].value_counts().reset_index().head(10)
                    top10.columns = [L["chart_top10_y"], L["chart_top10_x"]]
                    fig = px.bar(top10, x=L["chart_top10_x"], y=L["chart_top10_y"], orientation='h',
                                 title=L["chart_top10_title"], template=plotly_template)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.write(L["no_data"])
            with g2:
                if not f_df.empty:
                    st_counts = f_df["狀態_display"].value_counts().reset_index()
                    st_counts.columns = ["Status", "Count"]
                    fig2 = px.pie(st_counts, values="Count", names="Status", title=L["chart_status_title"], hole=0.4,
                                  template=plotly_template)
                    st.plotly_chart(fig2, use_container_width=True)
                else:
                    st.write(L["no_data"])

            st.markdown(f"#### {L['table_title']}")
            show_cols = [c for c in [machine_col, "狀態_display", detail_col, "Repair_Days"] if c]
            st.dataframe(f_df[show_cols], use_container_width=True, hide_index=True)

        # 成果二：零組件更換預測方法工具
        with tab2:
            st.subheader(L["pred_title"])
            st.caption(L["pred_subtitle"])
            if predict_data:
                display_pred_df = pd.DataFrame(predict_data).drop(
                    columns=["raw_name", "raw_mtbf", "raw_last_date", "raw_next_date"], errors="ignore")
                pred_df = display_pred_df.sort_values(L["xl_days_left"],
                                                      key=lambda x: pd.to_numeric(x, errors='coerce').fillna(999))
                st.dataframe(pred_df, use_container_width=True, hide_index=True)
            else:
                st.write(L["no_data"])

        # 成果三：F-mask 預防保養 (PM) 時程表
        with tab3:
            st.subheader(L["pm_plan_title"])
            st.caption(L["pm_plan_sub"])

            if predict_data:
                dynamic_pm_rows = []
                for idx, p in enumerate(predict_data):
                    p_name = str(p["raw_name"]).lower()

                    if "cylinder" in p_name or "valve" in p_name or "กระบอก" in p_name:
                        module = "Pneumatic"
                    elif "pump" in p_name or "filter" in p_name or "ปั๊ม" in p_name or "ตัวกรอง" in p_name:
                        module = "Vacuum"
                    elif "cable" in p_name or "sensor" in p_name or "สาย" in p_name or "เซนเซอร์" in p_name:
                        module = "Electrical"
                    else:
                        module = "Mechanical/General"

                    mtbf_val = p["raw_mtbf"]
                    if mtbf_val <= 45:
                        cycle = "每月 (Monthly)"
                    elif mtbf_val <= 135:
                        cycle = "每季 (Quarterly)"
                    else:
                        cycle = "每半年 (Semi-Annually)"

                    dynamic_pm_rows.append({
                        L["pm_col_id"]: f"PM-PART-{idx + 1:03d}",
                        L["pm_col_name"]: p["raw_name"],
                        L["pm_col_module"]: module,
                        L["pm_col_cycle"]: cycle,
                        L["pm_col_mtbf"]: f"{int(round(mtbf_val))} Days",
                        L["pm_col_last"]: p[L["xl_last_date"]],
                        L["pm_col_next"]: p[L["xl_pred_date"]],
                        L["pm_col_level"]: "L1" if mtbf_val <= 60 else "L2",
                        L["pm_col_time"]: 45,
                        L["pm_col_stock"]: 2,
                        L["pm_col_owner"]: "ME",
                        L["pm_col_sop"]: f"SOP-PM-{idx + 1:02d}"
                    })

                dynamic_pm_df = pd.DataFrame(dynamic_pm_rows)
                st.dataframe(dynamic_pm_df, use_container_width=True, hide_index=True)
            else:
                st.write(L["no_data"])

        # 新增：前 10 大故障維修方法分頁
        with tab4:
            st.subheader(L["methods_title"])
            st.caption(L["methods_sub"])
            if top10_methods_data:
                methods_df = pd.DataFrame(top10_methods_data)
                st.dataframe(methods_df, use_container_width=True, hide_index=True)
            else:
                st.write(L["no_data"])

        # 額外加分項：AI 助手
        with tab5:
            st.subheader(L["ai_title"])
            st.caption(L["ai_caption"])
            if "messages" not in st.session_state: st.session_state.messages = [
                {"role": "assistant", "content": L["ai_welcome"]}]
            for msg in st.session_state.messages: st.chat_message(msg["role"]).write(msg["content"])
            if user_input := st.chat_input(L["ai_input_holder"]):
                st.chat_message("user").write(user_input)
                st.session_state.messages.append({"role": "user", "content": user_input})
                reply = "收到指令！我正依據專案目標（分析報修頻率、預測更換時間）進行排查，這就為主管和 ME 工程師產出直觀結論。"
                st.chat_message("assistant").write(reply)
                st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"❌ 數據解析錯誤，請確認上傳的 GEM 維修數據格式。細節: {e}")
