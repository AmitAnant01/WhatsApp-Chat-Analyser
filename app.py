import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="WhatsApp Chat Analyzer",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

:root {
    --green:     #25D366;
    --teal:      #128C7E;
    --dark-teal: #075E54;
    --bg:        #0d0d0d;
    --surface:   #161616;
    --border:    #272727;
    --text:      #e8e8e8;
    --muted:     #6b6b6b;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
.main, .block-container { background-color: var(--bg) !important; }

section[data-testid="stSidebar"] {
    background: #0d0d0d !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--text) !important; }

.stat-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.1rem 1rem 0.9rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--dark-teal), var(--green));
}
.stat-val {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.55rem;
    font-weight: 600;
    color: var(--green);
    line-height: 1.1;
}
.stat-label {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-top: 0.3rem;
}

.info-strip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 3px solid var(--green);
    border-radius: 8px;
    padding: 0.85rem 1.1rem;
    margin-bottom: 0.65rem;
}
.info-strip .lbl {
    font-size: 0.68rem;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.info-strip .val {
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text);
    margin-top: 0.15rem;
}

.sec-head {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.76rem;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 1.8rem 0 0.9rem;
    padding-bottom: 0.45rem;
    border-bottom: 1px solid var(--border);
}

.stTabs [data-baseweb="tab-list"] {
    background: var(--surface) !important;
    border-radius: 8px;
    padding: 0.25rem;
    gap: 0.15rem;
    border: 1px solid var(--border);
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 6px !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    padding: 0.4rem 0.9rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--dark-teal) !important;
    color: #fff !important;
    font-weight: 600 !important;
}

.stButton > button {
    background: var(--dark-teal) !important;
    color: #fff !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 7px !important;
    padding: 0.55rem 1.2rem !important;
    width: 100% !important;
}
.stButton > button:hover { background: var(--teal) !important; }

.stSelectbox > div > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: 7px !important;
}

.footer {
    text-align: center;
    color: var(--muted);
    font-size: 0.75rem;
    padding: 2rem 0 1rem;
    border-top: 1px solid var(--border);
    margin-top: 3rem;
}

#MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── constants ────────────────────────────────────────────────────────────────
GREEN_SCALE  = ['#075E54', '#128C7E', '#25D366']
ACCENT_SCALE = ['#075E54', '#128C7E', '#25D366', '#34B7F1', '#00BCD4']
GREEN_LIST   = ['#25D366','#128C7E','#075E54','#34B7F1','#00BCD4',
                '#4CAF50','#8BC34A','#FFC107','#FF9800','#FF5252']

BASE_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter', color='#e8e8e8', size=12),
    margin=dict(l=10, r=10, t=36, b=10),
    xaxis=dict(gridcolor='#272727', showgrid=True, zeroline=False),
    yaxis=dict(gridcolor='#272727', showgrid=True, zeroline=False),
)

def L(**kw):
    """Return a merged copy of BASE_LAYOUT — safe override, no duplicate keys."""
    return {**BASE_LAYOUT, **kw}

def fmt(n):
    try: n = int(n)
    except: return str(n)
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)

def card(icon, val, label):
    return f"""<div class='stat-card'>
        <div style='font-size:1.3rem;margin-bottom:.3rem'>{icon}</div>
        <div class='stat-val'>{val}</div>
        <div class='stat-label'>{label}</div>
    </div>"""

def strip(label, val, color='var(--green)'):
    return f"""<div class='info-strip' style='border-left-color:{color}'>
        <div class='lbl'>{label}</div>
        <div class='val'>{val}</div>
    </div>"""

def sec(title):
    st.markdown(f"<div class='sec-head'>{title}</div>", unsafe_allow_html=True)


