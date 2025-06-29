
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from datetime import timedelta

# Load the data
df = pd.read_csv('openai_tickets-1.csv')
df['created_at'] = pd.to_datetime(df['created_at'])

st.set_page_config(page_title="Launch Support Dashboard", layout="wide")

st.title("🚀 Launch Support Dashboard")
st.markdown("Monitor spikes in support tickets during launches and help your team respond faster.")

# Sidebar filters
st.sidebar.header("Filters")
severity = st.sidebar.selectbox("Severity", ["All"] + sorted(df['severity'].unique()))
queues = st.sidebar.multiselect("Queue", options=sorted(df['queue'].unique()), default=sorted(df['queue'].unique()))

# Apply filters
filtered_df = df.copy()
if severity != "All":
    filtered_df = filtered_df[filtered_df['severity'] == severity]
if queues:
    filtered_df = filtered_df[filtered_df['queue'].isin(queues)]

# Ticket volume chart
st.subheader("📈 Ticket Volume Per Hour")
volume = filtered_df.set_index('created_at').resample('H').size()
fig, ax = plt.subplots(figsize=(10, 4))
volume.plot(ax=ax)
ax.set_ylabel("Tickets")
ax.set_title("Ticket Volume Per Hour")
st.pyplot(fig)

# Breakdown by queue, topic, language
col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Top Queues")
    st.write(filtered_df['queue'].value_counts().head(5))
with col2:
    st.subheader("Top Topics")
    st.write(filtered_df['topic'].value_counts().head(5))
with col3:
    st.subheader("Top Languages")
    st.write(filtered_df['language'].value_counts().head(5))

# Spike alert block
st.subheader("⚠️ Spike Detection")

latest_hour = df['created_at'].max().floor('h')
last_hour_df = df[df['created_at'] >= latest_hour - timedelta(hours=1)]
high_sev_last_hour = last_hour_df[last_hour_df['severity'] == 'high']

if len(high_sev_last_hour) > 30:
    top_queue = high_sev_last_hour['queue'].value_counts().idxmax()
    top_topic = high_sev_last_hour['topic'].value_counts().idxmax()
    top_lang = high_sev_last_hour['language'].value_counts().idxmax()

    st.error(f'''
    🚨 **Spike Alert**  
    - {len(high_sev_last_hour)} high-severity tickets in the past hour  
    - Most affected queue: {top_queue}  
    - Most common issue: {top_topic}  
    - Most common language: {top_lang}  
    ''')
    st.markdown("👥 Recommend alerting Engineering + Support leads.")
else:
    st.success("✅ No major high-severity spike detected in the past hour.")
