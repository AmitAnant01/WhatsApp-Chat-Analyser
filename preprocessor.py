import re
import pandas as pd


def preprocess(data):
    patterns = [
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s',
        r'\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s[APap][Mm]\s-\s',
        r'\[\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}:\d{2}\s[APap][Mm]\]\s',
        r'\d{1,2}-\d{1,2}-\d{2,4},\s\d{1,2}:\d{2}\s-\s',
    ]

    matched_pattern = None
    for p in patterns:
        if re.findall(p, data):
            matched_pattern = p
            break

    if not matched_pattern:
        matched_pattern = patterns[0]

    messages = re.split(matched_pattern, data)[1:]
    dates    = re.findall(matched_pattern, data)
    dates    = [d.strip().strip('[]').strip(' -').strip() for d in dates]

    df = pd.DataFrame({'user_message': messages, 'message_date': dates})

    date_formats = [
        '%d/%m/%Y, %H:%M',
        '%d/%m/%y, %H:%M',
        '%m/%d/%Y, %H:%M',
        '%m/%d/%y, %H:%M',
        '%d/%m/%Y, %I:%M %p',
        '%d/%m/%y, %I:%M %p',
        '%d/%m/%Y, %H:%M:%S %p',
        '%d-%m-%Y, %H:%M',
        '%d-%m-%y, %H:%M',
    ]

    parsed = False
    for fmt in date_formats:
        try:
            df['message_date'] = pd.to_datetime(df['message_date'], format=fmt, errors='raise')
            parsed = True
            break
        except Exception:
            continue

    if not parsed:
        df['message_date'] = pd.to_datetime(
            df['message_date'], infer_datetime_format=True, errors='coerce'
        )

    df.rename(columns={'message_date': 'date'}, inplace=True)

    users, messages_list = [], []
    for message in df['user_message']:
        entry = re.split(r'([\w\W]+?):\s', message)
        if entry[1:]:
            users.append(entry[1])
            messages_list.append(" ".join(entry[2:]))
        else:
            users.append('group_notification')
            messages_list.append(entry[0])

    df['user']    = users
    df['message'] = messages_list
    df.drop(columns=['user_message'], inplace=True)
    df.dropna(subset=['date'], inplace=True)

    df['only_date'] = df['date'].dt.date
    df['year']      = df['date'].dt.year
    df['month_num'] = df['date'].dt.month
    df['month']     = df['date'].dt.month_name()
    df['day']       = df['date'].dt.day
    df['day_name']  = df['date'].dt.day_name()
    df['hour']      = df['date'].dt.hour
    df['minute']    = df['date'].dt.minute
    df['week']      = df['date'].dt.isocalendar().week.astype(int)
    df['quarter']   = df['date'].dt.quarter

    period = []
    for hour in df['hour']:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-01")
        else:
            period.append(f"{str(hour).zfill(2)}-{str(hour + 1).zfill(2)}")
    df['period'] = period

    df['msg_length'] = df['message'].apply(len)
    df['word_count'] = df['message'].apply(lambda x: len(x.split()))
    df['is_media']   = df['message'].str.contains('<Media omitted>', na=False)
    df['is_deleted'] = df['message'].str.contains(
        'This message was deleted|message was deleted', na=False
    )

    return df