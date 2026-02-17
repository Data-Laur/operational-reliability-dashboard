with t_analytics:
    st.markdown("### 📊 Operational Insights")
    st.divider()
    
    # --- 1. GROWTH TIMELINE ---
    df_sorted = df.sort_values(by='Date')
    df_sorted['Cumulative Reviews'] = range(1, len(df_sorted) + 1)
    growth = alt.Chart(df_sorted).mark_area(
        line={'color':'#4338ca'}, 
        color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='#4338ca', offset=0), alt.GradientStop(color='white', offset=1)], x1=1, x2=1, y1=1, y2=0)
    ).encode(
        x=alt.X('Date:T', title='Timeline'), 
        y=alt.Y('Cumulative Reviews:Q', title='Review Velocity')
    ).properties(height=300)
    st.altair_chart(growth, use_container_width=True)
    
    st.divider()

    # --- 2. THE DUAL DNA ANALYSIS ---
    c1, c2 = st.columns(2)
    
    # Pre-processing text for both charts
    text_corpus = " ".join(df['Review'].astype(str).tolist()).lower()

    with c1:
        st.markdown("#### 🧠 Operational Pillars")
        st.caption("How your soft skills translate to business value.")
        
        # Mapping raw words to high-level architectural traits
        pillars = {
            "Execution Velocity": text_corpus.count("fast") + text_corpus.count("quick") + text_corpus.count("speed") + text_corpus.count("prompt"),
            "Composure (Calm/Easy)": text_corpus.count("calm") + text_corpus.count("easy") + text_corpus.count("patient") + text_corpus.count("stress-free"),
            "Communication Clarity": text_corpus.count("communicate") + text_corpus.count("talk") + text_corpus.count("conversation") + text_corpus.count("clear"),
            "Interpersonal IQ": text_corpus.count("nice") + text_corpus.count("friendly") + text_corpus.count("kind") + text_corpus.count("pleasant"),
            "High-Stakes Quality": text_corpus.count("beautiful") + text_corpus.count("perfect") + text_corpus.count("thorough") + text_corpus.count("organized")
        }
        
        pillar_df = pd.DataFrame(list(pillars.items()), columns=['Pillar', 'Mentions'])
        pillar_chart = alt.Chart(pillar_df).mark_bar(color='#4338ca', cornerRadiusEnd=4).encode(
            x=alt.X('Mentions:Q', title='Frequency'), 
            y=alt.Y('Pillar:N', sort='-x', title='')
        ).properties(height=350).configure_axis(labelLimit=300) # Prevents label cutoff
        
        st.altair_chart(pillar_chart, use_container_width=True)

    with c2:
        st.markdown("#### 🗣️ Raw Keyword Frequency")
        st.caption("Direct 'Word of Mouth' terminology from client reviews.")
        
        # High-frequency keywords identified in your audit
        raw_keywords = {
            "Great": text_corpus.count("great"),
            "Easy": text_corpus.count("easy"),
            "Quick/Fast": text_corpus.count("quick") + text_corpus.count("fast"),
            "Friendly": text_corpus.count("friendly"),
            "Wonderful": text_corpus.count("wonderful"),
            "Fantastic": text_corpus.count("fantastic"),
            "Professional": text_corpus.count("professional") + text_corpus.count("pro ")
        }
        
        raw_df = pd.DataFrame(list(raw_keywords.items()), columns=['Keyword', 'Count'])
        raw_chart = alt.Chart(raw_df).mark_bar(color='#6366f1', cornerRadiusEnd=4).encode(
            x=alt.X('Count:Q', title='Mentions'), 
            y=alt.Y('Keyword:N', sort='-x', title='')
        ).properties(height=350).configure_axis(labelLimit=300) # Prevents label cutoff
        
        st.altair_chart(raw_chart, use_container_width=True)
