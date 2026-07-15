import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime

# ==========================================
# 1. 網頁基本設定
# ==========================================
st.set_page_config(layout="wide", page_title="F-mask 運維極簡預測面板")

# ==========================================
# 2. 側邊欄控制（把語言與黑夜主題補回來）
# ==========================================
with st.sidebar:
    st.title("⚙️ 控制中心")
    # 補回泰文選項
    selected_lang = st.radio("🌐 選擇語言 / Language / ภาษา", ["繁體中文", "English", "ภาษาไทย"])
    # 網頁外觀切換
    theme_mode = st.radio("🌓 介面主題", ["☀️ 白天模式 (Light)", "🌙 黑夜模式 (Dark)"])
    st.divider()
    uploaded_file = st.file_uploader("📂 請上傳 GEM 更換紀錄 Excel (.xlsx)", type=["xlsx"])

# 根據選擇的主題，動態注入 CSS 去改變全網頁的底色與文字顏色，實現真黑夜模式
if "🌙" in theme_mode:
    bg_color = "#0e1117"
    text_color = "#ffffff"
    card_bg = "rgba(255, 255, 255, 0.05)"
    box_bg = "rgba(0, 102, 204, 0.2)"
    plotly_template = "plotly_dark"
else:
    bg_color = "#ffffff"
    text_color = "#31333f"
    card_bg = "rgba(0, 0, 0, 0.02)"
    box_bg = "#f0f7ff"
    plotly_template = "plotly"

