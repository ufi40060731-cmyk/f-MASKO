import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timedelta
import io

# 1. 設定網頁標題與寬螢幕版面
st.set_page_config(layout="wide")

# ==========================================
# 2. 太陽/月亮 (日夜模式) 切換器
# ==========================================
theme_mode = st.sidebar.radio(
    "🌓 介面主題 / Theme Mode",
    ["☀️ 白天模式 (Light)", "🌙 黑夜模式 (Dark)"]
)

if "🌙 黑夜模式 (Dark)" in theme_mode:
    plotly_template = "plotly_dark"
    st.markdown(
        """
        <style>
        .stApp { background-color: #0E1117; color: #FAFAFA; }
        .stFileUploader label p { color: #E0E0E0 !important; }
        .stTabs [data-baseweb="tab"] p { color: #A0A5B5 !important; font-size: 16px; }
        .stTabs [data-baseweb="tab"][aria-selected="true"] p { color: #FF4B4B !important; font-weight: bold; }
        [data-testid="stMetricLabel"] p { color: #E0E0E0 !important; }
        [data-testid="stMetricValue"] > div { color: #FFFFFF !important; }
        .stSidebar .stMarkdown h3, .stSidebar label p { color: #E0E0E0 !important; }
        .kpi-box { background-color: #1E222B; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; margin-bottom: 10px; }
        </style>
        """,
        unsafe_allow_html=True
    )
else:
    plotly_template = "plotly"
    st.markdown(
        """
        <style>
        .stApp { background-color: #FFFFFF; color: #31333F; }
        .kpi-box { background-color: #F0F2F6; padding: 15px; border-radius: 8px; border-left: 5px solid #FF4B4B; margin-bottom: 10px; }
        </style>
        """,
        unsafe_allow_html=True
    )

