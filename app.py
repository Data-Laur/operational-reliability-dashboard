import streamlit as st
import pandas as pd
import altair as alt
import os
import re

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Chagaris | Vibe Check", 
    page_icon="✨", # Sparkles for the 'Vibe' aesthetic
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- THE BRAND & UI ENGINE (CSS) ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Figtree', sans-serif;
        color: #1e293b;
    }

    /* --- NUCLEAR SIDEBAR FIX --- */
    [data-testid="stSidebarCollapsedControl"] {
        color: #4338ca !important;
        background-color: #f1f5f9 !important;
        border: 2px solid #4338ca !important;
        border-radius: 8px !important;
        padding: 5px !important;
    }
    
    [data-testid="stSidebarCollapsedControl"] svg {
        fill: #4338ca !important;
        stroke: #4338ca !important;
    }

    /* --- IMAGE CLARITY & CIRCLE FIX --- */
    [data-testid="stSidebar"] img {
        border-radius: 50%;
        border: 3px solid #4338ca;
        image-rendering: -webkit-optimize-contrast; 
        display: block;
        margin-left: auto;
        margin-right: auto;
        margin-bottom: 15px;
    }

    /* Tabs & Widgets Branding */
    div[data-baseweb="tab-list"] { padding: 10px 0; border-bottom: 1px solid #f1f5f9; }
    button[data-baseweb="tab"] { font-size: 16pt !important; font-weight: 700 !important; color: #475569 !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #4338ca !important; border-bottom-color: #4338ca !important; }
    div[data-baseweb="checkbox"] div:first-child { background-color: #4338ca !important; border-color: #4338ca !important; }

    /* Review Cards Styling */
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
    if os.path.exists("profile.jpg"):
        st.image("profile.jpg", width=120)
        
    st.markdown("<h1 style='color:#4338ca; margin:10px 0 0 0; text-align:center;'>LAUREN CHAGARIS</h1>", unsafe_allow_html=True)
    
    # CONFIDENT TITLES
    st.markdown("<p style='font-weight:700; color:#1e293b; text-align:center; margin-bottom:5px;'>AI Engineer & Data Scientist</p>", unsafe_allow_html=True)
    
    # SUSTAINABILITY TAG
    st.caption("Focus: Sustainability & Optimization 🌿")
    
    # CTA BUTTON
    st.link_button("🚀 Hire Me / LinkedIn", "https://www.linkedin.com/in/YOUR_LINKEDIN_HERE", use_container_width=True)
    
    st.divider()
    
    # PROOF OF PERFORMANCE
    if os.path.exists("reviews_screenshot.png"):
        with st.expander("✅ Verified Platform Data"):
            st.image("reviews_screenshot.png", caption="319 Total Ratings (Source: TaskRabbit)", use_container_width=True)
        st.divider()

    selected_domains = st.multiselect("Domains", sorted(df['Domain'].unique()), default=sorted(df['Domain'].unique()))
    available_cats = sorted(df[df['Domain'].isin(selected_domains)]['Category'].unique())
    selected_cats = [c for c in available_cats if st.checkbox(c, value=True, key=f"cb_{c}")]
    st.divider()
    st.download_button("📥 Download Reviews", df.to_csv(index=False).encode('utf-8'), "Lauren_Chagaris_Audit.csv")

# --- MAIN DASHBOARD: THE VIBE CHECK ---

# "VIBE CHECK" HEADER
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
                        <span style="color:#f59e0b; font-size:1.1rem;">{stars}</span>
                    </div>
                    <div style="font-size:0.9rem; color:#64748b; margin: 4px 0 12px 0;">📅 {d_str} • {row['Category']}</div>
                    {rev_html}
                </div>
            """, unsafe_allow_html=True)

with t_analytics:
    st.markdown("### 📊 Operational Insights")
    st.divider()
    
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
    text = " ".join(df['Review'].astype(str).tolist()).lower()
    targets = {"Fast": text.count("fast"), "Efficient": text.count("efficient"), "Professional": text.count("professional"), "Kind": text.count("kind"), "Helpful": text.count("helpful")}
    nlp_df = pd.DataFrame(list(targets.items()), columns=['Trait', 'Mentions'])
    nlp_chart = alt.Chart(nlp_df).mark_bar(color='#4338ca').encode(x=alt.X('Mentions:Q'), y=alt.Y('Trait:N', sort='-x')).properties(height=350)
    st.altair_chart(nlp_chart, use_container_width=True)