# ─── sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:.5rem 0 1.5rem'>
        <div style='font-family:JetBrains Mono,monospace;font-size:1rem;font-weight:600;color:#25D366;'>
            WhatsApp Analyzer
        </div>
        <div style='font-size:.72rem;color:#6b6b6b;margin-top:.2rem;'>chat export analyser</div>
    </div>""", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload Your chat here (.txt)", type=['txt'])
    st.markdown("""<div style='font-size:.72rem;color:#6b6b6b;margin-top:.5rem;line-height:1.7;'>
    Supported for only Without media
    </div>""", unsafe_allow_html=True)


# ─── hero ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='padding:2rem 0 1rem'>
    <div style='font-family:JetBrains Mono,monospace;font-size:1.9rem;font-weight:600;
                color:#e8e8e8;line-height:1.15;'>WhatsApp Chat Analyzer</div>
    <div style='color:#6b6b6b;font-size:.9rem;margin-top:.4rem;'>
        Timelines · Activity patterns · Word analysis · User insights
    </div>
</div>""", unsafe_allow_html=True)

if uploaded_file is None:
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(strip("Analytics", "Timelines, heatmaps, activity patterns"), unsafe_allow_html=True)
    with c2: st.markdown(strip("User stats", "Per-user breakdown, response times"), unsafe_allow_html=True)
    with c3: st.markdown(strip("Text analysis", "Word cloud, bigrams, sentiment"), unsafe_allow_html=True)
    st.info("Upload a WhatsApp chat export from the sidebar to get started.")
    st.stop()


# ─── parse ────────────────────────────────────────────────────────────────────
with st.spinner("Parsing..."):
    df = preprocessor.preprocess(uploaded_file.getvalue().decode("utf-8"))

if df.empty:
    st.error("Could not parse this file. Make sure it's a valid WhatsApp .txt export.")
    st.stop()

user_list = sorted(u for u in df['user'].unique() if u != 'group_notification')
user_list.insert(0, "Overall")

with st.sidebar:
    st.markdown("---")
    selected_user = st.selectbox("Analyze for", user_list)
    run = st.button("Run analysis")
    st.markdown("---")
    st.markdown(f"""
    <div style='font-size:.75rem;color:#6b6b6b;line-height:2;'>
    From &nbsp;&nbsp;<b style='color:#e8e8e8'>{df['only_date'].min()}</b><br>
    To &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;<b style='color:#e8e8e8'>{df['only_date'].max()}</b><br>
    Participants &nbsp;<b style='color:#e8e8e8'>{len(user_list)-1}</b><br>
    Total msgs &nbsp;&nbsp;<b style='color:#25D366'>{fmt(len(df))}</b>
    </div>""", unsafe_allow_html=True)

if not run:
    st.info("Select a user and click **Show analysis**.")
    st.stop()


# ─── fetch ────────────────────────────────────────────────────────────────────
(num_messages, num_words, num_media, num_links,
 num_emojis, num_deleted, avg_len, avg_words) = helper.fetch_stats(selected_user, df)

daily_tl     = helper.daily_timeline(selected_user, df)
monthly_tl   = helper.monthly_timeline(selected_user, df)
quarterly_tl = helper.quarterly_timeline(selected_user, df)
hourly_act   = helper.hourly_activity(selected_user, df)
yearly_act   = helper.yearly_activity(selected_user, df)
busy_day     = helper.week_activity_map(selected_user, df)
busy_month   = helper.month_activity_map(selected_user, df)
heatmap_df   = helper.activity_heatmap(selected_user, df)
wc           = helper.create_wordcloud(selected_user, df)
common_words = helper.most_common_words(selected_user, df)
bigrams      = helper.bigram_analysis(selected_user, df)
emoji_df     = helper.emoji_helper(selected_user, df)
link_df      = helper.link_analysis(selected_user, df)
sentiment    = helper.sentiment_basic(selected_user, df)
max_streak, cur_streak = helper.chat_streak(df)
best_date, best_count  = helper.most_active_date(selected_user, df)
response_df  = helper.response_time_analysis(df)
emoji_user   = helper.emoji_per_user(df)
weekly_tr    = helper.weekly_trend(selected_user, df)
len_dist     = helper.msg_length_distribution(selected_user, df)


