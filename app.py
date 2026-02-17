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

    /* --- RISK METRIC: Force green color and hide default arrow --- */
    div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetricDelta"] {
        color: #16a34a !important;
    }
    div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetricDelta"] svg {
        display: none !important;
    }

    /* --- TAB FONT SIZE FIX (Larger for recruiter visibility) --- */
    button[data-baseweb="tab"] { 
        font-size: 26px !important; 
        font-weight: 700 !important; 
        color: #64748b !important; 
        padding: 12px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] { 
        color: #4338ca !important; 
        border-bottom-color: #4338ca !important; 
    }
    div[data-baseweb="tab-list"] { 
        padding: 15px 0; 
        border-bottom: 3px solid #f1f5f9; 
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

    /* --- STREAK CALLOUT --- */
    .streak-callout {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #86efac;
        border-radius: 12px;
        padding: 16px 24px;
        text-align: center;
        margin-bottom: 20px;
    }
    .streak-number {
        font-size: 2.5rem;
        font-weight: 700;
        color: #16a34a;
        line-height: 1;
    }
    .streak-label {
        font-size: 0.95rem;
        color: #475569;
        margin-top: 4px;
    }

    /* --- SIDEBAR: Tighten spacing --- */
    section[data-testid="stSidebar"] hr {
        margin-top: 0.5rem !important;
        margin-bottom: 0.5rem !important;
    }
    section[data-testid="stSidebar"] .stExpander {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }
    section[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] > div {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


# --- DATA LOADING ---
@st.cache_data
def load_data():
    file_path = 'taskrabbit_reviews_clean.csv'
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
    else:
        # Fallback demo data if CSV not found
        data = {
            'Category': [
                'Arts / Crafts', 'Errands', 'Arts / Crafts', 'Arts / Crafts', 'Computer Help',
                'Errands', 'Event Staffing', 'Arts / Crafts', 'Packing & Unpacking', 'Computer Help',
                'Event Staffing', 'Event Staffing', 'Photography', 'Computer Help', 'Packing & Unpacking',
            ],
            'Date': [
                '2025-12-23', '2025-12-21', '2025-12-21', '2025-12-20', '2025-12-19',
                '2025-12-14', '2025-12-12', '2025-12-09', '2025-12-06', '2025-12-06',
                '2025-12-02', '2025-11-23', '2025-11-16', '2025-11-14', '2025-10-29',
            ],
            'Client Name': [
                'Pat B.', 'Kara Keating B.', 'Holly H.', 'Jeffrey G.', 'Miriam O.',
                'Carine C.', 'Shanti F.', 'Carl D.', 'Chris V.', 'Kathy D.',
                'Paula O.', 'Benjamin M.', 'Todd H.', 'Scott S.', 'Eri S.',
            ],
            'Rating': [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
            'Review': [
                "Lauren is very professional and does a great job. I highly recommend!",
                "Saved the day with a prompt gift wrapping job. Followed all instructions!",
                "Lauren is lovely to work with. Excellent communication and great attention to detail.",
                "Lauren was great. Great communication went over and out of her way to help when needed. Can't recommend her enough.",
                "Lauren was great at communication... relaxed yet very efficient, and got the job done.",
                "Lauren is a pleasure to work with. She was also very responsive throughout our communication.",
                "Lauren has now done three events at our house. She is terrific and such a pleasure to work with.",
                "Lauren is extremely talented and professional. She completed the entire task with great care.",
                "Very easy and friendly. Highly recommended.",
                "She is really good!",
                "She did an absolutely fantastic job decorating my trees! She worked quickly and efficiently.",
                "Lauren was excellent. Super communicative, friendly, and great to work with.",
                "No text provided",
                "Lauren is smart, pleasant and tenacious. Great combo! Hire her!! Very pleased.",
                "Lauren went above and beyond. Much appreciated.",
            ]
        }
        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')

    # Domain mapping
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

df = load_data()


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
        st.link_button("LinkedIn", "https://www.linkedin.com/in/lchagaris", use_container_width=True)
    with c2:
        st.link_button("Portfolio", "https://www.laurendemidesign.com", use_container_width=True)
    
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

    # 5. FILTERS
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
    
    st.divider()
    
    # 6. DOWNLOAD REVIEWS
    if not df.empty:
        download_df = df[['Category', 'Date', 'Client Name', 'Rating', 'Review']].copy()
        download_df['Date'] = download_df['Date'].dt.strftime('%Y-%m-%d')
        st.download_button(
            "📥 Download Reviews", 
            download_df.to_csv(index=False).encode('utf-8'), 
            "Lauren_Chagaris_Verified_Reviews.csv", 
            use_container_width=True
        )


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
            {"text": "Lauren is smart, pleasant and tenacious. Great combo! Hire her!! Very pleased.", "author": "Scott S.", "cat": "Technical Support"},
            {"text": "Lauren was fantastic! She was on time, communicative, and did an amazing job.", "author": "Emily R.", "cat": "Event Staffing"},
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
        m2.metric("Verified Sample", f"{len(df)}")
        m3.metric("Composite Rating", "4.94")
        m4.metric("5-Star Tasks", "310", delta="Top 1% Rank", delta_color="normal")
        m5.metric("Operational Risk", "Negligible")
        # Custom green down-arrow risk label via HTML
        st.markdown("""
            <style>
            div[data-testid="column"]:nth-of-type(5) div[data-testid="stMetricValue"] ~ div {
                display: none !important;
            }
            </style>
        """, unsafe_allow_html=True)
        # Inject custom risk delta directly under the metric
        with m5:
            st.markdown('<div style="color: #16a34a; font-size: 0.875rem; font-weight: 600; margin-top: -10px;">▼ ~3% Risk</div>', unsafe_allow_html=True)

        st.divider()
        
        # ============================
        # SEARCH & REVIEW FEED
        # ============================
        search = st.text_input(
            f"🔍 Search {len(df)} verified records...", 
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

        # 1. FIVE-STAR STREAK TIMELINE
        st.markdown("#### 🔥 Five-Star Consistency Streak")
        st.caption("Each bar is a verified review in chronological order. Longest unbroken five-star streak highlighted below.")
        
        df_sorted = df.sort_values(by='Date').reset_index(drop=True)
        df_sorted['Review #'] = range(1, len(df_sorted) + 1)
        
        # Color coding: green=5star, orange=4star, red=1-2star
        def get_bar_color(rating):
            if rating == 5.0:
                return '5 Star'
            elif rating == 4.0:
                return '4 Star'
            else:
                return '1-2 Star'
        
        df_sorted['Rating Group'] = df_sorted['Rating'].apply(get_bar_color)
        
        # Calculate longest streak
        streak = 0
        max_streak = 0
        for _, row in df_sorted.iterrows():
            if row['Rating'] == 5.0:
                streak += 1
                max_streak = max(max_streak, streak)
            else:
                streak = 0
        
        # Build streak chart - thin bars with gaps visible
        color_scale = alt.Scale(
            domain=['5 Star', '4 Star', '1-2 Star'],
            range=['#22c55e', '#f59e0b', '#ef4444']
        )
        
        streak_chart = alt.Chart(df_sorted).mark_bar(size=4).encode(
            x=alt.X('Review #:Q', 
                     title='Review (Chronological Order)',
                     scale=alt.Scale(domain=[0, len(df_sorted) + 1], padding=0),
                     axis=alt.Axis(values=list(range(20, len(df_sorted), 20)))
            ),
            y=alt.Y('Rating:Q', 
                     title='Rating', 
                     scale=alt.Scale(domain=[0, 5.5])
            ),
            color=alt.Color('Rating Group:N', 
                           scale=color_scale, 
                           legend=alt.Legend(title='Rating', orient='top')
            ),
            tooltip=['Client Name:N', 'Date:T', 'Rating:Q', 'Category:N']
        ).properties(height=280).configure_view(
            strokeWidth=0
        )
        
        st.altair_chart(streak_chart, use_container_width=True)
        
        # Streak callout
        st.markdown(f"""
            <div class="streak-callout">
                <div class="streak-number">{max_streak}</div>
                <div class="streak-label">Consecutive five-star reviews — longest unbroken streak</div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # 2. DUAL DNA ANALYSIS
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 🧠 Operational Pillars")
            st.caption("Strategic grouping of synonyms for high-level trait mapping.")
            
            pillar_data = {
                "Execution Velocity": text_corpus.count("fast") + text_corpus.count("quick") + text_corpus.count("speed") + text_corpus.count("efficient") + text_corpus.count("efficiency"),
                "Composure (Calm/Easy)": text_corpus.count("calm") + text_corpus.count("easy") + text_corpus.count("patient") + text_corpus.count("stress-free"),
                "Communication Clarity": text_corpus.count("communicat") + text_corpus.count("talk") + text_corpus.count("conversation"),
                "Interpersonal IQ": text_corpus.count("nice") + text_corpus.count("friendly") + text_corpus.count("kind"),
                "High-Stakes Quality": text_corpus.count("recommend") + text_corpus.count("perfect") + text_corpus.count("fantastic") + text_corpus.count("wonderful"),
            }
            pillar_df = pd.DataFrame(list(pillar_data.items()), columns=['Pillar', 'Mentions'])
            pillar_chart = alt.Chart(pillar_df).mark_bar(color='#6366f1').encode(
                x='Mentions:Q', 
                y=alt.Y('Pillar:N', sort='-x', title='')
            ).properties(height=350).configure_axis(labelLimit=300)
            st.altair_chart(pillar_chart, use_container_width=True)

        with c2:
            st.markdown("#### 🗣️ Raw Keyword Frequency")
            st.caption("Direct 'Word of Mouth' terminology extracted from records.")
            
            keyword_data = {
                "Great": text_corpus.count("great"),
                "Recommend": text_corpus.count("recommend"),
                "Helpful": text_corpus.count("helpful"),
                "Professional": text_corpus.count("professional"),
                "Efficient": text_corpus.count("efficient"),
                "Communication": text_corpus.count("communicat"),
                "Quick/Fast": text_corpus.count("quick") + text_corpus.count("fast"),
                "Easy": text_corpus.count("easy"),
                "Excellent": text_corpus.count("excellent"),
                "Friendly": text_corpus.count("friendly"),
                "Amazing": text_corpus.count("amazing"),
                "Wonderful": text_corpus.count("wonderful"),
            }
            raw_df = pd.DataFrame(list(keyword_data.items()), columns=['Keyword', 'Count'])
            raw_chart = alt.Chart(raw_df).mark_bar(color='#6366f1').encode(
                x='Count:Q', 
                y=alt.Y('Keyword:N', sort='-x', title='')
            ).properties(height=350).configure_axis(labelLimit=300)
            st.altair_chart(raw_chart, use_container_width=True)