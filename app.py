from pathlib import Path
import streamlit as st
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns 
import plotly.express as px
import datetime as dt

sns.set_theme(font_scale=1.2)

st.set_page_config(
    layout='wide',
    page_title="Startup Analysis",
    page_icon=":shark:",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

# Resolve file path relative to this script
BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "processed" / "startup_cleaned.csv"

df = pd.read_csv(DATA_PATH)
df['date'] = pd.to_datetime(df['date'])
df['month'] = df['date'].dt.month
df['year'] = df['date'].dt.year

# ==========================================
# 1. OVERALL ANALYSIS
# ==========================================
def load_overall_analysis():
    st.markdown(
        """
        <h2 style='text-align: justify; color: salmon; border-bottom: 3px solid grey; padding-bottom: 10px;' >
            🚀 Complete Dataset of Indian Startup Funding During 2015 - 2022 
        </h2>
        """, 
        unsafe_allow_html=True
    )

    st.dataframe(df)
    
    st.title("Overall analysis")
    
    # Total invested amount 
    total = int(df['amount'].sum())

    # Max funding 
    max_funding = df.groupby('startup')['amount'].max().sort_values(ascending=False).head().values[0]

    # Average funding size on one startup investment
    avg_funding = df.groupby('startup')['amount'].sum().mean()

    # Total number of startups 
    total_startup = df['startup'].nunique()

    st.markdown("---")
    
    # Making of metric cards
    col1, col2, col3, col4 = st.columns(4)

    with col1: 
        st.metric(label=" 🎯Total Investment :", value=str(total) + " Cr.", border=True)

    with col2: 
        st.metric(" 🎯 Maximun Investment :", value=str(max_funding) + " Cr.", border=True)

    with col3: 
        st.metric(" 🎯 average Investment :", value=str(round(avg_funding)) + " Cr.", border=True)

    with col4: 
        st.metric(" 🎯Total No Startup :", value=str(total_startup), border=True)

    # Month on month investment
    st.header("MoM graph")
    selected_option = st.selectbox('Selected Type : ', ['Total', 'Count'])

    if selected_option == 'Total':
        temp_df = df.groupby(['year', 'month'])['amount'].sum().reset_index()
    else:
        temp_df = df.groupby(['year', 'month'])['amount'].count().reset_index()
              
    temp_df['x_axis'] = temp_df['month'].astype('str') + '-' + temp_df['year'].astype('str')

    fig, ax = plt.subplots(figsize=(16, 6))
    sns.lineplot(data=temp_df, x='x_axis', y='amount', ax=ax, marker='o')
    plt.xticks(rotation=90, fontsize=8)
    plt.title("MoM Trend")
    st.pyplot(fig)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1: 
        st.subheader("Top sector for geting funding ")
        sector_sum = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).reset_index().head(10)

        fig1, ax1 = plt.subplots(figsize=(4, 4))
        ax1.pie(
            x=sector_sum['amount'],
            labels=sector_sum['vertical'],
            autopct="%0.1f%%",
            startangle=90,
            textprops={'fontsize': 4}
        )
        st.pyplot(fig1, use_container_width=False)

    with col2: 
        st.subheader("Top vertical sector for geting funding ")
        sector_counts = df['vertical'].value_counts().reset_index().head(10)

        fig3, ax3 = plt.subplots(figsize=(5, 15))
        ax3.pie(
            x=sector_counts['count'],
            labels=sector_counts['vertical'],
            autopct="%0.1f%%",
            startangle=90,
            textprops={'fontsize': 3}
        )
        st.pyplot(fig3, use_container_width=False)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1: 
        st.subheader("sum the  Top sector for funding")
        sector_sum = df.groupby('vertical')['amount'].sum().sort_values(ascending=False).reset_index().head(10)

        fig4, ax4 = plt.subplots(figsize=(5, 5))
        ax4.pie(
            x=sector_sum['amount'],
            labels=sector_counts['vertical'],
            autopct="%0.1f%%",
            startangle=90,
            textprops={'fontsize': 5}
        )
        st.pyplot(fig4, use_container_width=False)

    with col2: 
        st.subheader(" top 10 types of funding ")
        round_counts = df['round'].value_counts().reset_index().head(10)
        
        fig5 = sns.catplot(data=round_counts, kind='bar', x='round', y='count', hue='round', height=4.25, aspect=1.25)
        fig5.set_xticklabels(fontsize=8, rotation=90, ha='right')
        st.pyplot(fig5)

    st.markdown("---")
    col5, col6 = st.columns(2)
    with col5: 
        st.subheader(" top 10 City wise funding ( count )")
        city_count = df['city'].value_counts().reset_index().head(10)

        fig6 = sns.catplot(data=city_count, kind='bar', x='city', y='count', hue='city', height=8, aspect=1.75)
        st.pyplot(fig6) 
        
    with col6: 
        st.subheader(" top 10 City wise funding ( sum ) ")
        startup_year = df.groupby(['startup', 'year'])['amount'].sum().sort_values(ascending=False).reset_index().head(10)

        fig6 = sns.catplot(data=city_count, kind='bar', x='city', y='count', hue='city', height=8, aspect=1.75)
        st.pyplot(fig6)