# ─── overview ─────────────────────────────────────────────────────────────────
sec("Overview")
metrics = [
    ("💬", fmt(num_messages), "Messages"),
    ("🔤", fmt(num_words),    "Words"),
    ("🖼️", fmt(num_media),   "Media"),
    ("🔗", fmt(num_links),    "Links"),
    ("😀", fmt(num_emojis),   "Emojis"),
    ("🗑️", fmt(num_deleted), "Deleted"),
    ("📏", str(avg_len),      "Avg length"),
    ("📝", str(avg_words),    "Avg words"),
]
for col, (icon, val, label) in zip(st.columns(len(metrics)), metrics):
    col.markdown(card(icon, val, label), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
dominant = max(sentiment, key=sentiment.get)
sent_color = '#25D366' if dominant == 'Positive' else '#FF5252' if dominant == 'Negative' else '#FFC107'
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(strip("Longest streak",     f"{max_streak} days in a row"), unsafe_allow_html=True)
with c2: st.markdown(strip("Current streak",     f"{cur_streak} days"), unsafe_allow_html=True)
with c3: st.markdown(strip("Most active day",    f"{best_date}  ·  {fmt(best_count)} msgs"), unsafe_allow_html=True)
with c4: st.markdown(strip("Dominant sentiment", f"{dominant}  ·  {sentiment[dominant]}%", sent_color), unsafe_allow_html=True)


# ─── tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Timelines", "Activity", "Users", "Words & Text", "Emojis & Links", "Insights"
])

# ── Timelines ─────────────────────────────────────────────────────────────────
with tab1:
    sec("Daily message count")
    fig = px.area(daily_tl, x='only_date', y='message',
                  labels={'only_date':'Date','message':'Messages'},
                  color_discrete_sequence=['#25D366'])
    fig.update_traces(fill='tozeroy', line_color='#25D366', fillcolor='rgba(37,211,102,0.1)')
    fig.update_layout(**L())
    st.plotly_chart(fig, use_container_width=True)

    sec("Weekly trend (last 16 weeks)")
    fig_w = px.bar(weekly_tr, x='week_start', y='count',
                   labels={'week_start':'Week','count':'Messages'},
                   color='count', color_continuous_scale=GREEN_SCALE)
    fig_w.update_layout(**L(showlegend=False, coloraxis_showscale=False))
    st.plotly_chart(fig_w, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        sec("Monthly")
        fig2 = px.bar(monthly_tl, x='time', y='message',
                      labels={'time':'Month','message':'Messages'},
                      color='message', color_continuous_scale=GREEN_SCALE)
        fig2.update_layout(**L(showlegend=False, coloraxis_showscale=False))
        st.plotly_chart(fig2, use_container_width=True)

    with c2:
        sec("Quarterly")
        fig3 = px.bar(quarterly_tl, x='label', y='message',
                      labels={'label':'Quarter','message':'Messages'},
                      color='message', color_continuous_scale=GREEN_SCALE)
        fig3.update_layout(**L(showlegend=False, coloraxis_showscale=False))
        st.plotly_chart(fig3, use_container_width=True)

    sec("Yearly")
    fig4 = px.line(yearly_act, x='year', y='message', markers=True,
                   labels={'year':'Year','message':'Messages'},
                   color_discrete_sequence=['#25D366'])
    fig4.update_traces(line_width=2.5, marker_size=8)
    fig4.update_layout(**L())
    st.plotly_chart(fig4, use_container_width=True)

    if selected_user == 'Overall':
        sec("Top 5 users — monthly messages")
        user_time = helper.user_activity_over_time(df)
        fig5 = go.Figure()
        for i, (user, udf) in enumerate(user_time.items()):
            fig5.add_trace(go.Scatter(
                x=udf['time'], y=udf['message'], name=user,
                mode='lines+markers',
                line=dict(color=GREEN_LIST[i % len(GREEN_LIST)], width=2),
                marker=dict(size=5),
            ))
        fig5.update_layout(**L())
        st.plotly_chart(fig5, use_container_width=True)


# ── Activity ──────────────────────────────────────────────────────────────────
with tab2:
    c1, c2 = st.columns(2)
    with c1:
        sec("Day of week")
        fig = px.bar(x=busy_day.index, y=busy_day.values,
                     labels={'x':'Day','y':'Messages'},
                     color=busy_day.values, color_continuous_scale=GREEN_SCALE)
        fig.update_layout(**L(showlegend=False, coloraxis_showscale=False))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        sec("Month of year")
        fig2 = px.bar(x=busy_month.index, y=busy_month.values,
                      labels={'x':'Month','y':'Messages'},
                      color=busy_month.values, color_continuous_scale=ACCENT_SCALE)
        fig2.update_layout(**L(showlegend=False, coloraxis_showscale=False))
        st.plotly_chart(fig2, use_container_width=True)

    sec("Hour of day")
    fig3 = px.bar(hourly_act, x='hour', y='message',
                  labels={'hour':'Hour','message':'Messages'},
                  color='message', color_continuous_scale=GREEN_SCALE)
    fig3.update_layout(**L(showlegend=False, coloraxis_showscale=False))
    st.plotly_chart(fig3, use_container_width=True)

    sec("Heatmap — day vs hour period")
    if not heatmap_df.empty:
        fig4 = px.imshow(heatmap_df,
                         color_continuous_scale=['#0d0d0d','#075E54','#25D366'],
                         labels=dict(x='Hour period', y='Day', color='Messages'),
                         aspect='auto')
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                           font=dict(family='Inter', color='#e8e8e8'),
                           margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig4, use_container_width=True)

    sec("Day activity — polar view")
    fig5 = go.Figure(go.Barpolar(
        r=busy_day.values, theta=busy_day.index,
        marker_color=busy_day.values, marker_colorscale=GREEN_SCALE, opacity=0.9,
    ))
    fig5.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                       polar=dict(bgcolor='rgba(0,0,0,0)',
                                  radialaxis=dict(visible=True, gridcolor='#333'),
                                  angularaxis=dict(gridcolor='#333')),
                       font=dict(color='#e8e8e8'),
                       margin=dict(l=20, r=20, t=20, b=20), height=380)
    st.plotly_chart(fig5, use_container_width=True)