st.markdown(f"""
<style>
    /* 全網頁背景與文字 */
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
    .info-box {{
        background-color: {box_bg};
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #0066cc;
        margin-bottom: 15px;
        color: {text_color};
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. 完整的三語字典（含完整泰文）
# ==========================================
LANG_DICT = {
    "繁體中文": {
        "title": "🛠️ F-mask 機台預防保養與零件預測儀表板",
        "proj_obj": "🎯 專案目標 (Objective)",
        "proj_obj_text": "充分瞭解 F-mask 機台及其維護歷史。制定 PM 計劃、建立簡單預測機制，並整合為 ME 每月檢查與主管報告格式。",
        "proj_rule": "💡 工具使用原則 (Tools Rule)",
        "proj_rule_text": "介面須簡單易懂，讓設備工程師 (ME) 和主管團隊都能一目了然；且在離職/專案結束後，ME 必須能持續使用並更新。",
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
        "sop_c4": "⚙️ 1. 執行外觀標準巡檢，清理環境積塵；2. 檢查緊固件是否鬆動；3. 核對操作參數更換備件。"
    },
    "English": {
        "title": "🛠️ F-mask Machine PM & Part Prediction Dashboard",
        "proj_obj": "🎯 Project Objective",
        "proj_obj_text": "Understand F-mask maintenance history. Establish PM schedule, predict part replacements, and format for ME monthly review & executive report.",
        "proj_rule": "💡 System Sustainability Rule",
        "proj_rule_text": "The interface must be simple and clear for both MEs and executives. The tool must remain usable and updatable by MEs after handoff.",
        "tab_dashboard": "📊 Monthly Tracking Dashboard",
        "tab_prediction": "🔮 Part Prediction Mechanism",
        "tab_pm_schedule": "📅 Master PM Schedule Plan",
        "kpi_alert": "🚨 High Risk / Near-Overdue Parts",
        "kpi_hotspot": "🔥 Top Failure Hotspot",
        "kpi_backlog": "⏳ Uncompleted Work Orders",
        "action_title": "📋 Top Failures & ME SOP Actions",
        "action_desc": "SOPs are automatically mapped. Left side shows raw failure count, right shows immediate solution.",
        "sop_col": "💡 Immediate ME SOP Action",
        "sop_c1": "🔧 1. Check cylinder seal leaks; 2. Ensure lubricator oil; 3. Tighten fixing screws.",
        "sop_c2": "🧼 1. Clean/replace filter monthly; 2. Monitor pump temp/noise; 3. Check vacuum lines.",
        "sop_c3": "⚡ 1. Clean sensor oil; 2. Check cable carrier friction; 3. Apply contact cleaner.",
        "sop_c4": "⚙️ 1. General inspection & dusting; 2. Check loose fasteners; 3. Replace on schedule."
    },
    "ภาษาไทย": {
        "title": "🛠️ แดชบอร์ดซ่อมบำรุงเชิงป้องกันและคาดการณ์อะไหล่ F-mask",
        "proj_obj": "🎯 วัตถุประสงค์โครงการ (Objective)",
        "proj_obj_text": "ทำความเข้าใจประวัติการบำรุงรักษาเครื่องจักร F-mask จัดทำแผน PM, สร้างระบบคาดการณ์อย่างง่าย และจัดรูปแบบสำหรับการตรวจสอบรายเดือนของ ME และรายงานผู้บริหาร",
        "proj_rule": "💡 หลักการใช้งานเครื่องมือ (Tools Rule)",
        "proj_rule_text": "อินเทอร์เฟซต้องเรียบง่ายและเข้าใจง่ายสำหรับทั้ง ME และทีมผู้บริหาร และเครื่องมือนี้ต้องสามารถใช้งานและอัปเดตต่อได้หลังจากสิ้นสุดโครงการ",
        "tab_dashboard": "📊 แดชบอร์ดติดตามรายเดือน (Dashboard)",
        "tab_prediction": "🔮 กลไกการคาดการณ์อายุการใช้งานอะไหล่ (Prediction)",
        "tab_pm_schedule": "📅 แผนตารางเวลา PM มาตรฐาน (PM Schedule)",
        "kpi_alert": "🚨 อะไหล่แนะนำให้เปลี่ยน/ความเสี่ยงสูง",
        "kpi_hotspot": "🔥 อะไหล่ที่เสียบ่อยที่สุด (กฎ GEM)",
        "kpi_backlog": "⏳ ใบแจ้งซ่อมที่อยู่ระหว่างดำเนินการ",
        "action_title": "📋 10 อันดับชิ้นส่วนชำรุดสูงสุด & แนวทางแก้ไข SOP",
        "action_desc": "ระบบจับคู่ SOP ให้โดยอัตโนมัติ ดูปัญหาทางซ้าย ดูวิธีแก้ทางขวา",
        "sop_col": "💡 แนวทางแก้ไขและวิธีซ่อมทันทีสำหรับ ME (SOP)",
        "sop_c1": "🔧 1. ตรวจสอบการรั่วซึมของซีลกระบอกสูบ 2. ตรวจสอบน้ำมันหล่อลื่นหล่อลื่น 3. ขันสกรูยึดให้แน่นหนา",
        "sop_c2": "🧼 1. ล้าง/เปลี่ยนไส้กรองปั๊มสูญญากาศทุกเดือน 2. ตรวจสอบอุณหภูมิและเสียง 3. ตรวจสอบท่อลม",
        "sop_c3": "⚡ 1. ล้างคราบน้ำมันเซนเซอร์ป้องกันสัญญาณผิดพลาด 2. ตรวจเช็คสายไฟในรางกระดูกงู 3. ใช้น้ำยาฉีดหน้าสัมผัส",
        "sop_c4": "⚙️ 1. ตรวจสอบภายนอกทั่วไปทำความสะอาดฝุ่น 2. ตรวจสอบน็อตที่หลวม 3. เปลี่ยนอะไหล่ตามกำหนด"
    }
}
L = LANG_DICT[selected_lang]

# ==========================================
# 4. 主畫面頂端專案目標
# ==========================================
st.title(L["title"])
st.markdown(f"""
<div class="info-box">
    <strong>{L['proj_obj']}</strong>：{L['proj_obj_text']}<br>
    <strong>{L['proj_rule']}</strong>：{L['proj_rule_text']}
</div>
""", unsafe_allow_html=True)
st.divider()


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
        df["ระยะเวลา (วัน)"] = pd.to_numeric(df["ระยะเวลา (วัน)"], errors="coerce")
    if "วันที่แจ้งซ่อม" in df.columns:
        df["Parsed_Date"] = pd.to_datetime(df["วันที่แจ้งซ่อม"], format="%d/%m/%Y %H:%M:%S", errors='coerce')
        mask = df["Parsed_Date"].isna()
        df.loc[mask, "Parsed_Date"] = pd.to_datetime(df.loc[mask, "วันที่แจ้งซ่อม"], errors='coerce')
    return df


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
        grouped = df.dropna(subset=["Parsed_Date"]).groupby("ชื่อเครื่องจักร / อุปกรณ์")

        for name, group in grouped:
            count = len(group)
            mtbf = group["Parsed_Date"].diff().dt.days.dropna().mean() if count > 1 else 180
            if pd.isna(mtbf) or mtbf <= 0: mtbf = 180
            last_repair = group["Parsed_Date"].max()
            days_left = ((last_repair + pd.Timedelta(days=int(mtbf))) - datetime.now()).days

            if days_left <= 30:
                overdue_count += 1

            predict_data.append({
                "🔧 零件組件名稱 / Part Name": name,
                "📊 歷史更換次數 / Count": f"{count} 次",
                "⏳ 平均壽命週期 (MTBF)": f"{round(mtbf, 1)} 天",
                "🔮 預估下次更換剩餘天數": f"{days_left} 天"
            })

            # 動態 PM 分類邏輯
            p_lower = str(name).lower()
            if count >= (max_failures * 0.7) or mtbf <= 30:
                cycle = "每週 (Weekly)"
                action = L["sop_c1"] if ("กระบอก" in p_lower or "cylinder" in p_lower) else "列為最高頻點檢對象，每週檢查氣密與外觀狀態。"
            elif count >= (max_failures * 0.4) or mtbf <= 90:
                cycle = "每月 (Monthly)"
                action = L["sop_c2"] if ("ปั๊ม" in p_lower or "pump" in p_lower) else "執行標準月度點檢，清潔周邊積塵，確認內部參數。"
            elif mtbf <= 180:
                cycle = "每季 (Quarterly)"
                action = L["sop_c3"] if ("สาย" in p_lower or "cable" in p_lower) else "每季預防性清潔接點，量測訊號是否衰減。"
            else:
                cycle = "每半年 (Semi-Annually)"
                action = L["sop_c4"]

            dynamic_pm_plan.append({
                "📅 建議點檢週期": cycle,
                "🔧 設備組件名稱": name,
                "📊 歷史故障頻率": f"更換過 {count} 次",
                "💡 ME工程師標準點檢行動": action
            })

        pm_df = pd.DataFrame(dynamic_pm_plan)
        cycle_order = {"每週 (Weekly)": 0, "每月 (Monthly)": 1, "每季 (Quarterly)": 2, "每半年 (Semi-Annually)": 3}
        if not pm_df.empty:
            pm_df["order"] = pm_df["📅 建議點檢週期"].map(cycle_order)
            pm_df = pm_df.sort_values("order").drop(columns=["order"])
    else:
        top_part, top_count = "N/A", 0
        pm_df = pd.DataFrame()

    uncompleted_count = len(df[~df["สถานะใบแจ้งซ่อม"].astype(str).str.contains("แล้วเสร็จ|Completed",
                                                                               na=False)]) if "สถานะใบแจ้งซ่อม" in df.columns else 0

    # ==========================================
    # 6. 三分頁架構
    # ==========================================
    tab1, tab2, tab3 = st.tabs([L["tab_dashboard"], L["tab_prediction"], L["tab_pm_schedule"]])

    # --- TAB 1: 儀表板 ---
    with tab1:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(L["kpi_alert"], f"{overdue_count} 項")
        with col2:
            st.metric(L["kpi_hotspot"], f"{top_part} ({top_count}次)")
        with col3:
            st.metric(L["kpi_backlog"], f"{uncompleted_count} 件")

        st.write("---")
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
                elif "สาย" in p_lower or "cable" in p_lower or "chain" in p_lower:
                    sop_desc = L["sop_c3"]
                else:
                    sop_desc = L["sop_c4"]

                top10_methods.append({
                    "排名 (Rank)": idx + 1,
                    "設備組件名稱 (Part)": p_name,
                    "更換頻率 (次數)": f"{p_count} 次",
                    L["sop_col"]: sop_desc
                })
            st.dataframe(pd.DataFrame(top10_methods), use_container_width=True, hide_index=True)

        st.write("---")
        c_col1, c_col2 = st.columns(2)
        with c_col1:
            if "ชื่อเครื่องจักร / อุปกรณ์" in df.columns:
                fig_m = px.bar(counts_series.head(10).reset_index(), x="count", y="ชื่อเครื่องจักร / อุปกรณ์",
                               orientation="h", title="Top 10 GEM 更換率分析圖", template=plotly_template)
                fig_m.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig_m, use_container_width=True)
        with c_col2:
            if "สถานะใบแจ้งซ่อม" in df.columns:
                fig_s = px.pie(df["สถานะใบแจ้งซ่อม"].value_counts().reset_index(), values="count",
                               names="สถานะใบแจ้งซ่อม",
                               title="工單結案狀態分佈", hole=0.4, template=plotly_template)
                st.plotly_chart(fig_s, use_container_width=True)

        with st.expander("🔍 點擊展開原始運維歷史明細檔案 (Deep Dive)"):
            st.dataframe(df, use_container_width=True, hide_index=True)

    # --- TAB 2: 預測 ---
    with tab2:
        st.markdown("### 🔮 歷史數據自動預測分析")
        if predict_data:
            st.dataframe(pd.DataFrame(predict_data), use_container_width=True, hide_index=True)
        else:
            st.write("暫無資料。")

    # --- TAB 3: 動態 PM 週期表 ---
    with tab3:
        st.markdown("### 📅 F-mask 預防保養 (PM) 標準週期表")
        if not pm_df.empty:
            st.dataframe(pm_df, use_container_width=True, hide_index=True)
        else:
            st.info("請先上傳檔案以生成動態點檢表。")
else:
    st.info("💡 請在左側邊欄上傳您的維修數據 Excel 檔案。")