# ==========================================
# 2. STARTUP DETAILS ANALYSIS
# ==========================================
def load_startup_details(selected_startup):
    st.title(f"🚀 {selected_startup.title()}")

    startup_df = df[df['startup'].str.lower() == selected_startup.lower()].sort_values(by='date', ascending=False)

    if startup_df.empty:
        st.warning("No details found for this startup.")
        return

    # Extract primary metadata (from latest record)
    latest_info = startup_df.iloc[0]
    industry = latest_info['vertical'] if pd.notna(latest_info.get('vertical')) else 'Not Available'
    sub_industry = latest_info['subvertical'] if pd.notna(latest_info.get('subvertical')) else 'Not Available'
    location = latest_info['city'] if pd.notna(latest_info.get('city')) else 'Not Available'
    
    # Check if founders column exists in dataset
    if 'founders' in startup_df.columns:
        founders = latest_info['founders'] if pd.notna(latest_info.get('founders')) else 'Not Listed'
    else:
        founders = "N/A (Not in dataset)"

    total_raised = startup_df['amount'].sum()
    total_rounds = len(startup_df)

    # 1. Company Overview Cards
    col1, col2, col3 = st.columns(3)
    with col1: 
        st.metric("🏢 Industry (Vertical)", str(industry), border=True)
        st.metric("👥 Founders", str(founders), border=True)
    with col2: 
        st.metric("🎯 Sub-Industry", str(sub_industry), border=True)
        st.metric("📍 Location", str(location), border=True)
    with col3: 
        st.metric("💰 Total Capital Raised", f"{total_raised:,.2f} Cr.", border=True)
        st.metric("📈 Funding Rounds", str(total_rounds), border=True)

    st.markdown("---")

    # 2. Funding Rounds Breakdown
    st.subheader("📑 Funding Rounds History")
    
    rounds_table = startup_df[['date', 'round', 'investors', 'amount']].copy()
    rounds_table['date'] = rounds_table['date'].dt.strftime('%Y-%m-%d')
    rounds_table.rename(columns={
        'date': 'Date',
        'round': 'Stage / Round',
        'investors': 'Investors',
        'amount': 'Amount (in Cr.)'
    }, inplace=True)
    
    st.dataframe(rounds_table.reset_index(drop=True), use_container_width=True)

    st.markdown("---")

    # 3. Similar Companies
    st.subheader("🔍 Similar Companies")
    
    if industry != 'Not Available':
        similar_df = df[
            (df['vertical'].str.lower() == str(industry).lower()) & 
            (df['startup'].str.lower() != selected_startup.lower())
        ]
        
        similar_startups = similar_df[['startup', 'subvertical', 'city', 'amount']].drop_duplicates(subset=['startup'])
        similar_startups.rename(columns={
            'startup': 'Company Name',
            'subvertical': 'Sub-Industry',
            'city': 'City',
            'amount': 'Total Funding (Cr.)'
        }, inplace=True)

        if not similar_startups.empty:
            st.dataframe(similar_startups.head(10).reset_index(drop=True), use_container_width=True)
        else:
            st.info("No similar companies found in the same vertical.")
    else:
        st.info("Cannot determine similar companies without industry vertical.")


