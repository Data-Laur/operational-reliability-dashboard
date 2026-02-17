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

    :root { --primary-color: #4338ca; --text-color: #1e293b; }

    /* Tag & Checkbox Indigo Brand Fixes */
    span[data-baseweb="tag"] { background-color: #e0e7ff !important; border: 1px solid #4338ca !important; }
    span[data-baseweb="tag"] span { color: #4338ca !important; font-weight: 600 !important; }
    span[data-baseweb="tag"] svg { fill: #4338ca !important; }
    div[data-testid="stCheckbox"] label span[aria-checked="true"] { background-color: #4338ca !important; border-color: #4338ca !important; }

    /* UI Tweaks */
    button[data-testid="stSidebarCollapsedControl"] { color: #4338ca !important; border: 2px solid #4338ca !important; border-radius: 8px !important; }
    button[data-testid="stSidebarCollapsedControl"] svg { fill: #4338ca !important; }
    
    /* Domain Tag Box Fix */
    .stMultiSelect div[data-baseweb="select"] > div { max-height: none !important; white-space: normal !important; }
    
    /* Metric Font Fix */
    div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetricValue"] { font-size: 1.8rem !important; }

    /* Tab Styling */
    button[data-baseweb="tab"] { font-size: 20px !important; font-weight: 700 !important; color: #64748b !important; }
    button[data-baseweb="tab"][aria-selected="true"] { color: #4338ca !important; border-bottom-color: #4338ca !important; }
    div[data-baseweb="tab-list"] { padding: 15px 0; border-bottom: 2px solid #f1f5f9; }

    .review-card { background-color: #ffffff; padding: 24px; border-radius: 16px; border: 1px solid #e2e8f0; margin-bottom: 20px; text-align: left; }
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
            for line in f.readlines()[1:]:
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
    
    # RESTORED: Detailed Domain Logic
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

# --- SIDEBAR ---
with st.sidebar:
    if os.path.exists("profile.jpg"):
        img_b64 = get_img_as_base64("profile.jpg")
        st.markdown(f'<div style="display: flex; justify-content: center; margin-bottom: 20px;"><img src="data:image/jpg;base64,{img_b64}" style="border-radius: 50%; border: 3px solid #4338ca; width: 150px; height: 150px; object-fit: cover; display: block;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center;"><h1 style="color:#4338ca; margin:0; font-size: 2rem;">LAUREN CHAGARIS</h1><p style="font-weight:700; color:#1e293b; margin: 5px 0;">AI Engineer & Data Scientist</p><p style="font-size:0.85rem; color:#64748b; margin-bottom: 20px;">Focus: Sustainability & Optimization 🌿</p></div>', unsafe_allow_html=True)
    
    c1, c2 = st.columns(2)
    with c1: st.link_button("LinkedIn", "https://www.linkedin.com/in/laurenchagaris", use_container_width=True)
    with c2: st.link_button("Portfolio", "https://www.uxfol.io/p/laurenchagaris", use_container_width=True)
    
    st.divider()
    if os.path.exists("reviews_screenshot.png"):
        with st.expander("✅ Verified Platform Data", expanded=False):
            st.image("reviews_screenshot.png", use_container_width=True)
            st.markdown("<p style='text-align: center; font-size: 0.85rem; color: #64748b; margin-top: 5px; line-height: 1.4;'>319 Total Ratings<br>(Source: TaskRabbit)</p>", unsafe_allow_html=True)
    
    st.divider()
    
    # RESTORED: Filters & Tags
    st.markdown('<div style="text-align: left; width: 100%;">', unsafe_allow_html=True)
    selected_domains = st.multiselect("Domains", sorted(df['Domain'].unique()), default=sorted(df['Domain'].unique()))
    
    available_cats = sorted(df[df['Domain'].isin(selected_domains)]['Category'].unique())
    with st.expander("Filter Categories", expanded=False):
        selected_cats = [c for c in available_cats if st.checkbox(c, value=True, key=f"cb_{c}")]
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    st.download_button("📥 Download Reviews", df.to_csv(index=False).encode('utf-8'), "Lauren_Chagaris_Audit.csv", use_container_width=True)

# --- MAIN ---
st.markdown('<div style="background-color:#f8fafc; border-left: 5px solid #4338ca; padding: 20px; border-radius: 8px; margin-bottom: 25px;"><h2 style="margin-top:0; color:#1e293b;">The Chagaris Vibe Check</h2><p style="font-size:1.1rem; line-height:1.5; color:#475569;">This dashboard audits <strong>561 real-world tasks</strong> to provide empirical proof of reliability and problem-solving.</p></div>', unsafe_allow_html=True)

t_audit, t_analytics = st.tabs(["📂 Audit Feed", "📈 Analytics & Insights"])

with t_audit:
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Lifetime Tasks", "561")
    m2.metric("Audit Sample", f"{len(df)}")
    m3.metric("Composite Rating", "4.94")
    # RESTORED: Top 1% Delta
    m4.metric("5-Star Tasks", "310", delta="Top 1% Rank", delta_color="normal")
    m5.metric("Operational Risk", "Negligible", delta="- 0% Risk", delta_color="inverse")
    st.divider()
    
    search = st.text_input("🔍 Search verified records...", placeholder="Filter by keyword...")
    filtered_df = df[(df['Domain'].isin(selected_domains)) & (df['Category'].isin(selected_cats))].sort_values('Date', ascending=False)
    
    if search: filtered_df = filtered_df[filtered_df['Review'].str.contains(search, case=False, na=False)]
    for _, row in filtered_df.head(10).iterrows():
        st.markdown(f'<div class="review-card"><strong>{row["Client Name"]}</strong> <span style="color:#FBBF24;">{"★"*int(row["Rating"])}</span><br><small>{row["Date"].strftime("%B %d, %Y")} • {row["Category"]}</small><br>"{row["Review"]}"</div>', unsafe_allow_html=True)

with t_analytics:
    st.markdown("### 📊 Operational Insights")
    st.divider()
    
    # Text Analysis Prep
    text_corpus = " ".join(df['Review'].astype(str).tolist()).lower()

    # 1. GROWTH TIMELINE
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

    # 2. THE DUAL DNA ANALYSIS
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### 🧠 Operational Pillars")
        st.caption("Strategic grouping of synonyms for high-level trait mapping.")
        
        # RESTORED: "Efficient" added to Execution Velocity
        pillars = {
            "Execution Velocity": text_corpus.count("fast") + text_corpus.count("quick") + text_corpus.count("speed") + text_corpus.count("efficient") + text_corpus.count("efficiency"),
            "Composure (Calm/Easy)": text_corpus.count("calm") + text_corpus.count("easy") + text_corpus.count("patient") + text_corpus.count("stress-free"),
            "Communication Clarity": text_corpus.count("communicat") + text_corpus.count("talk") + text_corpus.count("conversation"),
            "Interpersonal IQ": text_corpus.count("nice") + text_corpus.count("friendly") + text_corpus.count("kind"),
            "High-Stakes Quality": text_corpus.count("beautiful") + text_corpus.count("perfect") + text_corpus.count("fantastic") + text_corpus.count("wonderful")
        }
        pillar_df = pd.DataFrame(list(pillars.items()), columns=['Pillar', 'Mentions'])
        pillar_chart = alt.Chart(pillar_df).mark_bar(color='#4338ca').encode(x='Mentions:Q', y=alt.Y('Pillar:N', sort='-x', title='')).properties(height=350).configure_axis(labelLimit=300)
        st.altair_chart(pillar_chart, use_container_width=True)

    with c2:
        st.markdown("#### 🗣️ Raw Keyword Frequency")
        st.caption("Direct 'Word of Mouth' terminology extracted from records.")
        raw_words = {
            "Great": text_corpus.count("great"),
            "Easy": text_corpus.count("easy"),
            "Friendly": text_corpus.count("friendly"),
            "Quick/Fast": text_corpus.count("quick") + text_corpus.count("fast"),
            "Communication": text_corpus.count("communicat"),
            "Beautiful": text_corpus.count("beautiful"),
            "Wonderful": text_corpus.count("wonderful"),
            "Efficient": text_corpus.count("efficient")
        }
        raw_df = pd.DataFrame(list(raw_words.items()), columns=['Keyword', 'Count'])
        raw_chart = alt.Chart(raw_df).mark_bar(color='#6366f1').encode(x='Count:Q', y=alt.Y('Keyword:N', sort='-x', title='')).properties(height=350).configure_axis(labelLimit=300)
        st.altair_chart(raw_chart, use_container_width=True)