# ── Users ─────────────────────────────────────────────────────────────────────
with tab3:
    if selected_user == 'Overall':
        x, new_df = helper.most_busy_users(df)

        c1, c2 = st.columns(2)
        with c1:
            sec("Most active users")
            fig = px.bar(x=x.values, y=x.index, orientation='h',
                         labels={'x':'Messages','y':'User'},
                         color=x.values, color_continuous_scale=GREEN_SCALE)
            fig.update_layout(**L(showlegend=False, coloraxis_showscale=False,
                                  yaxis=dict(autorange='reversed', gridcolor='#272727')))
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            sec("Message share %")
            fig2 = px.pie(new_df.head(8), values='percent', names='name',
                          color_discrete_sequence=GREEN_LIST, hole=0.45)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                               font=dict(family='Inter', color='#e8e8e8'),
                               legend=dict(bgcolor='rgba(0,0,0,0)'),
                               margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)

        sec("User stats table")
        st.dataframe(new_df.style.background_gradient(cmap='Greens', subset=['percent']),
                     use_container_width=True)

        sec("Avg message length by user")
        avg_len_df = helper.user_message_length(df).reset_index()
        avg_len_df.columns = ['user', 'avg_length']
        fig3 = px.bar(avg_len_df, x='avg_length', y='user', orientation='h',
                      color='avg_length', color_continuous_scale=GREEN_SCALE,
                      labels={'avg_length':'Avg characters','user':'User'})
        fig3.update_layout(**L(showlegend=False, coloraxis_showscale=False,
                               yaxis=dict(autorange='reversed', gridcolor='#272727')))
        st.plotly_chart(fig3, use_container_width=True)

        sec("Emoji usage by user")
        eu = emoji_user.reset_index()
        eu.columns = ['user', 'emojis']
        fig4 = px.bar(eu, x='emojis', y='user', orientation='h',
                      color='emojis', color_continuous_scale=['#128C7E','#FFC107'],
                      labels={'emojis':'Total emojis','user':'User'})
        fig4.update_layout(**L(showlegend=False, coloraxis_showscale=False,
                               yaxis=dict(autorange='reversed', gridcolor='#272727')))
        st.plotly_chart(fig4, use_container_width=True)

        if not response_df.empty:
            sec("Avg response time (minutes)")
            fig5 = px.bar(response_df, x='avg_response_min', y='user', orientation='h',
                          color='avg_response_min',
                          color_continuous_scale=['#25D366','#FF9800'],
                          labels={'avg_response_min':'Avg response (min)','user':'User'})
            fig5.update_layout(**L(showlegend=False, coloraxis_showscale=False,
                                   yaxis=dict(autorange='reversed', gridcolor='#272727')))
            st.plotly_chart(fig5, use_container_width=True)

    else:
        st.info(f"Showing stats for **{selected_user}**. Switch to Overall for cross-user comparison.")
        udf = df[df['user'] == selected_user]
        c1, c2, c3 = st.columns(3)
        fav_hour = udf['hour'].value_counts().idxmax() if len(udf) > 0 else 'N/A'
        with c1: st.markdown(strip("Active since",    str(udf['only_date'].min())), unsafe_allow_html=True)
        with c2: st.markdown(strip("Total messages",  fmt(len(udf))), unsafe_allow_html=True)
        with c3: st.markdown(strip("Peak hour",       f"{fav_hour}:00 – {fav_hour+1}:00"), unsafe_allow_html=True)