# ==========================================
# 3. INVESTOR DETAILS ANALYSIS
# ==========================================
def load_investor_details(investor):
    st.title(investor)
    
    # Load recent 5 investments
    last5_df = df[df['investors'].str.contains(investor, na=False)].head()[['date', 'startup', 'vertical', 'city', 'round', 'amount']]
    st.subheader("Most Recent Investment.")
    st.dataframe(last5_df)

    # Biggest investment
    big_series = df[df['investors'].str.contains(investor, na=False)].groupby('startup')['amount'].sum().sort_values(ascending=False).head()
    st.subheader("Biggesr Investment.")
    big_df = pd.DataFrame(big_series)
    st.dataframe(big_series)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1: 
        big_df = big_series.reset_index() 
        st.subheader("Seaborn bar (using catplot)")

        g = sns.catplot(data=big_df, kind='bar', x='startup', y='amount', hue='startup', height=5, aspect=1.5)
        for container in g.ax.containers:
            g.ax.bar_label(container, fmt='%.2f', padding=3)

        plt.title("Top 5 Investment")
        st.pyplot(g)
        
    with col2: 
        st.subheader("Biggesr Investment. in pie ")
        vertical_series = df[df['investors'].str.contains(investor, na=False)].groupby('vertical')['amount'].sum().sort_values(ascending=False).head()
        fig1, ax1 = plt.subplots()
        ax1.pie(vertical_series, labels=vertical_series.index, autopct="%0.01f%%")
        st.pyplot(fig1)
        
    st.markdown("---")
    col4, col5 = st.columns(2)
    with col4: 
        st.subheader("Biggesr round Investment. in pie ")
        round_series = df[df['investors'].str.contains(investor, na=False)].groupby('round')['amount'].sum().sort_values(ascending=False).head()
        fig1, ax1 = plt.subplots()
        ax1.pie(round_series, labels=round_series.index, autopct="%0.01f%%")
        st.pyplot(fig1)

    with col5: 
        st.subheader("Biggest city Investment. in pie ")
        city_series = df[df['investors'].str.contains(investor, na=False)].groupby('city')['amount'].sum().sort_values(ascending=False).head()
        fig1, ax1 = plt.subplots(figsize=(1.5, 1.5))
        ax1.pie(city_series, labels=city_series.index, autopct="%0.01f%%", textprops={'fontsize': 4})
        st.pyplot(fig1)

    st.markdown("---")
    col6, col7 = st.columns(2)
    with col6: 
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['year'] = df['date'].dt.year
        st.subheader("YOY Investment. in line ")
        year_series = df[df['investors'].str.contains(investor, na=False)].groupby('year')['amount'].sum().sort_values(ascending=False)
        year_df = pd.DataFrame(year_series).reset_index()

        linge_g = sns.relplot(data=year_df, kind='line', x='year', y='amount', height=5, aspect=1.5)
        st.pyplot(linge_g)

    with col7: 
        st.subheader("YOY Investment")
        year_series = df[df['investors'].str.contains(investor, na=False)].groupby('year')['amount'].sum().sort_index()
        year_df = year_series.reset_index()

        line_yoy = sns.relplot(data=year_df, kind='line', x='year', y='amount', markers=True, height=5, aspect=1.5)
        st.pyplot(line_yoy)


# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
st.title("Indian Startup Funding Dashboard", anchor=False)

st.sidebar.title("Statrup Funding Analysis.")
option = st.sidebar.selectbox('Select one :', ['Overall Analysis', 'Startup', 'Investor'])

if option == 'Overall Analysis':
    load_overall_analysis()

elif option == 'Startup':
    all_startups = sorted(df['startup'].dropna().unique().tolist())
    selected_startup = st.sidebar.selectbox('Select Startup:', all_startups)
    btn1 = st.sidebar.button("Find Startup Details")
    
    if btn1 or selected_startup:
        load_startup_details(selected_startup)

else:
    selcted_investor = st.sidebar.selectbox(
        'Select Investor :', 
        sorted(set(sum(df['investors'].dropna().str.split(','), [])))
    )

    btn2 = st.sidebar.button("Find Invertor Details")
    if btn2:
        load_investor_details(selcted_investor)