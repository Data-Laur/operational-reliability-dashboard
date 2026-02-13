import streamlit as st
import pandas as pd
import altair as alt
import os
import re
import time
import random

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Lauren | Operational Audit", 
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THE "ACCESSIBILITY & BRAND" CSS ENGINE ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Figtree', sans-serif;
        color: #1e293b;
    }

    /* --- TAB ACCESSIBILITY FIX (NO ORANGE) --- */
    div[data-baseweb="tab-list"] {
        position: sticky;
        top: 0;
        z-index: 99999;
        background-color: white;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
    }
    
    /* Inactive Tab: High-Contrast Slate */
    button[data-baseweb="tab"] { 
        font-size: 16pt !important; 
        font-weight: 700 !important;
        color: #64748b !important; 
    }
    
    /* Active Tab: High-Contrast Indigo */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #4338ca !important;
        border-bottom-color: #4338ca !important;
    }

    /* --- THE PURPLE FORCE (ELIMINATING RED) --- */
    div[data-baseweb="checkbox"] div:first-child { background-color: #4338ca !important; border-color: #4338ca !important; }
    div[data-baseweb="checkbox"] svg { fill: white !important; }
    span[data-baseweb="tag"] { background-color: #4338ca !important; color: white !important; }
    .stCheckbox label span { color: #4338ca !important; }
    
    /* SIDEBAR COLLAPSE ICON (PURPLE) */
    button[data-testid="stSidebarCollapseButton"] {
        background-color: #4338ca !important;
        color: white !important;
        border-radius: 50% !important;
    }

    /* LAYOUT OPTIMIZATION */
    .block-container { padding-top: 1.5rem !important; }
    .spotlight-card {
        background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%);
        color: white;
        padding: 28px;
        border-radius: 16px;
        margin: 15px 0 35px 0;
        box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.4);
    }

    /* CARDS & METRICS */
    .review-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }
    div[data-testid="stMetric"] { border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px !important; }
    div[data-testid="stMetricValue"] { font-size: 1.4rem !important; }

    .no-review { color: #94a3b8; font-style: italic; font-size: 14px; }
    
    header { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data
def load_data():
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'taskrabbit_master_clean.csv')
    if not os.path.exists(file_path): return pd.DataFrame()

    parsed_data = []
    pattern = re.compile(r'^(.+?),(\d{4}-\d{2}-\d{2}),(.+?),(\d\.\d),(.*)$')
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()[1:]
            for line in lines:
                match = pattern.match(line.strip())
                if match:
                    cat, date_val, name, rating, raw = match.groups()
                    clean = re.sub(r',"?\s*\d+\.\d+.*$', '', raw).strip('"').strip("'").replace('""', '"')
                    parsed_data.append([cat.replace('"', '').strip(), date_val, name, rating, clean])
    except: return pd.DataFrame()

    df = pd.DataFrame(parsed_data, columns=['Category', 'Date', 'Client Name', 'Rating', 'Review'])
    df = df[~df['Category'].str.contains('Help Moving', case=False, na=False)]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    
    def map_domains(category):
        cat = str(category).lower()
        if 'computer' in cat: return 'Technical Support'
        elif any(x in cat for x in ['packing', 'moving']): return 'Logistics'
        elif 'assistant' in cat: return 'Operations'
        elif 'photo' in cat: return 'Visual Media'
        return 'General Ops'
    
    df['Domain'] = df['Category'].apply(map_domains)
    return df

df = load_data()

# --- SIDEBAR BRANDING ---
with st.sidebar:
    st.markdown("<h1 style='color:#4338ca; margin-top:0; margin-bottom:0;'>LAUREN</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:600; font-size:1rem; color:#64748b;'>Operational Audit</p>", unsafe_allow_html=True)
    st.divider()

    selected_domains = st.multiselect("Domains", sorted(df['Domain'].unique()), default=sorted(df['Domain'].unique()))
    
    st.write("**Categories**")
    available_cats = sorted(df[df['Domain'].isin(selected_domains)]['Category'].unique())
    selected_cats = [c for c in available_cats if st.checkbox(c, value=True, key=f"cb_{c}")]

    st.divider()
    st.download_button("📥 Download Reviews", df.to_csv(index=False).encode('utf-8'), "Lauren_Performance_Reviews_Audit.csv")

# --- MAIN DASHBOARD ---
t_audit, t_analytics = st.tabs(["📂 Audit Feed", "📈 Analytics & Insights"])

with t_audit:
    # --- CAROUSEL SPOTLIGHT ---
    hall_of_fame = [
        {"text": "Lauren is smart, pleasant and tenacious. Great combo! Hire her!! Very pleased.", "author": "Scott S.", "cat": "Computer Help"},
        {"text": "Lauren was fantastic! She was on time, communicative, and did an amazing job.", "author": "Emily R.", "cat": "Moving Help"},
        {"text": "Absolute professional. Solved the problem quickly and explained everything clearly.", "author": "Michael B.", "cat": "Technical Support"}
    ]
    if 'idx' not in st.session_state: st.session_state.idx = 0

    c_left, c_main, c_right = st.columns([1, 12, 1])
    with c_left:
        st.markdown("<div style='height:85px;'></div>", unsafe_allow_html=True)
        if st.button("❮"): st.session_state.idx = (st.session_state.idx - 1) % len(hall_of_fame)
    with c_right:
        st.markdown("<div style='height:85px;'></div>", unsafe_allow_html=True)
        if st.button("❯"): st.session_state.idx = (st.session_state.idx + 1) % len(hall_of_fame)
    
    item = hall_of_fame[st.session_state.idx]
    with c_main:
        st.markdown(f"""
        <div class="spotlight-card">
            <div style="font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.15em; margin-bottom: 8px; opacity: 0.8;">🌟 Featured Testimonial</div>
            <div style="font-size: 1.4rem; font-style: italic; font-weight: 500;">"{item['text']}"</div>
            <div style="margin-top: 12px; font-weight: 700;">— {item['author']} | {item['cat']}</div>
        </div>
        """, unsafe_allow_html=True)

    # Metrics
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lifetime Tasks", "561")
    m2.metric("Verified Sample", f"{len(df)}")
    m3.metric("Composite Rating", f"{df['Rating'].mean():.2f}")
    m4.metric("Operational Risk", "Negligible", delta="- 0% Risk", delta_color="inverse")

    st.divider()
    search = st.text_input("🔍 Search 191 verified records...", placeholder="Filter by keyword...")

    filtered_df = df[(df['Domain'].isin(selected_domains)) & (df['Category'].isin(selected_cats))].sort_values('Date', ascending=False)
    if search: filtered_df = filtered_df[filtered_df['Review'].str.contains(search, case=False, na=False)]

    if not filtered_df.empty:
        for _, row in filtered_df.iterrows():
            d_str = row['Date'].strftime('%B %d, %Y')
            stars = "★" * int(round(row['Rating']))
            rev = str(row['Review']).strip()
            
            # --- NO-QUOTE LOGIC ---
            clean_check = re.sub(r'[^\w\s]', '', rev.lower())
            if clean_check in ['nan', 'none', 'null', 'no text provided', 'no review', '']:
                rev_html = '<div class="no-review">No written review provided.</div>'
            else:
                rev_html = f'<div class="review-body">"{rev}"</div>'

            st.markdown(f"""
                <div class="review-card">
                    <div style="background-color:#e0e7ff; color:#4338ca; padding:4px 12px; border-radius:6px; font-weight:700; font-size:0.8rem; display:inline-block; margin-bottom:12px;">{row['Domain']}</div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight:700; font-size:1.2rem;">{row['Client Name']}</span>
                        <span style="color:#f59e0b; font-size:1.2rem;">{stars}</span>
                    </div>
                    <div style="font-size:1rem; color:#64748b; margin: 8px 0 12px 0;">📅 {d_str} • {row['Category']}</div>
                    {rev_html}
                </div>
            """, unsafe_allow_html=True)

with t_analytics:
    st.markdown("### 📊 Operational Insights")
    st.divider()
    
    # Growth Chart
    df_sorted = df.sort_values(by='Date')
    df_sorted['Cumulative Reviews'] = range(1, len(df_sorted) + 1)
    growth = alt.Chart(df_sorted).mark_area(line={'color':'#4338ca'}, color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='#4338ca', offset=0), alt.GradientStop(color='white', offset=1)], x1=1, x2=1, y1=1, y2=0)).encode(x=alt.X('Date:T', title='Timeline'), y=alt.Y('Cumulative Reviews:Q', title='Count')).properties(height=350)
    st.altair_chart(growth, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🗓️ Density Heatmap")
        heatmap_df = df.copy()
        heatmap_df['Year'] = heatmap_df['Date'].dt.year
        heatmap_df['Month'] = heatmap_df['Date'].dt.month_name()
        heatmap_data = heatmap_df.groupby(['Year', 'Month']).size().reset_index(name='Count')
        heatmap = alt.Chart(heatmap_data).mark_rect().encode(x=alt.X('Year:O'), y=alt.Y('Month:O', sort=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]), color=alt.Color('Count:Q', scale=alt.Scale(scheme='purples'))).properties(height=350)
        st.altair_chart(heatmap, use_container_width=True)
        
    with c2:
        st.markdown("#### 🗣️ Sentiment DNA")
        text = " ".join(df['Review'].astype(str).tolist()).lower()
        targets = {"Fast": text.count("fast"), "Efficient": text.count("efficient"), "Professional": text.count("professional"), "Kind": text.count("kind"), "Helpful": text.count("helpful")}
        nlp_df = pd.DataFrame(list(targets.items()), columns=['Trait', 'Mentions'])
        nlp_chart = alt.Chart(nlp_df).mark_bar(color='#4338ca').encode(x=alt.X('Mentions:Q'), y=alt.Y('Trait:N', sort='-x')).properties(height=350)
        st.altair_chart(nlp_chart, use_container_width=True)