# ==========================================
# 3. 多國語言字典設定 (加入週期表與 AI 助手詞庫)
# ==========================================
LANG_DICT = {
    "繁體中文": {
        "title": "🛠️ F-mask 機台預防保養(PM)與零件預測儀表板",
        "subtitle": "目標：分析 F-mask 維護歷史，預測零件更換頻率，供設備工程師 (ME) 與主管團隊每月追蹤。",
        "upload_label": "請選擇上傳維修數據 Excel 檔案 (.xlsx)",
        "download_btn": "📥 下載零件預測與更換方法報告 (Excel)",
        "tab_dashboard": "📊 每月數據追蹤 (Dashboard)",
        "tab_prediction": "🔮 零件更換預測與方法 (Prediction & Procedure)",
        "tab_pm_schedule": "📅 預防保養週期表 (PM Schedule Plan)",
        "tab_ai_assistant": "🤖 AI 智慧運維助手 (AI Assistant)",

        # 知識庫
        "kb_title": "💡 F-mask 機台基本知識庫 (Machine Knowledge Base)",
        "kb_func_title": "🔍 機台核心功能 (Function)",
        "kb_func_desc": "主要負責生產線上的光罩/掩膜版 (Mask) 精密對位、曝光與表面防護處理，確保製程良率。",
        "kb_parts_title": "⚙️ 主要零組件 (Key Components)",
        "kb_parts_desc": "包含高精密對位氣缸、進氣/真空泵浦、GEM 通訊模組、UV 導光條、輸送帶軸承及感測器線組。",
        "kb_wear_title": "🚨 常見磨損/損壞部位 (Wear & Tear)",
        "kb_wear_desc": "依據現場技術員與歷史反饋，氣缸密封件、泵浦濾網、輸送帶皮帶及電纜拖鏈（易斷線）為高磨損易耗部位。",

        "filter_title": "🔍 篩選條件 (Filters)",
        "filter_year": "選擇年份 (Year)",
        "filter_month": "選擇月份 (Month)",
        "filter_status": "選擇案件狀態 (Status)",
        "kpi_total": "總報修件數",
        "kpi_completed": "已完成件數",
        "kpi_avg_days": "平均維修天數",
        "unit_cases": "件",
        "unit_days": "天",
        "no_data": "無數據",
        "chart_top10_title": "📌 F-mask 機台/零件報修排行 Top 10",
        "chart_top10_x": "報修次數",
        "chart_top10_y": "設備零件名稱",
        "chart_status_title": "📈 維修案件狀態佔比",
        "chart_month_title": "📅 每月報修趨勢",
        "table_title": "📋 設備維護歷史明細",

        "col_doc": "文件流水號",
        "col_machine": "機台/零件名稱",
        "col_status": "目前狀態",
        "col_detail": "詳細處理需求",
        "col_duration": "維修耗時(天)",
        "info_tip": "💡 提示：請先在上方上傳 Excel 維修數據檔案以解鎖數據分析追蹤與 AI 助手。",

        # 預測頁面
        "pred_title": "🔮 智慧零件更換預測機制、失效根源與標準作業方法",
        "pred_subtitle": "系統已自動計算故障間隔、媒合歷史損壞的「根源原因」，並結合 SOP 更換方法供現場 ME 工程師對照作業。",
        "xl_part_name": "設備零件名稱",
        "xl_failures": "歷史報修次數",
        "xl_mtbf": "平均故障間隔 MTBF (天)",
        "xl_last_date": "最後一次更換日",
        "xl_pred_date": "下一次建議更換日",
        "xl_days_left": "剩餘壽命天數",
        "xl_status_alert": "維護狀態提示",
        "xl_root_cause": "失效根源原因分析 (Root Cause)",
        "xl_procedure": "建議更換與保養方法 (SOP)",

        "alert_safe": "✅ 正常",
        "alert_overdue": "🚨 已逾期",
        "alert_warning": "⚠️ 建議預防性更換",

        "rc_cylinder": "【氣壓不穩/密封磨損】工廠端供氣壓力瞬間波動，或長時間作動導致內部橡膠 O-ring 老化硬化漏氣。",
        "rc_pump": "【粉塵阻塞/負壓超載】過濾網未定期清理，微小顆粒進入泵體導致葉片卡死，或長時間真空吸附超載。",
        "rc_cable": "【反復應力/機械疲勞】拖鏈彎曲半徑設計不良，高頻率來回擺動導致內部銅線應力集中斷線。",
        "rc_default": "【常規機械磨損】達到零件材料疲勞壽命上限，需定期進行硬體潤滑與預防性更換。",

        "sop_content": (
            "1. 機台停機並執行 Lockout/Tagout 安全程序。\n"
            "2. 拆卸舊零件，使用無塵布與電子清潔劑清理安裝部。\n"
            "3. 換上新組件，使用扭力板手確認鎖緊螺絲。\n"
            "4. 進行 GEM 連線與單動測試，確認無訊號異常後復機。"
        ),

        # 週期表保養專用欄位
        "pm_plan_title": "📅 F-mask 機台標準預防保養 (PM) 維修週期表",
        "pm_plan_sub": "此為固定的標準機台維修計畫，包含保養層級、標準工時與庫存，供 ME 工程師作為固定點檢排程依據。",
        "pm_dl_btn": "📥 下載標準 PM 維修週期計畫表 (Excel)",
        "pm_col_id": "零件編號",
        "pm_col_name": "維修項目/零組件",
        "pm_col_module": "對應模組",
        "pm_col_cycle": "保養維修週期",
        "pm_col_mtbf": "預估壽命 (MTBF)",
        "pm_col_last": "前次維修日",
        "pm_col_next": "下次預定 PM 日",
        "pm_col_level": "保養層級",
        "pm_col_time": "標準工時 (Mins)",
        "pm_col_stock": "安全庫存量",
        "pm_col_owner": "負責單位",
        "pm_col_sop": "SOP 參考文件/方法",

        # AI 助手字串與新上傳標籤
        "ai_title": "🤖 F-mask AI 設備運維助手",
        "ai_caption": "AI 助手已綁定網頁初始數據。如果您想詢問「全新或其他 Excel 表格」，請直接在下方區塊丟入檔案。",
        "ai_upload_label": "📂 拖曳或點擊上傳要詢問的 Excel 數據報表 (.xlsx)",
        "ai_welcome": "你好！我是 F-mask AI 助手。👋\n\n我已經準備就緒！如果您有特定的 Excel 數據需要分析，可以**直接在下方丟入檔案**，並直接問我問題！（例如：'幫我統計這張表哪種零件壞最多？'）",
        "ai_input_holder": "請輸入您的提問..."
    },
    "English": {
        "title": "🛠️ F-mask Machine PM & Part Replacement Prediction Dashboard",
        "subtitle": "Objective: Analyze F-mask maintenance history, predict part replacement frequency for ME and management tracking.",
        "upload_label": "Please upload the maintenance data Excel file (.xlsx)",
        "download_btn": "📥 Download Part Prediction & Procedure Report (Excel)",
        "tab_dashboard": "📊 Monthly Tracking",
        "tab_prediction": "🔮 Part Prediction & Procedure",
        "tab_pm_schedule": "📅 PM Schedule Plan",
        "tab_ai_assistant": "🤖 AI Assistant",

        "kb_title": "💡 F-mask Machine Knowledge Base",
        "kb_func_title": "🔍 Core Function",
        "kb_func_desc": "Responsible for precise mask alignment, exposure, and surface protection to ensure process yield.",
        "kb_parts_title": "⚙️ Key Components",
        "kb_parts_desc": "Includes alignment cylinders, vacuum pumps, GEM communication modules, UV light guides, conveyor bearings, and sensor wiring.",
        "kb_wear_title": "🚨 High Wear Areas",
        "kb_wear_desc": "Based on technician feedback, cylinder seals, pump filters, conveyor belts, and cable carrier chains are highly prone to wear and breakage.",

        "filter_title": "🔍 Filters",
        "filter_year": "Select Year",
        "filter_month": "Select Month",
        "filter_status": "Select Status",
        "kpi_total": "Total Cases",
        "kpi_completed": "Completed Cases",
        "kpi_avg_days": "Avg Repair Duration",
        "unit_cases": "pcs",
        "unit_days": "days",
        "no_data": "No Data",
        "chart_top10_title": "📌 Top 10 F-mask Machine/Part Failures",
        "chart_top10_x": "Failure Count",
        "chart_top10_y": "Machine/Part Name",
        "chart_status_title": "📈 Repair Status Distribution",
        "chart_month_title": "📅 Monthly Repair Trend",
        "table_title": "📋 Equipment Maintenance History Details",

        "col_doc": "Doc Number",
        "col_machine": "Machine/Part",
        "col_status": "Status",
        "col_detail": "Failure Details",
        "col_duration": "Duration (Days)",
        "info_tip": "💡 Tip: Please upload the Excel file above first to unlock dashboard tracking.",

        "pred_title": "🔮 Intelligent Prediction, Root Cause Analysis & SOP Procedures",
        "pred_subtitle": "Calculated based on historical data with dynamic 'Root Cause' identification and standard procedures.",
        "xl_part_name": "Part Name",
        "xl_failures": "Failures Count",
        "xl_mtbf": "MTBF (Days)",
        "xl_last_date": "Last Replacement Date",
        "xl_pred_date": "Predicted Next Replacement",
        "xl_days_left": "Days Left",
        "xl_status_alert": "Status Alert",
        "xl_root_cause": "Root Cause Analysis",
        "xl_procedure": "Replacement Procedure (SOP)",

        "alert_safe": "✅ Safe",
        "alert_overdue": "🚨 Overdue",
        "alert_warning": "⚠️ Warning (Replace Soon)",

        "rc_cylinder": "[Pressure Instability / Seal Wear] CDA pressure fluctuation or long-term high frequency movement causing rubber O-ring aging and air leakage.",
        "rc_pump": "[Dust Clogging / Vacuum Overload] Failure to clean the filter mesh regularly, causing micro-particles to jam the pump internal vanes.",
        "rc_cable": "[Repeated Stress / Mechanical Fatigue] Suboptimal cable carrier bending radius combined with high-frequency travel causing internal copper core breakage.",
        "rc_default": "[Normal Fatigue & Wear] Reached the material fatigue limit. Requires periodic hardware hardware lubrication and preventive replacement.",

        "sop_content": (
            "1. Shut down the machine and execute the Lockout/Tagout (LOTO) safety procedure.\n"
            "2. Remove the old component, clean the mounting area with a lint-free cloth and electronic cleaner.\n"
            "3. Install the new part, use a torque wrench to ensure screws are properly tightened.\n"
            "4. Verify GEM online connectivity and perform a single-action test to ensure no signal anomalies before restart."
        ),

        # PM Plan English
        "pm_plan_title": "📅 F-mask Machine Preventive Maintenance (PM) Cycle Plan",
        "pm_plan_sub": "This is a fixed master schedule containing maintenance levels, standard man-hours, and safety stock for MEs.",
        "pm_dl_btn": "📥 Download Master PM Cycle Schedule (Excel)",
        "pm_col_id": "Part ID",
        "pm_col_name": "Maintenance Item / Component",
        "pm_col_module": "Module",
        "pm_col_cycle": "PM Interval",
        "pm_col_mtbf": "Estimated Lifespan (MTBF)",
        "pm_col_last": "Last Service Date",
        "pm_col_next": "Next PM Date",
        "pm_col_level": "PM Level",
        "pm_col_time": "Standard Time (Mins)",
        "pm_col_stock": "Safety Stock",
        "pm_col_owner": "Owner Team",
        "pm_col_sop": "SOP Reference File / Method",

        # AI Assistant English
        "ai_title": "🤖 F-mask AI Assistant",
        "ai_caption": "The AI assistant can query bound datasets or analyze any newly dropped Excel files.",
        "ai_upload_label": "📂 Drop or upload an Excel report to query (.xlsx)",
        "ai_welcome": "Hello! I am your F-mask AI assistant. 👋\n\nYou can **drop a new Excel file below** and ask me questions directly! (e.g., 'Analyze the failure trend in this sheet.')",
        "ai_input_holder": "Type your question here..."
    },
    "ภาษาไทย": {
        "title": "🛠️ แดชบอร์ดซ่อมบำรุงเชิงป้องกัน (PM) และคาดการณ์อะไหล่ F-mask",
        "subtitle": "เป้าหมาย: วิเคราะห์ประวัติการซ่อมบำรุง F-mask คาดการณ์ความถี่ในการเปลี่ยนอะไหล่สำหรับ ME และผู้บริหาร",
        "upload_label": "กรุณาอัปโหลดไฟล์ Excel ข้อมูลการซ่อมบำรุง (.xlsx)",
        "download_btn": "📥 ดาวน์โหลดรายงานการคาดการณ์และวิธีการเปลี่ยนอะไหล่ (Excel)",
        "tab_dashboard": "📊 ติดตามข้อมูลรายเดือน",
        "tab_prediction": "🔮 การคาดการณ์และวิธีการเปลี่ยนอะไหล่",
        "tab_pm_schedule": "📅 ตารางเวลาและรอบการบำรุงรักษา (PM Schedule Plan)",
        "tab_ai_assistant": "🤖 ผู้ช่วยอัจฉริยะ AI (AI Assistant)",

        "kb_title": "💡 คลังความรู้พื้นฐานเครื่องจักร F-mask",
        "kb_func_title": "🔍 ฟังก์ชันหลักของเครื่องจักร",
        "kb_func_desc": "รับผิดชอบในการจัดตำแหน่งหน้ากาก (Mask) ที่แม่นยำ การเปิดรับแสง และการปกป้องพื้นผิว เพื่อให้มั่นใจในผลผลิตของกระบวนการ",
        "kb_parts_title": "⚙️ ส่วนประกอบสำคัญ",
        "kb_parts_desc": "รวมถึงกระบอกสูบจัดตำแหน่ง, ปั๊มสุญญากาศ, โมดูลการสื่อสาร GEM, แถบนำแสง UV, แบริ่งสายพานลำเลียง และชุดสายไฟเซนเซอร์",
        "kb_wear_title": "🚨 จุดที่สึกหรอและเสียหายบ่อย",
        "kb_wear_desc": "จากความคิดเห็นของช่างเทคนิคและประวัติ ซีลกระบอกสูบ, ตัวกรองปั๊ม, สายพานลำเลียง และโซ่ลากสายเคเบิล (ขาดง่าย) เป็นจุดที่สึกหรอสูง",

        "filter_title": "🔍 เงื่อนไขการกรอง (Filters)",
        "filter_year": "เลือกปี (Year)",
        "filter_month": "เลือกเดือน (Month)",
        "filter_status": "เลือกสถานะ (Status)",
        "kpi_total": "จำนวนการแจ้งซ่อมทั้งหมด",
        "kpi_completed": "ดำเนินการเสร็จสิ้น",
        "kpi_avg_days": "ระยะเวลาซ่อมเฉลี่ย",
        "unit_cases": "รายการ",
        "unit_days": "วัน",
        "no_data": "ไม่มีข้อมูล",
        "chart_top10_title": "📌 10 อันดับเครื่องจักร/อะไหล่ที่แจ้งซ่อมบ่อยที่สุด",
        "chart_top10_x": "จำนวนครั้งที่แจ้งซ่อม",
        "chart_top10_y": "ชื่อเครื่องจักร / อุปกรณ์",
        "chart_status_title": "📈 สัดส่วนสถานะใบแจ้งซ่อม",
        "chart_month_title": "📅 แนวโน้มการแจ้งซ่อมรายเดือน",
        "table_title": "📋 รายละเอียดประวัติการซ่อมบำรุงอุปกรณ์",

        "col_doc": "ลำดับเอกสาร",
        "col_machine": "ชื่อเครื่องจักร / อุปกรณ์",
        "col_status": "สถานะปัจจุบัน",
        "col_detail": "รายละเอียดที่ต้องการดำเนินการ",
        "col_duration": "ระยะเวลา (วัน)",
        "info_tip": "💡 คำแนะนำ: กรุณาอัปโหลดไฟล์ Excel ด้านบนก่อนเพื่อเปิดใช้งานการวิเคราะห์ข้อมูลแดชบอร์ดและผู้ช่วย AI",

        "pred_title": "🔮 ระบบคาดการณ์อะไหล่, การวิเคราะห์สาเหตุที่แท้จริง (Root Cause) และ SOP",
        "pred_subtitle": "ระบบคำนวณรอบการชำรุด จับคู่สาเหตุรากเหง้าของปัญหา พร้อมขั้นตอนปฏิบัติงานสำหรับทีมวิศวกร ME",
        "xl_part_name": "ชื่อชิ้นส่วนอุปกรณ์",
        "xl_failures": "จำนวนครั้งที่ชำรุดในประวัติศาสตร์",
        "xl_mtbf": "ระยะเวลาเฉลี่ยก่อนการชำรุด MTBF (วัน)",
        "xl_last_date": "วันที่เปลี่ยนล่าสุด",
        "xl_pred_date": "วันที่แนะนำให้เปลี่ยนครั้งต่อไป",
        "xl_days_left": "จำนวนวันอายุการใช้งานที่เหลือ",
        "xl_status_alert": "การแจ้งเตือนสถานะการบำรุงรักษา",
        "xl_root_cause": "การวิเคราะห์สาเหตุรากเหง้า (Root Cause)",
        "xl_procedure": "วิธีการเปลี่ยนและบำรุงรักษาที่แนะนำ (SOP)",

        "alert_safe": "✅ ปกติ",
        "alert_overdue": "🚨 เกินกำหนด",
        "alert_warning": "⚠️ แนะนำให้เปลี่ยนเพื่อป้องกันไว้ก่อน",

        "rc_cylinder": "[ความดันลมไม่คงที่ / ซีลสึกหรอ] ความดันลมในโรงงานผันผวนชั่วขณะ หรือการทำงานความถี่สูงเป็นเวลานานทำให้โอริงยางเสื่อมสภาพและเกิดลมรั่ว",
        "rc_pump": "[กรองอุดตัน / สูญญากาศเกินพิกัด] ไม่ได้ทำความสะอาดแผ่นกรองฝุ่นตามกำหนด ทำให้อนุภาคขนาดเล็กเข้าไปติดในใบพัดปั๊มภายใน",
        "rc_cable": "[แรงเค้นซ้ำๆ / ความล้าทางกล] รัศมีการโค้งงอของกระดูกงูสายไฟไม่เหมาะสม ร่วมกับการขยับความถี่สูงทำให้สายทองแดงภายในขาด",
        "rc_default": "[ความล้าทางกลตามปกติ] ครบอายุการใช้งานของวัสดุ จำเป็นต้องหล่อลื่นฮาร์ดแวร์ตามระยะเวลาและเปลี่ยนชิ้นส่วนเพื่อป้องกัน",

        "sop_content": (
            "1. หยุดการทำงานของเครื่องจักรและปฏิบัติตามขั้นตอนความปลอดภัย Lockout/Tagout (LOTO)\n"
            "2. ถอดชิ้นส่วนเก่าออก ทำความสะอาดตำแหน่งติดตั้งด้วยผ้าที่ไม่มีขนและน้ำยาทำความสะอาดอิเล็กทรอนิกส์\n"
            "3. ใส่ชิ้นส่วนใหม่เข้าไป ใช้ประแจทอร์คเพื่อตรวจสอบการขันสกรูให้แน่นหนา\n"
            "4. ตรวจสอบการเชื่อมต่อออนไลน์ของระบบ GEM และทำการทดสอบการทำงานเดี่ยวเพื่อให้แน่ใจว่าไม่มีสัญญาณผิดปกติก่อนเริ่มเครื่องใหม่"
        ),

        # PM Plan Thai
        "pm_plan_title": "📅 ตารางเวลาและแผนรอบการซ่อมบำรุงเชิงป้องกัน (PM) F-mask",
        "pm_plan_sub": "นี่คือตารางแผนงานซ่อมบำรุงเครื่องจักรมาตรฐาน (ความถึ่การตรวจ, ระดับช่าง, เวลามาตรฐาน และ คลังอะไหล่ปลอดภัย)",
        "pm_dl_btn": "📥 ดาวน์โหลดแผนตารางเวลาการบำรุงรักษา PM (Excel)",
        "pm_col_id": "รหัสอะไหล่",
        "pm_col_name": "รายการซ่อมบำรุง / อะไหล่",
        "pm_col_module": "โมดูลที่เกี่ยวข้อง",
        "pm_col_cycle": "รอบเวลา PM แนะนำ",
        "pm_col_mtbf": "อายุใช้งานคาดการณ์ (MTBF)",
        "pm_col_last": "วันที่ซ่อมล่าสุด",
        "pm_col_next": "วันที่แผน PM ถัดไป",
        "pm_col_level": "ระดับการบำรุงรักษา",
        "pm_col_time": "เวลามาตรฐาน (นาที)",
        "pm_col_stock": "คลังอะไหล่ปลอดภัย",
        "pm_col_owner": "ทีมผู้รับผิดชอบ",
        "pm_col_sop": "เอกสารอ้างอิง SOP / วิธีการ",

        # AI Assistant Thai
        "ai_title": "🤖 ผู้ช่วยอัจฉริยะ AI ประจำเครื่องจักร",
        "ai_caption": "ระบบ AI สามารถวิเคราะห์ไฟล์ข้อมูลที่คุณโยนเข้าสู่ระบบที่นี่ได้ทันที",
        "ai_upload_label": "📂 ลากหรือคลิกเพื่ออัปโหลดไฟล์ Excel เพื่อสอบถามคำถาม (.xlsx)",
        "ai_welcome": "สวัสดีครับ! ผมคือ AI ผู้ช่วย 👋\n\nคุณสามารถ**อัปโหลดไฟล์ Excel ใหม่ที่ด้านล่างนี้** แล้วถามคำถามผมได้ทันทีครับ! (เช่น: 'ช่วยสรุปข้อมูลแผ่นงานนี้ให้หน่อย')",
        "ai_input_holder": "พิมพ์ข้อคำถามของคุณที่นี่..."
    },
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
    "4.1 ตรวจเช็คและแก้ปัญหาเบื้องต้นโดยช่าง": {"繁體中文": "4.1 檢修中 (Troubleshooting)",
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

selected_lang = st.sidebar.radio("🌐 選擇語言 / Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
L = LANG_DICT[selected_lang]

st.title(L["title"])
st.write(L["subtitle"])

uploaded_file = st.file_uploader(L["upload_label"], type=["xlsx"])


# =========================================================
# 4. 固定且精準的「標準預防保養(PM)維修週期表」資料庫
# =========================================================
def get_static_pm_plan():
    if selected_lang == "繁體中文":
        return [
            {"ID": "CYL-SEC-001", "Name": "氣缸密封件更換", "Module": "氣壓驅動模組", "Cycle": "每月 (Monthly)",
             "MTBF": "45 天", "Last": "2026-06-15", "Next": "2026-07-15", "Level": "L1 (常規)", "Time": 30, "Stock": 10,
             "Owner": "廠內維修組", "SOP": "SOP-PM-01-002: 檢查磨損、更換密封圈並塗抹潤滑油"},
            {"ID": "CBL-CHN-005", "Name": "電纜拖鏈結構檢查", "Module": "動態佈線模組", "Cycle": "每月 (Monthly)",
             "MTBF": "50 天", "Last": "2026-06-20", "Next": "2026-07-20", "Level": "L1 (常規)", "Time": 45, "Stock": 2,
             "Owner": "廠內維修組", "SOP": "SOP-PM-01-008: 清理灰塵，檢查鏈節是否有裂痕及卡頓"},
            {"ID": "VAC-FLT-012", "Name": "真空泵浦濾網清潔", "Module": "真空吸附模組", "Cycle": "每季 (Quarterly)",
             "MTBF": "90 天", "Last": "2026-05-10", "Next": "2026-08-10", "Level": "L2 (技術)", "Time": 60, "Stock": 5,
             "Owner": "廠內維修組", "SOP": "SOP-PM-02-015: 拆卸濾網使用高壓空氣清潔，視磨損更換"},
            {"ID": "BLT-DRV-023", "Name": "輸送帶皮帶張力調整", "Module": "傳動輸送模組", "Cycle": "每季 (Quarterly)",
             "MTBF": "120 天", "Last": "2026-05-15", "Next": "2026-09-15", "Level": "L2 (技術)", "Time": 90, "Stock": 4,
             "Owner": "設備工程部", "SOP": "SOP-PM-02-021: 測量皮帶張力值，調整配重或張緊螺絲"},
            {"ID": "MOT-SRV-088", "Name": "主軸伺服馬達校準", "Module": "精密定位模組",
             "Cycle": "每半年 (Semi-Annually)", "MTBF": "180 天", "Last": "2026-03-10", "Next": "2026-09-10",
             "Level": "L3 (進階)", "Time": 180, "Stock": 1, "Owner": "原廠工程師",
             "SOP": "SOP-PM-03-001: 使用雷射干涉儀進行多軸精度補償校正"},
            {"ID": "LGT-EXP-099", "Name": "曝光機光源模組檢測", "Module": "核心曝光模組",
             "Cycle": "每半年 (Semi-Annually)", "MTBF": "180 天", "Last": "2026-04-01", "Next": "2026-10-01",
             "Level": "L3 (進階)", "Time": 240, "Stock": 1, "Owner": "原廠工程師",
             "SOP": "SOP-PM-03-005: 量測光強衰減率，調整功率或更換燈源"},
            {"ID": "STR-FRM-000", "Name": "機台主結構硬體大修", "Module": "機體本體", "Cycle": "每年 (Annually)",
             "MTBF": "365 天", "Last": "2026-01-05", "Next": "2027-01-05", "Level": "L3 (進階)", "Time": 480,
             "Stock": 0, "Owner": "設備工程部", "SOP": "SOP-PM-04-001: 全面拆解結構件、更換耗損軸承、結構水平重測"}
        ]
    elif selected_lang == "English":
        return [
            {"ID": "CYL-SEC-001", "Name": "Cylinder Seal Replacement", "Module": "Pneumatic Module", "Cycle": "Monthly",
             "MTBF": "45 Days", "Last": "2026-06-15", "Next": "2026-07-15", "Level": "L1 (Routine)", "Time": 30,
             "Stock": 10, "Owner": "Internal Repair Team",
             "SOP": "SOP-PM-01-002: Check wear, replace O-ring, apply grease"},
            {"ID": "CBL-CHN-005", "Name": "Cable Chain Structure Check", "Module": "Wiring Module", "Cycle": "Monthly",
             "MTBF": "50 Days", "Last": "2026-06-20", "Next": "2026-07-20", "Level": "L1 (Routine)", "Time": 45,
             "Stock": 2, "Owner": "Internal Repair Team",
             "SOP": "SOP-PM-01-008: Clean dust, check chain link cracks or jams"},
            {"ID": "VAC-FLT-012", "Name": "Vacuum Pump Filter Cleaning", "Module": "Vacuum Module",
             "Cycle": "Quarterly", "MTBF": "90 Days", "Last": "2026-05-10", "Next": "2026-08-10",
             "Level": "L2 (Technical)", "Time": 60, "Stock": 5, "Owner": "Internal Repair Team",
             "SOP": "SOP-PM-02-015: Clean filter with high-pressure air, replace if worn"},
            {"ID": "BLT-DRV-023", "Name": "Conveyor Belt Tension Tuning", "Module": "Conveyor Module",
             "Cycle": "Quarterly", "MTBF": "120 Days", "Last": "2026-05-15", "Next": "2026-09-15",
             "Level": "L2 (Technical)", "Time": 90, "Stock": 4, "Owner": "ME Dept",
             "SOP": "SOP-PM-02-021: Measure tension values, adjust counterweights"},
            {"ID": "MOT-SRV-088", "Name": "Main Axis Servo Motor Calibration", "Module": "Precision Axis",
             "Cycle": "Semi-Annually", "MTBF": "180 Days", "Last": "2026-03-10", "Next": "2026-09-10",
             "Level": "L3 (Advanced)", "Time": 180, "Stock": 1, "Owner": "Vendor Engineer",
             "SOP": "SOP-PM-03-001: Laser interferometer multi-axis compensation"},
            {"ID": "LGT-EXP-099", "Name": "Exposure Light Module Inspection", "Module": "Exposure Module",
             "Cycle": "Semi-Annually", "MTBF": "180 Days", "Last": "2026-04-01", "Next": "2026-10-01",
             "Level": "L3 (Advanced)", "Time": 240, "Stock": 1, "Owner": "Vendor Engineer",
             "SOP": "SOP-PM-03-005: Measure light attenuation, adjust power or source"},
            {"ID": "STR-FRM-000", "Name": "Machine Main Frame Overhaul", "Module": "Main Frame", "Cycle": "Annually",
             "MTBF": "365 Days", "Last": "2026-01-05", "Next": "2027-01-05", "Level": "L3 (Advanced)", "Time": 480,
             "Stock": 0, "Owner": "ME Dept",
             "SOP": "SOP-PM-04-001: Disassemble frame, replace bearings, relevel structure"}
        ]
    else:  # ภาษาไทย
        return [
            {"ID": "CYL-SEC-001", "Name": "เปลี่ยนซีลกระบอกสูบ", "Module": "โมดูลนิวแมติกส์",
             "Cycle": "รายเดือน (Monthly)", "MTBF": "45 วัน", "Last": "2026-06-15", "Next": "2026-07-15",
             "Level": "L1 (ทั่วไป)", "Time": 30, "Stock": 10, "Owner": "ทีมซ่อมบำรุงภายใน",
             "SOP": "SOP-PM-01-002: ตรวจสอบความสึกหรอ เปลี่ยนโอริง ทาจาระบี"},
            {"ID": "CBL-CHN-005", "Name": "ตรวจสอบโครงสร้างกระดูกงูสายไฟ", "Module": "โมดูลเดินสายไฟ",
             "Cycle": "รายเดือน (Monthly)", "MTBF": "50 วัน", "Last": "2026-06-20", "Next": "2026-07-20",
             "Level": "L1 (ทั่วไป)", "Time": 45, "Stock": 2, "Owner": "ทีมซ่อมบำรุงภายใน",
             "SOP": "SOP-PM-01-008: ทำความสะอาดฝุ่น ตรวจรอยแตกหรือการติดขัด"},
            {"ID": "VAC-FLT-012", "Name": "ทำความสะอาดไส้กรองปั๊มสูญญากาศ", "Module": "โมดูลสูญญากาศ",
             "Cycle": "รายไตรมาส (Quarterly)", "MTBF": "90 วัน", "Last": "2026-05-10", "Next": "2026-08-10",
             "Level": "L2 (เทคนิค)", "Time": 60, "Stock": 5, "Owner": "ทีมซ่อมบำรุงภายใน",
             "SOP": "SOP-PM-02-015: เป่ากรองด้วยลมแรงดันสูง เปลี่ยนหากสึกหรอ"},
            {"ID": "BLT-DRV-023", "Name": "ปรับความตึงสายพานลำเลียง", "Module": "โมดูลระบบลำเลียง",
             "Cycle": "รายไตรมาส (Quarterly)", "MTBF": "120 วัน", "Last": "2026-05-15", "Next": "2026-09-15",
             "Level": "L2 (เทคนิค)", "Time": 90, "Stock": 4, "Owner": "แผนก ME",
             "SOP": "SOP-PM-02-021: วัดค่าความตึง ปรับตุ้มถ่วงหรือสกรูความตึง"},
            {"ID": "MOT-SRV-088", "Name": "คาลิเบรตเซอร์โวมоเตอร์แกนหลัก", "Module": "โมดูลกำหนดตำแหน่ง",
             "Cycle": "ทุกครึ่งปี (Semi-Annually)", "MTBF": "180 วัน", "Last": "2026-03-10", "Next": "2026-09-10",
             "Level": "L3 (ขั้นสูง)", "Time": 180, "Stock": 1, "Owner": "วิศวกรผู้ผลิต (Vendor)",
             "SOP": "SOP-PM-03-001: 使用雷射干涉儀進行多軸精度補償校正"},
            {"ID": "LGT-EXP-099", "Name": "ตรวจสอบโมดูลแหล่งกำเนิดแสงเอ็กซ์โปเชอร์", "Module": "โมดูลแสงเอ็กซ์โปเชอร์",
             "Cycle": "ทุกครึ่งปี (Semi-Annually)", "MTBF": "180 วัน", "Last": "2026-04-01", "Next": "2026-10-01",
             "Level": "L3 (ขั้นสูง)", "Time": 240, "Stock": 1, "Owner": "วิศวกรผู้ผลิต (Vendor)",
             "SOP": "SOP-PM-03-005: วัดการลดทอนของแสง ปรับกำลังไฟหรือเปลี่ยนแหล่งแสง"},
            {"ID": "STR-FRM-000", "Name": "โอเวอร์ฮอลโครงสร้างหลักเครื่องจักร", "Module": "โครงสร้างหลัก",
             "Cycle": "ประจำปี (Annually)", "MTBF": "365 วัน", "Last": "2026-01-05", "Next": "2027-01-05",
             "Level": "L3 (ขั้นสูง)", "Time": 480, "Stock": 0, "Owner": "แผนก ME",
             "SOP": "SOP-PM-04-001: ถอดประกอบโครงสร้าง เปลี่ยนแบริ่งที่สึกหรอ ปรับระดับโครงสร้างใหม่"}
        ]


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
            elif len(val) >= 4 and val[:4].isdigit():
                return val[:4]
            return "Unknown"

        def extract_month(dt):
            if pd.notna(dt): return f"{dt.month:02d}"
            return "Unknown"

        df["年份_data"] = df["วันที่แจ้งซ่อม"].apply(extract_year).astype(str)
        df["月份_data"] = df["Parsed_Date"].apply(extract_month).astype(str)
    else:
        df["年份_data"] = "Unknown"
        df["月份_data"] = "Unknown"
        df["Parsed_Date"] = pd.NaT

    return df


if uploaded_file is not None:
    try:
        df = load_and_clean_data(uploaded_file)

        if "สถานะใบแจ้งซ่อม" in df.columns:
            df["狀態_display"] = df["สถานะใบแจ้งซ่อม"].apply(
                lambda x: STATUS_MAP.get(x, {}).get(selected_lang, x) if pd.notna(x) else x)
        else:
            df["狀態_display"] = "Unknown"

        # 機台基本知識庫區塊
        st.markdown(f"### {L['kb_title']}")
        kb_col1, kb_col2, kb_col3 = st.columns(3)
        with kb_col1:
            st.markdown(
                f'<div class="kpi-box"><h4>{L["kb_func_title"]}</h4><p style="font-size:14px; margin:0;">{L["kb_func_desc"]}</p></div>',
                unsafe_allow_html=True)
        with kb_col2:
            st.markdown(
                f'<div class="kpi-box"><h4>{L["kb_parts_title"]}</h4><p style="font-size:14px; margin:0;">{L["kb_parts_desc"]}</p></div>',
                unsafe_allow_html=True)
        with kb_col3:
            st.markdown(
                f'<div class="kpi-box"><h4>{L["kb_wear_title"]}</h4><p style="font-size:14px; margin:0;">{L["kb_wear_desc"]}</p></div>',
                unsafe_allow_html=True)
        st.write("---")


        # 開啟 4 個分頁：將 AI 智慧助手完全獨立成第 4 個分頁
        tab1, tab2, tab3, tab4 = st.tabs(
            [L["tab_dashboard"], L["tab_prediction"], L["tab_pm_schedule"], L["tab_ai_assistant"]])

        # 計算預測分頁的動態數據
        predict_data = []
        if "ชื่อเครื่องจักร / อุปกรณ์" in df.columns and not df["Parsed_Date"].isna().all():
            grouped = df.dropna(subset=["Parsed_Date"]).groupby("ชื่อเครื่องจักร / อุปกรณ์")
            for name, group in grouped:
                group = group.sort_values("Parsed_Date")
                count = len(group)
                mtbf = group["Parsed_Date"].diff().dt.days.dropna().mean() if count > 1 else 180
                if pd.isna(mtbf) or mtbf <= 0: mtbf = 180
                last_repair = group["Parsed_Date"].max()
                next_predict_date = last_repair + pd.Timedelta(days=int(mtbf)) if pd.notna(last_repair) else pd.NaT
                days_left = (next_predict_date - datetime.now()).days if pd.notna(next_predict_date) else 0

                status_alert = L["alert_safe"]
                if days_left < 0:
                    status_alert = L["alert_overdue"]
                elif days_left <= 30:
                    status_alert = L["alert_warning"]

                part_lower = str(name).lower()
                if "กระบอก" in part_lower or "cylinder" in part_lower:
                    assigned_root_cause = L["rc_cylinder"]
                elif "ปั๊ม" in part_lower or "pump" in part_lower:
                    assigned_root_cause = L["rc_pump"]
                elif "สาย" in part_lower or "cable" in part_lower or "chain" in part_lower:
                    assigned_root_cause = L["rc_cable"]
                else:
                    assigned_root_cause = L["rc_default"]

                predict_data.append({
                    L["xl_part_name"]: name,
                    L["xl_failures"]: count,
                    L["xl_mtbf"]: round(mtbf, 1),
                    L["xl_last_date"]: last_repair.strftime('%Y-%m-%d') if pd.notna(last_repair) else "N/A",
                    L["xl_pred_date"]: next_predict_date.strftime('%Y-%m-%d') if pd.notna(next_predict_date) else "N/A",
                    L["xl_days_left"]: days_left,
                    L["xl_status_alert"]: status_alert,
                    L["xl_root_cause"]: assigned_root_cause,
                    L["xl_procedure"]: L["sop_content"]
                })

        pred_df = pd.DataFrame(predict_data).sort_values(by=L["xl_days_left"]) if predict_data else pd.DataFrame()

        # ==========================================
        # TAB 1: 每月數據追蹤儀表板
        # ==========================================
        with tab1:
            st.sidebar.markdown(f"### {L['filter_title']}")
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
                df["年份_data"].isin(selected_years) &
                df["月份_data"].isin(selected_months) &
                df["狀態_display"].isin(selected_status)
                ]

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(L["kpi_total"], f"{len(filtered_df)} {L['unit_cases']}")
            with col2:
                c_count = len(filtered_df[filtered_df["สถานะใบแจ้งซ่อม"].astype(str).str.contains("แล้วเสร็จ",
                                                                                                  na=False)]) if "สถานะใบแจ้งซ่อม" in filtered_df.columns else 0
                st.metric(L["kpi_completed"], f"{c_count} {L['unit_cases']}")
            with col3:
                avg_days = filtered_df["ระยะเวลา (วัน)"].mean() if "ระยะเวลา (วัน)" in filtered_df.columns else pd.NA
                st.metric(L["kpi_avg_days"], f"{avg_days:.1f} {L['unit_days']}" if pd.notna(avg_days) else L["no_data"])

            c_col1, c_col2 = st.columns(2)
            with c_col1:
                if "ชื่อเครื่องจักร / อุปกรณ์" in filtered_df.columns and not filtered_df.empty:
                    machine_counts = filtered_df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts().reset_index().head(10)
                    machine_counts.columns = [L["chart_top10_y"], L["chart_top10_x"]]
                    fig_m = px.bar(machine_counts, x=L["chart_top10_x"], y=L["chart_top10_y"], orientation="h",
                                   title=L["chart_top10_title"], template=plotly_template)
                    fig_m.update_layout(yaxis={"categoryorder": "total ascending"})
                    st.plotly_chart(fig_m, use_container_width=True)
                else:
                    st.write(L["no_data"])
            with c_col2:
                if "狀態_display" in filtered_df.columns and not filtered_df.empty:
                    status_counts = filtered_df["狀態_display"].value_counts().reset_index()
                    status_counts.columns = [L["col_status"], L["unit_cases"]]
                    fig_s = px.pie(status_counts, values=L["unit_cases"], names=L["col_status"],
                                   title=L["chart_status_title"], hole=0.4, template=plotly_template)
                    fig_s.update_traces(textposition='outside', textinfo='percent', automargin=True)
                    fig_s.update_layout(showlegend=True,
                                        legend=dict(orientation="h", yanchor="top", y=-0.1, xanchor="center", x=0.5),
                                        margin=dict(t=40, b=80, l=50, r=50))
                    st.plotly_chart(fig_s, use_container_width=True)
                else:
                    st.write(L["no_data"])

            st.write("---")
            st.subheader(L["table_title"])
            cols_to_show = ["ลำดับเอกสาร", "ชื่อเครื่องจักร / อุปกรณ์", "狀態_display", "รายละเอียดที่ต้องการดำเนินการ",
                            "ระยะเวลา (วัน)", "年份_data", "月份_data"]
            existing_cols = [c for c in cols_to_show if c in filtered_df.columns]
            if not filtered_df.empty and existing_cols:
                st.dataframe(filtered_df[existing_cols], use_container_width=True, hide_index=True)
            else:
                st.write(L["no_data"])
        # ==========================================
        # TAB 2: 🔮 零件更換預測頁面
        # ==========================================
        with tab2:
            st.subheader(L["pred_title"])
            st.write(L["pred_subtitle"])
            if not pred_df.empty:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    pred_df.to_excel(writer, index=False, sheet_name='Predict_Report')
                buffer.seek(0)
                st.download_button(label=L["download_btn"], data=buffer,
                                   file_name=f"Predict_Report_{selected_lang}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                                   mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                st.write("---")
                st.dataframe(pred_df, use_container_width=True, hide_index=True)
            else:
                st.write(L["no_data"])

        # ==========================================
        # TAB 3: 📅 預防保養週期表 (內建大計畫表)
        # ==========================================
        with tab3:
            st.subheader(L["pm_plan_title"])
            st.write(L["pm_plan_sub"])

            raw_pm_plan = get_static_pm_plan()
            plan_df = pd.DataFrame(raw_pm_plan)
            plan_df.columns = [
                L["pm_col_id"], L["pm_col_name"], L["pm_col_module"], L["pm_col_cycle"],
                L["pm_col_mtbf"], L["pm_col_last"], L["pm_col_next"], L["pm_col_level"],
                L["pm_col_time"], L["pm_col_stock"], L["pm_col_owner"], L["pm_col_sop"]
            ]

            pm_buffer = io.BytesIO()
            with pd.ExcelWriter(pm_buffer, engine='openpyxl') as writer:
                plan_df.to_excel(writer, index=False, sheet_name='PM_Master_Plan')
            pm_buffer.seek(0)

            st.download_button(
                label=L["pm_dl_btn"],
                data=pm_buffer,
                file_name=f"F-mask_PM_Master_Plan_{selected_lang}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            st.write("---")
            st.dataframe(plan_df, use_container_width=True, hide_index=True)

        # ==========================================
        # TAB 4: 🤖 AI 智慧運維助手 (包含獨立上傳區)
        # ==========================================
        with tab4:
            st.subheader(L["ai_title"])
            st.caption(L["ai_caption"])

            # 🔥 關鍵新增：在第四分頁聊天框上方，單獨增設一個 Excel 上傳區
            ai_file = st.file_uploader(L["ai_upload_label"], type=["xlsx"], key="ai_exclusive_uploader")

            st.write("---")

            # 初始化聊天紀錄 (綁定在 session_state)
            if "messages" not in st.session_state:
                st.session_state.messages = [
                    {"role": "assistant", "content": L["ai_welcome"]}
                ]

            # 顯示歷史對話紀錄
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.write(msg["content"])

            # 接收使用者對話輸入
            if user_input := st.chat_input(L["ai_input_holder"]):
                # 顯示使用者發送的訊息
                with st.chat_message("user"):
                    st.write(user_input)
                st.session_state.messages.append({"role": "user", "content": user_input})

                # AI 回應核心邏輯 (串接現場 DataFrame 進行動態分析)
                with st.chat_message("assistant"):
                    response_placeholder = st.empty()
                    q = user_input.lower()

                    # 決定 AI 要去讀「主畫面上傳的檔」還是「AI 分頁專屬上傳的檔」
                    target_df = df  # 預設讀大主頁的 Excel
                    file_source_msg = "（已綁定主儀表板數據集）"

                    if ai_file is not None:
                        try:
                            target_df = load_and_clean_data(ai_file)
                            file_source_msg = f"（📊 已成功讀取您在此分頁丟入的新檔案：`{ai_file.name}`）"
                        except:
                            file_source_msg = "（⚠️ 偵測到新檔案但讀取失敗，改用原主頁數據）"

                    if "氣缸" in q or "cylinder" in q:
                        if selected_lang == "繁體中文":
                            reply = f"**【AI 專家分析：氣缸組件】**\n\n根據標準維修週期，**氣缸密封件**保養週期為每月一次（壽命約 45 天）。歷史損壞主因通常為【工廠端供氣壓力瞬間波動】，更換時請對照 **SOP-PM-01-002**，更換 O-ring 並均勻塗抹潤滑油。"
                        elif selected_lang == "English":
                            reply = f"**【AI Expert Analysis: Cylinder Component】**\n\nAccording to the schedule, the **Cylinder Seals** have a monthly cycle (lifespan ~45 days). The historical failure is often due to CDA pressure fluctuations. Please follow **SOP-PM-01-002** to replace the O-ring and apply specialized grease."
                        else:
                            reply = f"**【AI วิเคราะห์ผู้เชี่ยวชาญ: ซีลกระบอกสูบ】**\n\nตามตารางรอบเวลา **ซีลกระบอกสูบ** มีรอบการบำรุงรักษาทุกเดือน (อายุการใช้งานประมาณ 45 วัน) สาเหตุหลักที่พบบ่อยคือความดันลมในโรงงานผันผวน กรุณาปฏิบัติตาม **SOP-PM-01-002** ในการเปลี่ยนโอริงและทาจาระบี"

                    elif any(k in q for k in ["最常壞", "排行", "top", "最多"]):
                        if not target_df.empty and "ชื่อเครื่องจักร / อุปกรณ์" in target_df.columns:
                            top_part = target_df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts().idxmax()
                            top_count = target_df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts().max()

                            if selected_lang == "繁體中文":
                                reply = f"**【📊 AI 即時數據分析】** {file_source_msg}\n\n根據數據分析，目前報修次數最多的零件是 **「{top_part}」**，累計發生了 **{top_count} 次** 故障。建議 ME 團隊在下次排程中優先針對此項目進行重點點檢！"
                            elif selected_lang == "English":
                                reply = f"**【📊 AI Live Data Analysis】** {file_source_msg}\n\nBased on the analysis, the most frequently repaired part is **\"{top_part}\"** with **{top_count} total failures**. It is highly recommended that the ME team prioritize this item."
                            else:
                                reply = f"**【📊 AI การวิเคราะห์ข้อมูลสด】** {file_source_msg}\n\nจากข้อมูล อะไหล่ที่มีการแจ้งซ่อมบ่อยที่สุดคือ **\"{top_part}\"** โดยมีการชำรุดทั้งหมด **{top_count} ครั้ง** แนะนำให้ทีม ME จัดลำดับความสำคัญในการตรวจสอบชิ้นส่วนนี้ก่อน"
                        else:
                            if selected_lang == "繁體中文":
                                reply = f"❌ 數據庫欄位不符合或尚未偵測到數據。{file_source_msg}"
                            elif selected_lang == "English":
                                reply = f"❌ Data column not matched or empty. {file_source_msg}"
                            else:
                                reply = f"❌ ไม่พบข้อมูลหรือคอลัมน์ไม่ถูกต้อง {file_source_msg}"

                    elif any(k in q for k in ["保養", "sop", "步驟"]):
                        reply = f"**【🛠️ F-mask Standard SOP Procedure】**\n\n{L['sop_content']}"

                    else:
                        if selected_lang == "繁體中文":
                            reply = f"我收到了您的問題！{file_source_msg}\n\n我隨時可以為您分析這份表格中的具體組件（如：氣缸、泵浦）狀態或統計排行喔！"
                        elif selected_lang == "English":
                            reply = f"I received your question! {file_source_msg}\n\nFeel free to ask about specific components like cylinders, pumps, or stats based on this sheet."
                        else:
                            reply = f"ได้รับคำถามแล้วครับ! {file_source_msg}\n\nสามารถถามเจาะจงรายชิ้นส่วนหรือสถิติจากตารางนี้ได้เลยครับ"

                    response_placeholder.write(reply)
                    st.session_state.messages.append({"role": "assistant", "content": reply})

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.info(L["info_tip"])
