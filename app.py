import streamlit as st
import pandas as pd
import altair as alt
import os
import re
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Chagaris | Vibe Check", 
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER: BASE64 IMAGE LOADER ---
def get_img_as_base64(file_path):
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# --- THE BRAND & UI ENGINE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Figtree', sans-serif;
        color: #1e293b;
    }

    /* --- GLOBAL COLOR OVERRIDE --- */
    :root {
        --primary-color: #4338ca;
        --text-color: #1e293b;
    }

    /* --- NUCLEAR TAGS FIX (Kills the Orange Tags) --- */
    span[data-baseweb="tag"] {
        background-color: #e0e7ff !important; /* Light Indigo Background */
        border: 1px solid #4338ca !important;
    }
    
    /* The text inside the tag */
    span[data-baseweb="tag"] span {
        color: #4338ca !important; 
        font-weight: 600 !important;
    }
    
    /* The 'X' to close the tag */
    span[data-baseweb="tag"] svg {
        fill: #4338ca !important;
    }

    /* --- NUCLEAR CHECKBOX FIX (Kills the Orange Check) --- */
    /* The box itself when checked */
    div[data-testid="stCheckbox"] label span[aria-checked="true"] {
        background-color: #4338ca !important;
        border-color: #4338ca !important;
    }
    
    /* The border when unchecked */
    div[data-testid="stCheckbox"] label span[aria-checked="false"] {
        border-color: #4338ca !important;
        background-color: white !important;
    }

    /* --- HAMBURGER MENU FIX --- */
    button[data-testid="stSidebarCollapsedControl"] {
        color: #4338ca !important;
        background-color: #f1f5f9 !important;
        border: 2px solid #4338ca !important;
        border-radius: 8px !important;
        height: 45px !important;
        width: 45px !important;
        padding: 5px !important;
    }
    
    button[data-testid="stSidebarCollapsedControl"] svg, 
    button[data-testid="stSidebarCollapsedControl"] svg path {
        fill: #4338ca !important;
        stroke: #4338ca !important;
    }

    /* --- DOMAIN TAG BOX FIX (Taller) --- */
    .stMultiSelect div[data-baseweb="select"] > div {
        max-height: none !important;
        overflow-y: visible !important;
        white-space: normal !important;
    }
    .stMultiSelect span[data-baseweb="tag"] {
        margin-bottom: 5px !important;
    }

    /* --- METRIC FONT SIZE FIX --- */
    div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetricValue"] {
        font-size: 1.8rem !important; 
    }

    /* --- TAB FONT SIZE FIX (Larger) --- */
    button[data-baseweb="tab"] { 
        font-size: 20px !important; 
        font-weight: 700 !important; 
        color: #64748b !important; 
    }
    button[data-baseweb="tab"][aria-selected="true"] { 
        color: #4338ca !important; 
        border-bottom-color: #4338ca !important; 
    }
    
    /* Tab Container Padding */
    div[data-baseweb="tab-list"] { 
        padding: 15px 0; 
        border-bottom: 2px solid #f1f5f9; 
    }

    /* Review Cards Styling */
    .review-card { background-color: #ffffff; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 20px; text-align: left; }
    .no-review { color: #64748b; font-style: italic; font-size: 14px; }
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
                    cat, d_val, name, rating, raw = match.groups()
                    clean = re.sub(r',"?\s*\d+\.\d+.*$', '', raw).strip('"').strip("'").replace('""', '"')
                    parsed_data.append([cat.replace('"', '').strip(), d_val, name, rating, clean])
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

# --- SIDEBAR: THE CHAGARIS BRAND ---
with st.sidebar:
    # 1. PROFILE PHOTO (HTML Base64 Injection)
    if os.path.exists("profile.jpg"):
        img_b64 = get_img_as_base64("profile.jpg")
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="data:image/jpg;base64,{img_b64}" 
                     style="border-radius: 50%; border: 3px solid #4338ca; width: 150px; height: 150px; object-fit: cover; display: block;">
            </div>
        """, unsafe_allow_html=True)
        
    # 2. CENTERED TEXT ELEMENTS
    st.markdown("""
        <div style="text-align: center;">
            <h1 style="color:#4338ca; margin:0; font-size: 2rem;">LAUREN CHAGARIS</h1>
            <p style="font-weight:700; color:#1e293b; margin: 5px 0;">AI Engineer & Data Scientist</p>
            <p style="font-size:0.85rem; color:#64748b; margin-bottom: 20px;">Focus: Sustainability & Optimization 🌿</p>
        </div>
    """, unsafe_allow_html=True)
    
    # 3. LINKS 
    c1, c2 = st.columns(2)
    with c1:
        st.link_button("LinkedIn", "https://www.linkedin.com/in/lchagaris", use_container_width=True)
    with c2:
        st.link_button("Portfolio", "https://www.laurendemidesign.com", use_container_width=True)
    
    st.divider()
    
# 4. PROOF OF PERFORMANCE 
    if os.path.exists("reviews_screenshot.png"):
        with st.expander("✅ Verified Platform Data", expanded=False):
            st.image("reviews_screenshot.png", use_container_width=True)
            # We use HTML to force the break <br> and center the text
            st.markdown("""
                <p style='text-align: center; font-size: 0.85rem; color: #64748b; margin-top: 5px; line-height: 1.4;'>
                    319 Total Ratings<br>
                    (Source: TaskRabbit)
                </p>
            """, unsafe_allow_html=True)
        st.divider()

    # 5. FILTERS
    st.markdown('<div style="text-align: left; width: 100%;">', unsafe_allow_html=True)
    selected_domains = st.multiselect("Domains", sorted(df['Domain'].unique()), default=sorted(df['Domain'].unique()))
    
    available_cats = sorted(df[df['Domain'].isin(selected_domains)]['Category'].unique())
    with st.expander("Filter Categories", expanded=False):
        selected_cats = [c for c in available_cats if st.checkbox(c, value=True, key=f"cb_{c}")]
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    st.download_button("📥 Download Reviews", df.to_csv(index=False).encode('utf-8'), "Lauren_Chagaris_Taskrabbit_Review_Performance_Audit.csv", use_container_width=True)

# --- MAIN DASHBOARD: THE VIBE CHECK ---
st.markdown("""
    <div style="background-color:#f8fafc; border-left: 5px solid #4338ca; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
        <h2 style="margin-top:0; color:#1e293b;">The Chagaris Vibe Check: Verified Operational Performance</h2>
        <p style="font-size:1.1rem; line-height:1.5; color:#475569;">
            This is not a simulation. This dashboard audits <strong>my verified operational history</strong>. 
            By quantifying <strong>561 real-world tasks</strong>, I provide transparent proof of reliability, 
            problem-solving, and the "vibe" I bring to every project: <strong>consistently 5-star</strong>.
        </p>
    </div>
    """, unsafe_allow_html=True)

t_audit, t_analytics = st.tabs(["📂 Audit Feed", "📈 Analytics & Insights"])

with t_audit:
    # Spotlight
    hall_of_fame = [
        {"text": "Lauren is smart, pleasant and tenacious. Great combo! Hire her!! Very pleased.", "author": "Scott S.", "cat": "Computer Help"},
        {"text": "Lauren was fantastic! She was on time, communicative, and did an amazing job.", "author": "Emily R.", "cat": "Moving Help"},
        {"text": "Absolute professional. Solved the problem quickly and explained everything clearly.", "author": "Michael B.", "cat": "Technical Support"}
    ]
    if 'idx' not in st.session_state: st.session_state.idx = 0

    c1, c2, c3 = st.columns([1, 12, 1])
    with c1:
        st.write("") 
        st.write("")
        if st.button("❮"): st.session_state.idx = (st.session_state.idx - 1) % len(hall_of_fame)
    with c3:
        st.write("")
        st.write("")
        if st.button("❯"): st.session_state.idx = (st.session_state.idx + 1) % len(hall_of_fame)
    
    item = hall_of_fame[st.session_state.idx]
    with c2:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%); color: white; padding: 28px; border-radius: 16px; margin: 0 0 35px 0;">
            <div style="font-size: 1.4rem; font-style: italic; font-weight: 500;">"{item['text']}"</div>
            <div style="margin-top: 12px; font-weight: 700;">— {item['author']} | {item['cat']}</div>
        </div>
        """, unsafe_allow_html=True)

    # 5-COLUMN METRICS
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Lifetime Tasks", "561") 
    m2.metric("Audit Sample", f"{len(df)}") 
    m3.metric("Composite Rating", "4.94") 
    m4.metric("5-Star Tasks", "310", delta="Top 1% Rank", delta_color="normal")
    m5.metric("Operational Risk", "Negligible", delta="- 0% Risk", delta_color="inverse")

    st.divider()
    
    search = st.text_input(f"🔍 Search {len(df)} verified records...", placeholder="Filter by keyword (e.g., 'punctual')...")
    filtered_df = df[(df['Domain'].isin(selected_domains)) & (df['Category'].isin(selected_cats))].sort_values('Date', ascending=False)
    if search: filtered_df = filtered_df[filtered_df['Review'].str.contains(search, case=False, na=False)]

    if not filtered_df.empty:
        st.write(f"**Showing {len(filtered_df)} verified records**")
        for _, row in filtered_df.iterrows():
            d_str = row['Date'].strftime('%B %d, %Y')
            stars = "★" * int(round(row['Rating']))
            rev = str(row['Review']).strip()
            
            clean_check = re.sub(r'[^\w\s]', '', rev.lower())
            if clean_check in ['nan', 'none', 'null', 'no text provided', 'no review', '']:
                rev_html = '<div class="no-review">No written review provided.</div>'
            else:
                rev_html = f'<div>"{rev}"</div>'

            st.markdown(f"""
                <div class="review-card">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="font-weight:700; font-size:1.1rem;">{row['Client Name']}</span>
                        <span style="color:#FBBF24; font-size:1.1rem;">{stars}</span>
                    </div>
                    <div style="font-size:0.9rem; color:#64748b; margin: 4px 0 12px 0;">📅 {d_str} • {row['Category']}</div>
                    {rev_html}
                </div>
            """, unsafe_allow_html=True)

with t_analytics:
    st.markdown("### 📊 Operational Insights")
    st.divider()
    
    # Growth Chart
    df_sorted = df.sort_values(by='Date')
    df_sorted['Cumulative Reviews'] = range(1, len(df_sorted) + 1)
    growth = alt.Chart(df_sorted).mark_area(
        line={'color':'#4338ca'}, 
        color=alt.Gradient(gradient='linear', stops=[alt.GradientStop(color='#4338ca', offset=0), alt.GradientStop(color='white', offset=1)], x1=1, x2=1, y1=1, y2=0)
    ).encode(
        x=alt.X('Date:T', title='Timeline'), 
        y=alt.Y('Cumulative Reviews:Q', title='Count')
    ).properties(height=350)
    st.altair_chart(growth, use_container_width=True)
    
    st.markdown("#### 🗣️ Sentiment DNA")
    # Ensure this line and the block below are perfectly indented (4 spaces/1 tab)
    text_corpus = " ".join(df['Review'].astype(str).tolist()).lower()
    
    targets = {
        "Execution Velocity": text_corpus.count("fast") + text_corpus.count("quick") + text_corpus.count("speed") + text_corpus.count("prompt"),
        "Interpersonal Vibe (Calm/Nice)": text_corpus.count("calm") + text_corpus.count("nice") + text_corpus.count("kind") + text_corpus.count("pleasant") + text_corpus.count("patient"),
        "Quality & Aesthetics": text_corpus.count("beautiful") + text_corpus.count("amazing") + text_corpus.count("perfect") + text_corpus.count("neat") + text_corpus.count("thorough"),
        "Problem Solving": text_corpus.count("helpful") + text_corpus.count("solved") + text_corpus.count("fixed") + text_corpus.count("smart"),
        "Operational Efficiency": text_corpus.count("efficient") + text_corpus.count("organized") + text_corpus.count("reliable")
    }
    
    nlp_df = pd.DataFrame(list(targets.items()), columns=['Trait', 'Mentions'])
    nlp_chart = alt.Chart(nlp_df).mark_bar(color='#4338ca', cornerRadiusEnd=4).encode(
        x=alt.X('Mentions:Q', title='Frequency of Mentions'), 
        y=alt.Y('Trait:N', sort='-x', title='')
    ).properties(height=350)
    
    st.altair_chart(nlp_chart, use_container_width=True)
