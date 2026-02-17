st.divider()
    
    # --- ASSET LOADING & FILTERS ---
    # Defensive check for the screenshot asset to prevent TypeError
    if os.path.exists("reviews_screenshot.png"):
        with st.expander("✅ Verified Platform Data", expanded=False):
            try:
                st.image("reviews_screenshot.png", use_container_width=True)
            except Exception:
                st.warning("Review assets are currently optimizing. Please refer to the README for visual audits.")
    
    st.divider()
    
    # Filters & Tags
    st.markdown('<div style="text-align: left; width: 100%;">', unsafe_allow_html=True)
    
    # Ensure Domain column exists before any UI calls refer to it
    if 'Domain' not in df.columns:
        df['Domain'] = df['Category'].apply(map_domains)
    
    # Logical Sequence: Define selected_domains before using it in filters
    unique_domains = sorted(df['Domain'].unique())
    selected_domains = st.multiselect("Domains", unique_domains, default=unique_domains)
    
    # Filter available categories based on the selected domains
    available_cats = sorted(df[df['Domain'].isin(selected_domains)]['Category'].unique())
    
    with st.expander("Filter Categories", expanded=False):
        selected_cats = [c for c in available_cats if st.checkbox(c, value=True, key=f"cb_{c}")]
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # Business Impact: CSV Export functionality
    st.download_button(
        label="📥 Download Reviews", 
        data=df.to_csv(index=False).encode('utf-8'), 
        file_name="Lauren_Chagaris_Taskrabbit_Performance_Audit.csv", 
        use_container_width=True
    )

# --- MAIN DASHBOARD BODY ---
st.markdown('<div style="background-color:#f8fafc; border-left: 5px solid #4338ca; padding: 20px; border-radius: 8px; margin-bottom: 25px;"><h2 style="margin-top:0; color:#1e293b;">The Chagaris Vibe Check</h2><p style="font-size:1.1rem; line-height:1.5; color:#475569;">This dashboard audits <strong>561 real-world tasks</strong> to provide empirical proof of reliability and problem-solving.</p></div>', unsafe_allow_html=True)

t_audit, t_analytics = st.tabs(["📂 Audit Feed", "📈 Analytics & Insights"])