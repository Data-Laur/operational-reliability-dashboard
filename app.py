import streamlit as st
import pandas as pd
import altair as alt
import os

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Operational Reliability Audit",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- DATA LOADING & GREEN AI OPTIMIZATION ---
@st.cache_data
def load_data():
    # Priority 1: Load the private master file if it exists (Local Dev)
    if os.path.exists("taskrabbit_reviews.csv"):
        df = pd.read_csv("taskrabbit_reviews.csv")
    # Priority 2: Load the public template (GitHub / Streamlit Cloud)
    elif os.path.exists("taskrabbit_reviews_TEMPLATE.csv"):
        df = pd.read_csv("taskrabbit_reviews_TEMPLATE.csv")
    else:
        # Fallback for empty repo state
        return pd.DataFrame(columns=["Date", "Category", "Rating", "Review", "Client Name"])
    
    # Standardize Column Names (Capitalize for display)
    df.columns = [c.strip().title() for c in df.columns]
    
    # Data Cleaning & Type Conversion
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    if 'Rating' in df.columns:
        df['Rating'] = pd.to_numeric(df['Rating'], errors='coerce')
        
    return df

def map_domains(category):
    """Maps raw task categories to high-level business domains."""
    cat_lower = str(category).lower()
    if any(x in cat_lower for x in ['mount', 'tv', 'install', 'shelf', 'art', 'curtain', 'blind']):
        return 'Mounting & Installation'
    elif any(x in cat_lower for x in ['assembl', 'ikea', 'furniture']):
        return 'Furniture Assembly'
    elif any(x in cat_lower for x in ['elec', 'light', 'fan', 'outlet', 'switch']):
        return 'Electrical Help'
    elif any(x in cat_lower for x in ['repair', 'fix', 'door', 'wall', 'hole']):
        return 'Home Repairs'
    elif any(x in cat_lower for x in ['move', 'heavy', 'lift', 'haul']):
        return 'Heavy Lifting & Moving'
    else:
        return 'General Handyman'

df = load_data()

# --- SIDEBAR PROFILE ---
with st.sidebar:
    if os.path.exists("profile.jpg"):
        st.image("profile.jpg", width=120)
    
    st.title("Lauren Chagaris")
    st.markdown("**AI Engineer & Data Scientist**")
    st.markdown("Focus: Sustainability & Optimization 🌿")
    
    st.link_button("LinkedIn", "https://www.linkedin.com/in/laurenchagaris", use_container_width=True)
    st.link_button("Portfolio", "https://www.laurendemidesign.com", use_container_width=True)
    
    st.divider()
    
    # Metrics in Sidebar
    total_tasks = 561 # Hardcoded verified count from platform
    audit_sample = len(df)
    st.metric("Lifetime Tasks", total_tasks)
    st.metric("Audit Sample", f"{audit_sample} ({round(audit_sample/total_tasks*100)}%)")

# --- MAIN DASHBOARD ---
st.markdown('<div style="background-color:#f8fafc; border-left: 5px solid #4338ca; padding: 20px; border-radius: 8px; margin-bottom: 25px;"><h2 style="margin-top:0; color:#1e293b;">The Chagaris Vibe Check</h2><p style="font-size:1.1rem; line-height:1.5; color:#475569;">This dashboard audits <strong>561 real-world tasks</strong> to provide empirical proof of reliability and problem-solving.</p></div>', unsafe_allow_html=True)

# --- VERIFICATION ASSETS (Fault Tolerant) ---
if os.path.exists("reviews_screenshot.png"):
    with st.expander("✅ Verified Platform Data", expanded=False):
        try:
            st.image("reviews_screenshot.png", use_container_width=True)
        except Exception:
            st.warning("Visual asset optimizing. See README.")

st.divider()

# --- FILTERS & DOMAIN MAPPING ---
# Ensure Domain column exists before any filtering logic
if 'Domain' not in df.columns and 'Category' in df.columns:
    df['Domain'] = df['Category'].apply(map_domains)
elif 'Domain' not in df.columns:
    df['Domain'] = "Unknown"

# 1. Domain Filter
unique_domains = sorted(df['Domain'].unique()) if 'Domain' in df.columns else []
selected_domains = st.multiselect("Select Business Domains", unique_domains, default=unique_domains)

# 2. Category Filter (Dependent on Domain)
if 'Category' in df.columns:
    available_cats = sorted(df[df['Domain'].isin(selected_domains)]['Category'].unique())
    with st.expander("Filter Specific Categories", expanded=False):
        selected_cats = st.multiselect("Categories", available_cats, default=available_cats)
else:
    selected_cats = []

# Apply Filters
if 'Domain' in df.columns and 'Category' in df.columns:
    filtered_df = df[
        (df['Domain'].isin(selected_domains)) & 
        (df['Category'].isin(selected_cats))
    ]
else:
    filtered_df = df

# --- TABS & VISUALIZATION ---
t_audit, t_analytics = st.tabs(["📂 Audit Feed", "📈 Analytics & Insights"])

with t_audit:
    st.dataframe(
        filtered_df[['Date', 'Category', 'Rating', 'Review', 'Client Name'] if 'Client Name' in filtered_df.columns else filtered_df.columns],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DateColumn("Service Date", format="MMM DD, YYYY"),
            "Rating": st.column_config.NumberColumn("Rating", format="%d ⭐"),
            "Review": st.column_config.TextColumn("Client Feedback", width="large"),
        }
    )
    
    st.download_button(
        label="📥 Download Audit CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name="Lauren_Chagaris_Performance_Audit.csv",
        mime="text/csv"
    )

with t_analytics:
    if not filtered_df.empty and 'Date' in filtered_df.columns:
        # Chart 1: Monthly Task Volume
        monthly_vol = filtered_df.set_index('Date').resample('M').size().reset_index(name='Count')
        chart = alt.Chart(monthly_vol).mark_bar(color='#4338ca').encode(
            x='Date:T',
            y='Count:Q',
            tooltip=['Date', 'Count']
        ).properties(title="Longitudinal Reliability (Task Volume over Time)")
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Insufficient data for analytics visualization.")