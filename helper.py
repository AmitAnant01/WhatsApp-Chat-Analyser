from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import numpy as np
import emoji
from urlextract import URLExtract
import re

extract = URLExtract()

STOP_WORDS = set([
    'the','a','an','and','or','but','in','on','at','to','for','of','with',
    'is','it','this','that','was','are','be','have','had','has','he','she',
    'they','we','you','i','my','your','our','their','its','will','would',
    'could','should','do','did','does','not','no','so','if','as','by',
    'from','up','about','into','than','then','there','when','where','who',
    'which','what','how','all','been','were','him','her','his','them','me',
    'us','very','just','more','also','can','get','got','let','ll','re','ve',
    'don','t','s','m','media','omitted','null','message','deleted','ok',
    'okay','yes','yeah','yep','yup','nope','hi','hello','hey','lol','haha',
    'hehe','hmm','oh','ah','uh','um','like','know','think','good','well',
    'right','sure','see','come','go','time','day','now','one',
])


# ── STATS ─────────────────────────────────────────────────────────────────────

def fetch_stats(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    num_messages = df.shape[0]
    num_words    = sum(len(m.split()) for m in df['message'])
    num_media    = df['is_media'].sum()
    num_deleted  = df['is_deleted'].sum()
    num_links    = sum(len(extract.find_urls(m)) for m in df['message'])
    num_emojis   = sum(
        len([c for c in m if c in emoji.EMOJI_DATA]) for m in df['message']
    )
    avg_len   = round(df['msg_length'].mean(), 1) if 'msg_length' in df.columns else 0
    avg_words = round(df['word_count'].mean(), 1) if 'word_count' in df.columns else 0

    return num_messages, num_words, num_media, num_links, num_emojis, num_deleted, avg_len, avg_words


# ── TIMELINES ─────────────────────────────────────────────────────────────────

def monthly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    tl = df.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
    tl['time'] = tl['month'].str[:3] + " " + tl['year'].astype(str)
    return tl


def daily_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    return df.groupby('only_date').count()['message'].reset_index()


def quarterly_timeline(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    q = df.groupby(['year', 'quarter']).count()['message'].reset_index()
    q['label'] = "Q" + q['quarter'].astype(str) + " " + q['year'].astype(str)
    return q


def yearly_activity(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    return df.groupby('year').count()['message'].reset_index()


# ── ACTIVITY MAPS ─────────────────────────────────────────────────────────────

def week_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    return df['day_name'].value_counts().reindex(order, fill_value=0)


def month_activity_map(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    order = ['January','February','March','April','May','June',
             'July','August','September','October','November','December']
    return df['month'].value_counts().reindex(order, fill_value=0)


def activity_heatmap(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    day_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    heatmap = df.pivot_table(
        index='day_name', columns='period', values='message', aggfunc='count'
    ).fillna(0)
    heatmap = heatmap.reindex([d for d in day_order if d in heatmap.index])
    return heatmap


def hourly_activity(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    return df.groupby('hour').count()['message'].reset_index()


# ── USER ANALYSIS ─────────────────────────────────────────────────────────────

def most_busy_users(df):
    x = df['user'].value_counts().head(10)
    pct = round((df['user'].value_counts() / df.shape[0]) * 100, 2).reset_index()
    pct.columns = ['name', 'percent']
    return x, pct


def user_activity_over_time(df):
    users = (
        df[df['user'] != 'group_notification']['user']
        .value_counts().head(5).index.tolist()
    )
    result = {}
    for user in users:
        udf = df[df['user'] == user]
        monthly = udf.groupby(['year', 'month_num', 'month']).count()['message'].reset_index()
        monthly['time'] = monthly['month'].str[:3] + " " + monthly['year'].astype(str)
        result[user] = monthly
    return result


def user_message_length(df):
    df2 = df[df['user'] != 'group_notification'].copy()
    return df2.groupby('user')['msg_length'].mean().sort_values(ascending=False).head(10)


def response_time_analysis(df):
    df2 = df[df['user'] != 'group_notification'].sort_values('date').copy()
    df2['prev_date'] = df2['date'].shift(1)
    df2['prev_user'] = df2['user'].shift(1)
    df2['gap_min']   = (df2['date'] - df2['prev_date']).dt.total_seconds() / 60

    responses = df2[
        (df2['user'] != df2['prev_user']) &
        (df2['gap_min'] < 60) &
        (df2['gap_min'] > 0)
    ]
    if responses.empty:
        return pd.DataFrame(columns=['user', 'avg_response_min'])

    result = responses.groupby('user')['gap_min'].mean().round(1).reset_index()
    result.columns = ['user', 'avg_response_min']
    return result.sort_values('avg_response_min').head(10)


def emoji_per_user(df):
    df2 = df[df['user'] != 'group_notification'].copy()
    result = {}
    for user in df2['user'].unique():
        msgs = df2[df2['user'] == user]['message']
        result[user] = sum(len([c for c in m if c in emoji.EMOJI_DATA]) for m in msgs)
    return pd.Series(result).sort_values(ascending=False).head(10)


# ── WORD / TEXT ANALYSIS ──────────────────────────────────────────────────────

def _clean_messages(df):
    return df[~df['message'].str.contains(
        '<Media omitted>|This message was deleted', na=False
    )]


def create_wordcloud(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    df = _clean_messages(df)
    text = df['message'].str.cat(sep=" ")
    words = [w for w in text.lower().split() if w not in STOP_WORDS and len(w) > 2]
    clean_text = " ".join(words) or "no text messages"

    wc = WordCloud(
        width=800, height=400,
        min_font_size=10,
        background_color='#111111',
        colormap='Greens',
        max_words=200,
        collocations=False,
    )
    return wc.generate(clean_text)


def most_common_words(selected_user, df, n=20):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    df = _clean_messages(df)
    words = [
        w for m in df['message']
        for w in m.lower().split()
        if w not in STOP_WORDS and len(w) > 2 and w.isalpha()
    ]
    return pd.DataFrame(Counter(words).most_common(n), columns=['word', 'count'])


def bigram_analysis(selected_user, df, n=15):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    df = _clean_messages(df)
    bigrams = []
    for msg in df['message']:
        words = [w for w in msg.lower().split()
                 if w not in STOP_WORDS and len(w) > 2 and w.isalpha()]
        bigrams.extend(f"{words[i]} {words[i+1]}" for i in range(len(words) - 1))
    return pd.DataFrame(Counter(bigrams).most_common(n), columns=['bigram', 'count'])


def sentiment_basic(selected_user, df):
    positive_words = {
        'good','great','love','awesome','amazing','wonderful','happy','excellent',
        'fantastic','nice','best','thanks','thank','beautiful','perfect','brilliant',
        'superb','congratulations','congrats','well','yay','wow','incredible','blessed'
    }
    negative_words = {
        'bad','sad','hate','terrible','awful','horrible','worst','poor','wrong',
        'failed','fail','sorry','angry','upset','unfortunately','problem','issue',
        'error','broken','never','miss','cry','tired','boring','useless','annoying'
    }
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]

    pos = neg = neu = 0
    for msg in df['message']:
        words = set(msg.lower().split())
        p = len(words & positive_words)
        n = len(words & negative_words)
        if p > n:   pos += 1
        elif n > p: neg += 1
        else:       neu += 1

    total = pos + neg + neu or 1
    return {
        'Positive': round(pos / total * 100, 1),
        'Negative': round(neg / total * 100, 1),
        'Neutral':  round(neu / total * 100, 1),
    }


# ── EMOJI & LINK ANALYSIS ─────────────────────────────────────────────────────

def emoji_helper(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    emojis = [c for m in df['message'] for c in m if c in emoji.EMOJI_DATA]
    if not emojis:
        return pd.DataFrame(columns=['emoji', 'count'])
    return pd.DataFrame(Counter(emojis).most_common(20), columns=['emoji', 'count'])


def link_analysis(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    domains = []
    for msg in df['message']:
        for url in extract.find_urls(msg):
            try:
                domain = re.sub(r'^www\.', '', url.split('/')[2])
                domains.append(domain)
            except Exception:
                pass
    if not domains:
        return pd.DataFrame(columns=['domain', 'count'])
    return pd.DataFrame(Counter(domains).most_common(10), columns=['domain', 'count'])


# ── STREAK / PATTERN ──────────────────────────────────────────────────────────

def chat_streak(df):
    dates = sorted(df['only_date'].unique())
    if not dates:
        return 0, 0
    max_streak = cur_streak = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            cur_streak += 1
            max_streak = max(max_streak, cur_streak)
        else:
            cur_streak = 1
    return max_streak, cur_streak


def most_active_date(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    counts = df.groupby('only_date').count()['message']
    if counts.empty:
        return None, 0
    return counts.idxmax(), counts.max()


# ── ADVANCED: MESSAGE LENGTH DISTRIBUTION ─────────────────────────────────────

def msg_length_distribution(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    df = _clean_messages(df)
    bins = [0, 10, 30, 60, 100, 200, 500, 99999]
    labels = ['1-10', '11-30', '31-60', '61-100', '101-200', '201-500', '500+']
    df = df.copy()
    df['length_bucket'] = pd.cut(df['msg_length'], bins=bins, labels=labels)
    return df['length_bucket'].value_counts().reindex(labels).fillna(0).reset_index()


# ── ADVANCED: FIRST MESSAGE OF DAY ────────────────────────────────────────────

def first_message_of_day(df):
    df2 = df[df['user'] != 'group_notification'].copy()
    df2 = df2.sort_values('date')
    first = df2.groupby('only_date').first().reset_index()
    return first['user'].value_counts().head(10).reset_index().rename(
        columns={'index': 'user', 'user': 'count'}
    )


# ── ADVANCED: WEEKLY TREND (last 12 weeks) ────────────────────────────────────

def weekly_trend(selected_user, df):
    if selected_user != "Overall":
        df = df[df['user'] == selected_user]
    df2 = df.copy()
    df2['week_start'] = df2['date'].dt.to_period('W').apply(lambda r: r.start_time.date())
    weekly = df2.groupby('week_start').count()['message'].reset_index()
    weekly.columns = ['week_start', 'count']
    return weekly.tail(16)