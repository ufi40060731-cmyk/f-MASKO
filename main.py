with tab1:
    st.markdown("### 📊 關鍵維護指標總覽")
    
    # 確保 df 已經被正確讀取並處理
    if not df.empty:
        # 計算統計數據
        col1, col2, col3 = st.columns(3)
        
        # 1. 高頻故障機台 (使用機器名稱統計)
        top_part = df["ชื่อเครื่องจักร / อุปกรณ์"].value_counts().idxmax() if not df.empty else "N/A"
        
        # 2. 未結案工單數
        completed_mask = df["สถานะใบแจ้งซ่อม"].astype(str).str.contains("9.0|Closed|結案", na=False, case=False)
        uncompleted_count = len(df[~completed_mask])
        
        # 3. 總紀錄數
        total_records = len(df)
        
        # 顯示指標
        col1.metric("🔥 高頻故障機台", top_part)
        col2.metric("⏳ 未結案工單", f"{uncompleted_count} 件")
        col3.metric("📊 總維修紀錄", f"{total_records} 筆")
        
        st.divider()
        st.markdown("##### ⏳ 待處理工單清單")
        # 顯示前 10 筆未結案清單
        st.dataframe(df[~completed_mask][["ลำดับเอกสาร", "ชื่อเครื่องจักร / อุปกรณ์", "สถานะใบแจ้งซ่อม"]].head(10), use_container_width=True)
    else:
        st.info("⚠️ 請先在側邊欄上傳 Excel 檔案以顯示數據。")