# ── Words & Text ──────────────────────────────────────────────────────────────
with tab4:
    c1, c2 = st.columns(2)
    with c1:
        sec("Word cloud")
        fig_wc, ax = plt.subplots(figsize=(8, 4))
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        fig_wc.patch.set_facecolor('#161616')
        st.pyplot(fig_wc)
        plt.close()

    with c2:
        sec("Most common words")
        if not common_words.empty:
            fig2 = px.bar(common_words.head(15), x='count', y='word', orientation='h',
                          color='count', color_continuous_scale=GREEN_SCALE,
                          labels={'count':'Frequency','word':'Word'})
            fig2.update_layout(**L(showlegend=False, coloraxis_showscale=False,
                                   yaxis=dict(autorange='reversed', gridcolor='#272727')))
            st.plotly_chart(fig2, use_container_width=True)

    sec("Top bigrams (word pairs)")
    if not bigrams.empty:
        fig3 = px.bar(bigrams.head(15), x='count', y='bigram', orientation='h',
                      color='count', color_continuous_scale=ACCENT_SCALE,
                      labels={'count':'Frequency','bigram':'Word pair'})
        fig3.update_layout(**L(showlegend=False, coloraxis_showscale=False,
                               yaxis=dict(autorange='reversed', gridcolor='#272727')))
        st.plotly_chart(fig3, use_container_width=True)

    sec("Message length distribution")
    len_dist.columns = ['length_bucket', 'count']
    fig_ld = px.bar(len_dist, x='length_bucket', y='count',
                    labels={'length_bucket':'Character range','count':'Messages'},
                    color='count', color_continuous_scale=GREEN_SCALE)
    fig_ld.update_layout(**L(showlegend=False, coloraxis_showscale=False))
    st.plotly_chart(fig_ld, use_container_width=True)

    sec("Sentiment breakdown")
    c1, c2 = st.columns([1, 2])
    with c1:
        for label, val in sentiment.items():
            color = '#25D366' if label == 'Positive' else '#FF5252' if label == 'Negative' else '#FFC107'
            st.markdown(strip(label, f"{val}%", color), unsafe_allow_html=True)
    with c2:
        fig4 = go.Figure(go.Pie(
            labels=list(sentiment.keys()), values=list(sentiment.values()),
            hole=0.55, marker_colors=['#25D366','#FF5252','#FFC107'],
        ))
        fig4.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                           font=dict(family='Inter', color='#e8e8e8'),
                           legend=dict(bgcolor='rgba(0,0,0,0)'),
                           margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(fig4, use_container_width=True)

    sec("Full word frequency table")
    if not common_words.empty:
        st.dataframe(common_words.style.background_gradient(cmap='Greens', subset=['count']),
                     use_container_width=True)


