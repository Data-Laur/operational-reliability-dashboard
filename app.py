import streamlit as st
import pandas as pd
import altair as alt
import os
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Lauren | Operational Audit", 
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THE BRAND & ACCESSIBILITY ENGINE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Figtree', sans-serif;
        color: #1e293b;
    }

    /* --- SIDEBAR & NAVIGATION FIXES --- */
    /* 1. Unhide the header so mobile users see the hamburger menu */
    header { visibility: visible !important; background-color: transparent !important; }
    
    /* 2. Make the 'Open Menu' arrow/hamburger HIGH CONTRAST INDIGO */
    [data-testid="stSidebarCollapsedControl"] {
        color: #4338ca !important;
        font-weight: 700 !important;
    }
    
    /* 3. Hide the 'Manage App' default clutter, but keep the nav button */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* --- PROFILE PICTURE (CIRCLE, NO BLUR) --- */
    [data-testid="stSidebar"] img {
        border-radius: 50%;
        border: 3px solid #4338ca; /* Indigo Brand Border */
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        display: block;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 15px;
    }

    /* --- TABS & WIDGETS --- */
    div[data-baseweb="tab-list"] {
        position: sticky; top: 0; z-index: 999; background-color: white; padding: 10px 0; border-bottom: 1px solid #f1f5f9;
    }
    button[data-baseweb="tab"] { font-size: 16pt !important; font-weight: 700 !important; color: #475569 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #4338ca !important; border-bottom-color: #4338ca !important; }
    div[data-baseweb="checkbox"] div:first-child { background-color: #4338ca !important; border-color: #4338ca !important; }
    div[data-baseweb="checkbox"] svg { fill: white !important; }

    /* --- CARDS & LAYOUT --- */
    .context-header {
        background-color: #f8fafc; border-left: 5px solid #4338ca; padding: 20px; border-radius: 8px; margin-bottom: 25px;
    }
    .spotlight-card {
        background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%); color: white; padding: 28px; border-radius: 16px; margin: 15px 0 35px 0;
    }
    .review-card { background-color: #ffffff; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 20px; }
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
    
    # --- FILTERING OUT 'HELP MOVING' ---
    # This happens BEFORE we count the rows, so 'len(df)' will be accurate (190)
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

# --- SIDEBAR: PROFILE & FILTERS ---
with st.sidebar:
    # 1. PROFILE PICTURE (Must match filename in repo)
    # The CSS above will automatically make this circular
    if os.path.exists("profile.jpg"):
        st.image("profile.jpg", width=120)
    
    st.markdown("<h1 style='color:#4338ca; margin:10px 0 0 0; text-align:center;'>LAUREN</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-weight:600; color:#64748b; text-align:center;'>Operations & Analytics</p>", unsafe_allow_html=True)
    st.divider()

    selected_domains = st.multiselect("Domains", sorted(df['Domain'].unique()), default=sorted(df['Domain'].unique()))
    
    st.write("**Categories**")
    available_cats = sorted(df[df['Domain'].isin(selected_domains)]['Category'].unique())
    selected_cats = [c for c in available_cats if st.checkbox(c, value=True, key=f"cb_{c}")]

    st.divider()
    st.download_button("📥 Download Reviews", df.to_csv(index=False).encode('utf-8'), "Lauren_Performance_Audit.csv")

# --- CONTEXT HEADER ---
st.markdown("""
    <div class="context-header">
        <h2 style="margin-top:0; color:#1e293b;">Project Overview: Operational Performance Audit</h2>
        <p style="font-size:1.1rem; line-height:1.5; color:#475569;">
            This application is a <strong>longitudinal performance study</strong> analyzing verified professional tasks. 
            By quantifying seven years of client feedback, this audit proves a scalable track record of operational excellence and reliability.
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- MAIN DASHBOARD ---
t_audit, t_analytics = st.tabs(["📂 Audit Feed", "📈 Analytics & Insights"])

with t_audit:
    # SPOTLIGHT
    hall_of_fame = [
        {"text": "Lauren is smart, pleasant and tenacious. Great combo! Hire her!! Very pleased.", "author": "Scott S.", "cat": "Computer Help"},
        {"text": "Lauren was fantastic! She was on time, communicative, and did an amazing job.", "author": "Emily R.", "cat": "Moving Help"},
        {"text": "Absolute professional. Solved the problem quickly and explained everything clearly.", "author": "Michael B.", "cat": "Technical Support"}
    ]
    if 'idx' not in st.session_state: st.session_state.idx = 0

    c_left, c_main, c_right = st.columns([1, 12, 1])
    with c_left:
        st.markdown("<div style='height:85px;'></div>", unsafe_allow_html=True)
        if st.button("❮", aria_label="Previous"): st.session_state.idx = (st.session_state.idx - 1) % len(hall_of_fame)
    with c_right:
        st.markdown("<div style='height:85px;'></div>", unsafe_allow_html=True)
        if st.button("❯", aria_label="Next"): st.session_state.idx = (st.session_state.idx + 1) % len(hall_of_fame)
    
    item = hall_of_fame[st.session_state.idx]
    with c_main:
        st.markdown(f"""
        <div class="spotlight-card">
            <div style="font-size: 1.4rem; font-style: italic; font-weight: 500;">"{item['text']}"</div>
            <div style="margin-top: 12px; font-weight: 700;">— {item['author']} | {item['cat']}</div>
        </div>
        """, unsafe_allow_html=True)

    # METRICS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Lifetime Tasks", "561")
    # 2. DYNAMIC METRIC FIX (No hardcoding)
    m2.metric("Audit Sample", f"{len(df)}") 
    m3.metric("Composite Rating", f"{df['Rating'].mean():.2f}")
    m4.metric("Operational Risk", "Negligible", delta="- 0% Risk", delta_color="inverse")

    st.divider()
    
    # 3. DYNAMIC SEARCH PLACEHOLDER FIX
    search = st.text_input(
        f"🔍 Search {len(df)} verified records...", 
        placeholder="Filter by keyword (e.g., 'fast', 'punctual')..."
    )

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
                        <span style="color:#f59e0b; font-size:1.1rem;">{stars}</span>
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
    
    # Sentiment
    st.markdown("#### 🗣️ Sentiment DNA")
    text = " ".join(df['Review'].astype(str).tolist()).lower()
    targets = {"Fast": text.count("fast"), "Efficient": text.count("efficient"), "Professional": text.count("professional"), "Kind": text.count("kind"), "Helpful": text.count("helpful")}
    nlp_df = pd.DataFrame(list(targets.items()), columns=['Trait', 'Mentions'])
    nlp_chart = alt.Chart(nlp_df).mark_bar(color='#4338ca').encode(x=alt.X('Mentions:Q'), y=alt.Y('Trait:N', sort='-x')).properties(height=350)
    st.altair_chart(nlp_chart, use_container_width=True)
