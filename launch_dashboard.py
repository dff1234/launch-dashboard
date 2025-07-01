
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

# Top-level metrics
latest_hour = df['created_at'].max().floor('h')
last_hour_df = df[df['created_at'] >= latest_hour - timedelta(hours=1)]
high_sev_last_hour = last_hour_df[last_hour_df['severity'] == 'high']

col1, col2, col3 = st.columns(3)
col1.metric("High-Sev (last hr)", len(high_sev_last_hour))
col2.metric("Total Tickets", len(filtered_df))
top_topic = high_sev_last_hour['topic'].value_counts().idxmax() if not high_sev_last_hour.empty else "N/A"
col3.metric("Top Topic", top_topic)

# Spike detection
st.subheader("⚠️ Spike Detection")
if len(high_sev_last_hour) > 30:
    top_queue = high_sev_last_hour['queue'].value_counts().idxmax()
    top_lang = high_sev_last_hour['language'].value_counts().idxmax()

    st.error(f"🚨 {len(high_sev_last_hour)} high-severity tickets detected in the last hour!")
    st.markdown("### 💡 Recommended Actions")
    st.markdown("- 📣 Notify engineering lead")
    st.markdown("- 👥 Deploy 20+ BPO agents")
    st.markdown("- 🧾 Investigate `payment_declined` in Stripe logs")

    # Executive summary
    st.markdown("### 📝 Executive Update")
    summary_text = f"""**Executive Update – {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}**

• Root cause: {top_topic} in {top_queue}, language: {top_lang}  
• Current volume: {len(high_sev_last_hour)} high-severity tickets this hour  
• Mitigation: Recommended BPO surge + Eng investigation  
• Next update: {(pd.Timestamp.now() + pd.Timedelta(hours=1)).strftime('%H:%M')}  
• Blockers: Awaiting Stripe response  
"""
    st.text_area("📤 Copy-paste this update", summary_text, height=160)
else:
    st.success("✅ No major high-severity spike detected in the past hour.")

# Low-priority auto-triage option
st.subheader("🧹 Auto-Triage Low-Priority Tickets")
low_sev_df = filtered_df[filtered_df['severity'] == 'low']
if not low_sev_df.empty:
    st.info(f"{len(low_sev_df)} low-priority tickets detected – ready for triage.")
    st.download_button("📥 Download low-priority tickets", low_sev_df.to_csv(index=False), file_name="triage_low.csv")

# Breakdown views
st.subheader("🔍 Breakdown by Queue, Topic, Language")
col1, col2, col3 = st.columns(3)
with col1:
    st.write("**Top Queues**")
    st.write(filtered_df['queue'].value_counts().head(5))
with col2:
    st.write("**Top Topics**")
    st.write(filtered_df['topic'].value_counts().head(5))
with col3:
    st.write("**Top Languages**")
    st.write(filtered_df['language'].value_counts().head(5))

# Most recent high-severity tickets
st.subheader("📝 Recent High-Severity Tickets")
recent_high = filtered_df[filtered_df['severity'] == 'high'].sort_values('created_at', ascending=False).head(10)
st.dataframe(recent_high)

# Footer
st.caption(f"Last updated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
