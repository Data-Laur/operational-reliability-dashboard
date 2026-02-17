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
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

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
        background-color: #e0e7ff !important;
        border: 1px solid #4338ca !important;
    }
    span[data-baseweb="tag"] span {
        color: #4338ca !important; 
        font-weight: 600 !important;
    }
    span[data-baseweb="tag"] svg {
        fill: #4338ca !important;
    }

    /* --- NUCLEAR CHECKBOX FIX (Kills the Orange Check) --- */
    div[data-testid="stCheckbox"] label span[aria-checked="true"] {
        background-color: #4338ca !important;
        border-color: #4338ca !important;
    }
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
    div[data-baseweb="tab-list"] { 
        padding: 15px 0; 
        border-bottom: 2px solid #f1f5f9; 
    }

    /* --- CAROUSEL STYLING --- */
    .carousel-card {
        background: linear-gradient(135deg, #4338ca 0%, #6366f1 100%);
        color: white;
        padding: 28px;
        border-radius: 16px;
        margin: 0 0 35px 0;
    }
    .carousel-label {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        margin-bottom: 10px;
        opacity: 0.9;
    }
    .carousel-quote {
        font-size: 1.4rem;
        font-style: italic;
        font-weight: 500;
    }
    .carousel-author {
        margin-top: 12px;
        font-weight: 700;
    }

    /* --- REVIEW CARDS --- */
    .review-card {
        background-color: #ffffff;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        margin-bottom: 20px;
        text-align: left;
    }
    .no-review {
        color: #64748b;
        font-style: italic;
        font-size: 14px;
    }

    /* --- DOWNLOAD BUTTON BRAND COLOR --- */
    div[data-testid="stDownloadButton"] button {
        background-color: #4338ca !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        background-color: #3730a3 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- DATA LOADING ---
@st.cache_data
def load_data():
    # Priority 1: Real data (local / private)
    real_files = ['taskrabbit_master_clean.csv', 'taskrabbit_reviews.csv']
    file_path = None
    for f in real_files:
        if os.path.exists(f):
            file_path = f
            break
    
    if file_path:
        # Regex parser for the messy CSV
        parsed_data = []
        pattern = re.compile(r'^(.+?),(\d{4}-\d{2}-\d{2}),(.+?),(\d\.\d),(.*)$')
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as fh:
                for line in fh.readlines()[1:]:
                    match = pattern.match(line.strip())
                    if match:
                        cat, d_val, name, rating, raw = match.groups()
                        clean = re.sub(r',"?\s*\d+\.\d+.*$', '', raw).strip('"').strip("'").replace('""', '"')
                        parsed_data.append([cat.replace('"', '').strip(), d_val, name, rating, clean])
            df = pd.DataFrame(parsed_data, columns=['Category', 'Date', 'Client Name', 'Rating', 'Review'])
        except:
            return pd.DataFrame(), False
        return _process_df(df), True
    
    # Priority 2: Demo data (Streamlit Cloud / public)
    data = {
        'Category': [
            'Packing & Unpacking', 'Event Staffing', 'Organization', 
            'Technical Support', 'Moving Help', 'Computer Help',
            'Personal Assistant', 'Photography', 'Arts / Crafts',
            'Errands', 'Furniture Assembly', 'Office Administration',
            'Packing & Unpacking', 'Event Staffing', 'Organization'
        ],
        'Date': [
            '2025-12-06', '2025-11-20', '2025-10-15', '2025-09-10', '2025-08-05',
            '2025-07-22', '2025-06-18', '2025-05-30', '2025-04-12', '2025-03-08',
            '2025-02-14', '2025-01-20', '2024-12-15', '2024-11-10', '2024-10-05'
        ],
        'Client Name': [
            'Pat B.', 'Kara Keating B.', 'Holly H.', 'Jeffrey G.', 'Miriam O.',
            'Scott S.', 'Emily R.', 'Michael B.', 'Sarah T.', 'James K.',
            'Lisa M.', 'David W.', 'Rachel P.', 'Chris A.', 'Amanda F.'
        ],
        'Rating': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 4.9],
        'Review': [
            "Lauren is very professional and does a great job. I highly recommend!",
            "Saved the day with a prompt gift wrapping job. Followed all instructions!",
            "Lauren is lovely to work with. Excellent communication and great attention to detail.",
            "Lauren was great. Great communication went over and out of her way to help when needed. Can't recommend her enough.",
            "Absolute professional. Solved the problem quickly and explained everything clearly.",
            "Lauren is smart, pleasant and tenacious. Great combo! Hire her!! Very pleased.",
            "Lauren was fantastic! She was on time, communicative, and did an amazing job.",
            "Very thorough and careful. Went above and beyond what was asked.",
            "Quick, efficient, and friendly. Made the whole process easy and stress-free.",
            "Great experience! Lauren was punctual and very detail-oriented.",
            "Wonderful job assembling everything. Very patient and meticulous.",
            "Lauren kept everything organized and on track. Highly efficient.",
            "Very easy and friendly. Highly recommended for any task.",
            "Lauren went above and beyond. Fast execution and great communication.",
            "Lauren is very sweet and nice. She can absolutely be left alone to do a job on her own."
        ]
    }
    df = pd.DataFrame(data)
    return _process_df(df), False

def _process_df(df):
    df = df[~df['Category'].str.contains('Help Moving', case=False, na=False)]
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    
    def map_domains(category):
        cat = str(category).lower()
        if 'computer' in cat or 'technical' in cat:
            return 'Technical Support'
        elif any(x in cat for x in ['packing', 'moving', 'organization']):
            return 'Logistics'
        elif 'assistant' in cat or 'staffing' in cat:
            return 'Operations'
        elif 'photo' in cat:
            return 'Visual Media'
        return 'General Ops'
    
    df['Domain'] = df['Category'].apply(map_domains)
    return df

df, is_real_data = load_data()


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    # 1. PROFILE PHOTO
    img_b64 = get_img_as_base64("profile.jpg")
    if img_b64:
        st.markdown(f"""
            <div style="display: flex; justify-content: center; margin-bottom: 20px;">
                <img src="data:image/jpg;base64,{img_b64}" 
                     style="border-radius: 50%; border: 3px solid #4338ca; width: 150px; height: 150px; object-fit: cover; display: block;">
            </div>
        """, unsafe_allow_html=True)
        
    # 2. NAME & TITLE
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
        st.link_button("LinkedIn", "https://www.linkedin.com/in/laurenchagaris", use_container_width=True)
    with c2:
        st.link_button("Portfolio", "https://www.uxfol.io/p/laurenchagaris", use_container_width=True)
    
    st.divider()
    
    # 4. VERIFIED PLATFORM DATA PROOF
    if os.path.exists("reviews_screenshot.png"):
        with st.expander("✅ Verified Platform Data", expanded=False):
            st.image("reviews_screenshot.png", use_column_width=True)
            st.markdown("""
                <p style='text-align: center; font-size: 0.85rem; color: #64748b; margin-top: 5px; line-height: 1.4;'>
                    319 Total Ratings<br>
                    (Source: TaskRabbit)
                </p>
            """, unsafe_allow_html=True)
        st.divider()

    # 5. FILTERS
    st.markdown('<div style="text-align: left; width: 100%;">', unsafe_allow_html=True)
    if not df.empty:
        selected_domains = st.multiselect(
            "Domains", 
            sorted(df['Domain'].unique()), 
            default=sorted(df['Domain'].unique())
        )
        available_cats = sorted(df[df['Domain'].isin(selected_domains)]['Category'].unique())
        with st.expander("Filter Categories", expanded=False):
            selected_cats = [c for c in available_cats if st.checkbox(c, value=True, key=f"cb_{c}")]
    else:
        selected_domains = []
        selected_cats = []
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 6. DOWNLOAD / PRIVACY NOTICE
    if not df.empty and is_real_data:
        st.download_button(
            "📥 Download Reviews", 
            df.to_csv(index=False).encode('utf-8'), 
            "Lauren_Chagaris_Audit.csv", 
            use_container_width=True
        )
    elif not df.empty:
        st.caption("🔒 *Real dataset hidden for privacy. Showing demo data.*")


# ============================================================
# MAIN DASHBOARD
# ============================================================

# --- HEADER: THE VIBE CHECK ---
st.markdown("""
    <div style="background-color:#f8fafc; border-left: 5px solid #4338ca; padding: 20px; border-radius: 8px; margin-bottom: 25px;">
        <h2 style="margin-top:0; color:#1e293b;">The Chagaris Vibe Check</h2>
        <p style="font-size:1.1rem; line-height:1.5; color:#475569;">
            This dashboard audits <strong>7 years of verified tasks</strong> to provide empirical proof of reliability and problem-solving.
        </p>
    </div>
    """, unsafe_allow_html=True)

if df.empty:
    st.warning("⚠️ No data loaded.")
else:
    t_audit, t_analytics = st.tabs(["📂 Audit Feed", "📈 Analytics & Insights"])

    with t_audit:
        # ============================
        # TESTIMONIAL CAROUSEL
        # ============================
        hall_of_fame = [
            {"text": "Absolute professional. Solved the problem quickly and explained everything clearly.", "author": "Michael B.", "cat": "Technical Support"},
            {"text": "Lauren is smart, pleasant and tenacious. Great combo! Hire her!! Very pleased.", "author": "Scott S.", "cat": "Computer Help"},
            {"text": "Lauren was fantastic! She was on time, communicative, and did an amazing job.", "author": "Emily R.", "cat": "Moving Help"},
        ]
        if 'idx' not in st.session_state:
            st.session_state.idx = 0

        c_left, c_center, c_right = st.columns([1, 12, 1])
        with c_left:
            st.write("")
            st.write("")
            if st.button("❮"):
                st.session_state.idx = (st.session_state.idx - 1) % len(hall_of_fame)
        with c_right:
            st.write("")
            st.write("")
            if st.button("❯"):
                st.session_state.idx = (st.session_state.idx + 1) % len(hall_of_fame)
        
        item = hall_of_fame[st.session_state.idx]
        with c_center:
            st.markdown(f"""
            <div class="carousel-card">
                <div class="carousel-label">⭐ HIGH-IMPACT TESTIMONIAL</div>
                <div class="carousel-quote">"{item['text']}"</div>
                <div class="carousel-author">— {item['author']} | {item['cat']}</div>
            </div>
            """, unsafe_allow_html=True)

        # ============================
        # METRICS ROW
        # ============================
        m1, m2, m3, m4, m5 = st.columns(5)
        m1.metric("Lifetime Tasks", "561")
        
        if is_real_data:
            m2.metric("Verified Sample", f"{len(df)}")
        else:
            m2.metric("Verified Sample", "190")
        
        m3.metric("Composite Rating", "4.94")
        m4.metric("5-Star Tasks", "310", delta="Top 1% Rank", delta_color="normal")
        m5.metric("Operational Risk", "Negligible", delta="- 0% Risk", delta_color="inverse")

        st.divider()
        
        # ============================
        # SEARCH & REVIEW FEED
        # ============================
        display_count = len(df) if is_real_data else 191
        search = st.text_input(
            f"🔍 Search {display_count} verified records...", 
            placeholder="Filter by keyword..."
        )
        
        filtered_df = df[
            (df['Domain'].isin(selected_domains)) & 
            (df['Category'].isin(selected_cats))
        ].sort_values('Date', ascending=False)
        
        if search:
            filtered_df = filtered_df[
                filtered_df['Review'].str.contains(search, case=False, na=False)
            ]

        if not filtered_df.empty:
            st.write(f"**Showing {len(filtered_df)} verified records**")
            for _, row in filtered_df.iterrows():
                d_str = row['Date'].strftime('%B %d, %Y')
                stars = "★" * int(round(row['Rating']))
                rev = str(row['Review']).strip()
                
                # Clean check for empty reviews
                clean_check = re.sub(r'[^\w\s]', '', rev.lower())
                if clean_check in ['nan', 'none', 'null', 'no text provided', 'no review', '']:
                    rev_html = '<div class="no-review">No written review provided.</div>'
                else:
                    rev_html = f'<div>"{rev}"</div>'

                st.markdown(f"""
                    <div class="review-card">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <span style="font-size: 0.75rem; font-weight: 600; color: #64748b; text-transform: uppercase; letter-spacing: 0.5px;">{row['Domain']}</span>
                            </div>
                            <span style="color:#FBBF24; font-size:1.1rem;">{stars}</span>
                        </div>
                        <div style="font-weight:700; font-size:1.1rem; margin: 4px 0 2px 0;">{row['Client Name']}</div>
                        <div style="font-size:0.9rem; color:#64748b; margin: 0 0 12px 0;">📅 {d_str} • {row['Category']}</div>
                        {rev_html}
                    </div>
                """, unsafe_allow_html=True)

    # ============================
    # ANALYTICS TAB
    # ============================
    with t_analytics:
        st.markdown("### 📊 Operational Insights")
        st.divider()
        
        text_corpus = " ".join(df['Review'].astype(str).tolist()).lower()

        # 1. GROWTH TIMELINE
        df_sorted = df.sort_values(by='Date')
        df_sorted['Cumulative Reviews'] = range(1, len(df_sorted) + 1)
        growth = alt.Chart(df_sorted).mark_area(
            line={'color':'#4338ca'}, 
            color=alt.Gradient(
                gradient='linear', 
                stops=[
                    alt.GradientStop(color='#4338ca', offset=0), 
                    alt.GradientStop(color='white', offset=1)
                ], 
                x1=1, x2=1, y1=1, y2=0
            )
        ).encode(
            x=alt.X('Date:T', title='Timeline'), 
            y=alt.Y('Cumulative Reviews:Q', title='Review Velocity')
        ).properties(height=300)
        st.altair_chart(growth, use_container_width=True)
        
        st.divider()

        # 2. DUAL DNA ANALYSIS
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🧠 Operational Pillars")
            st.caption("Strategic grouping of synonyms for high-level trait mapping.")
            
            pillars = {
                "Execution Velocity": text_corpus.count("fast") + text_corpus.count("quick") + text_corpus.count("speed") + text_corpus.count("efficient") + text_corpus.count("efficiency"),
                "Composure (Calm/Easy)": text_corpus.count("calm") + text_corpus.count("easy") + text_corpus.count("patient") + text_corpus.count("stress-free"),
                "Communication Clarity": text_corpus.count("communicat") + text_corpus.count("talk") + text_corpus.count("conversation"),
                "Interpersonal IQ": text_corpus.count("nice") + text_corpus.count("friendly") + text_corpus.count("kind"),
                "High-Stakes Quality": text_corpus.count("beautiful") + text_corpus.count("perfect") + text_corpus.count("fantastic") + text_corpus.count("wonderful")
            }
            pillar_df = pd.DataFrame(list(pillars.items()), columns=['Pillar', 'Mentions'])
            pillar_chart = alt.Chart(pillar_df).mark_bar(color='#4338ca').encode(
                x='Mentions:Q', 
                y=alt.Y('Pillar:N', sort='-x', title='')
            ).properties(height=350).configure_axis(labelLimit=300)
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
            raw_chart = alt.Chart(raw_df).mark_bar(color='#6366f1').encode(
                x='Count:Q', 
                y=alt.Y('Keyword:N', sort='-x', title='')
            ).properties(height=350).configure_axis(labelLimit=300)
            st.altair_chart(raw_chart, use_container_width=True)