# ── Emojis & Links ────────────────────────────────────────────────────────────
with tab5:
    c1, c2 = st.columns(2)
    with c1:
        sec("Top emojis")
        if not emoji_df.empty:
            fig = px.bar(emoji_df.head(15), x='count', y='emoji', orientation='h',
                         color='count', color_continuous_scale=['#075E54','#FFC107'],
                         labels={'count':'Times used','emoji':'Emoji'})
            fig.update_layout(**L(showlegend=False, coloraxis_showscale=False,
                                  yaxis=dict(autorange='reversed', gridcolor='#272727')))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No emojis found in this chat.")

    with c2:
        sec("Emoji distribution")
        if not emoji_df.empty:
            fig2 = px.pie(emoji_df.head(10), values='count', names='emoji',
                          color_discrete_sequence=GREEN_LIST, hole=0.4)
            fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)',
                               font=dict(family='Inter', color='#e8e8e8'),
                               legend=dict(bgcolor='rgba(0,0,0,0)'),
                               margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig2, use_container_width=True)

    if not emoji_df.empty:
        sec("Emoji table")
        st.dataframe(emoji_df.style.background_gradient(cmap='Greens', subset=['count']),
                     use_container_width=True)

    sec("Most shared domains")
    if not link_df.empty:
        fig3 = px.bar(link_df, x='count', y='domain', orientation='h',
                      color='count', color_continuous_scale=ACCENT_SCALE,
                      labels={'count':'Times shared','domain':'Domain'})
        fig3.update_layout(**L(showlegend=False, coloraxis_showscale=False,
                               yaxis=dict(autorange='reversed', gridcolor='#272727')))
        st.plotly_chart(fig3, use_container_width=True)
        st.dataframe(link_df, use_container_width=True)
    else:
        st.info("No links found in this chat.")


# ── Insights ──────────────────────────────────────────────────────────────────
with tab6:
    sec("Summary")
    total_days   = (df['only_date'].max() - df['only_date'].min()).days or 1
    msgs_per_day = round(num_messages / total_days, 1)
    peak_hour    = hourly_act.loc[hourly_act['message'].idxmax(), 'hour']
    peak_day     = busy_day.idxmax()
    peak_month   = busy_month.idxmax()

    rows = [
        [("Messages / day",     f"{msgs_per_day} avg"),
         ("Peak hour",          f"{peak_hour}:00 – {peak_hour+1}:00")],
        [("Most active day",    peak_day),
         ("Most active month",  peak_month)],
        [("Longest streak",     f"{max_streak} consecutive days"),
         ("Current streak",     f"{cur_streak} days")],
        [("Total emojis",       fmt(num_emojis)),
         ("Links shared",       fmt(num_links))],
        [("Dominant sentiment", f"{dominant}  ·  {sentiment[dominant]}%"),
         ("Deleted messages",   fmt(num_deleted))],
    ]
    for row in rows:
        c1, c2 = st.columns(2)
        with c1: st.markdown(strip(row[0][0], row[0][1]), unsafe_allow_html=True)
        with c2: st.markdown(strip(row[1][0], row[1][1]), unsafe_allow_html=True)

    sec("Message type breakdown")
    fdf = df.copy() if selected_user == 'Overall' else df[df['user'] == selected_user]
    fig = go.Figure(go.Funnel(
        y=['Total', 'Text', 'Media', 'Deleted'],
        x=[len(fdf),
           fdf[~fdf['is_media'] & ~fdf['is_deleted']].shape[0],
           int(fdf['is_media'].sum()),
           int(fdf['is_deleted'].sum())],
        marker_color=['#25D366','#128C7E','#34B7F1','#FF5252'],
        textinfo='value+percent initial',
        textfont=dict(color='white'),
    ))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(family='Inter', color='#e8e8e8'),
                      margin=dict(l=10, r=10, t=20, b=10), height=320)
    st.plotly_chart(fig, use_container_width=True)

    sec("7-day rolling average")
    roll = daily_tl.copy()
    roll['rolling'] = roll['message'].rolling(7, min_periods=1).mean().round(1)
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=roll['only_date'], y=roll['message'], name='Daily',
                              line=dict(color='rgba(37,211,102,0.25)', width=1),
                              fill='tozeroy', fillcolor='rgba(37,211,102,0.05)'))
    fig2.add_trace(go.Scatter(x=roll['only_date'], y=roll['rolling'], name='7-day avg',
                              line=dict(color='#25D366', width=2.5)))
    fig2.update_layout(**L())
    st.plotly_chart(fig2, use_container_width=True)


# ─── footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class='footer'>
    Made with ❤️ by <span style='color:#25D366;font-weight:600;'>Amit</span>
</div>
""", unsafe_allow_html=True)