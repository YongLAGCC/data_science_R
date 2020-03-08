import requests, bs4
import pandas as pd
from datetime import datetime

df = pd.DataFrame()
total = ["./Data/CNBC/tesla, OR roadster, OR elon, OR musk, OR teslamodel from_CNBC since_2016-11-10 until_2017-11-10 - Twitter Search",\
          "./Data/CNBC/tesla, OR roadster, OR elon, OR musk, OR teslamodel from_CNBC since_2017-11-10 until_2018-03-11 - Twitter Search",\
          "./Data/CNBC/tesla, OR roadster, OR elon, OR musk, OR teslamodel from_CNBC since_2018-03-11 until_2018-06-11 - Twitter Search",\
          "./Data/CNBC/tesla, OR roadster, OR elon, OR musk, OR teslamodel from_CNBC since_2018-06-11 until_2018-09-11 - Twitter Search",\
          "./Data/CNBC/tesla, OR roadster, OR elon, OR musk, OR teslamodel from_CNBC since_2018-09-11 until_2018-11-11 - Twitter Search"]
for fname in total:
    new_df = pd.DataFrame()
    soup = bs4.BeautifulSoup(open(fname+".html", "rb"), 'html.parser')
    new_df["tweet"] = soup.select('.stream-item')
    df = df.append(new_df, ignore_index=True)

df.drop_duplicates(inplace=True)

def get_time(r):
    try:
        res = r["tweet"].select('._timestamp')[0].text
        if not " " in res:
            res = None
        if len(res.split(" ")[1]) != 4:
            res += " 2018"
    except:
        return None
    return res

def get_text(r):
    try:
        li = r["tweet"].select('.tweet-text')
        res = [item.text for item in li]
        res = "\n".join(res)
    except:
        return None
    return res

def get_counts(r):
    try:
        li = r.select('.ProfileTweet-actionCountForPresentation')
        res = [item.text if item.text != '' else 0 for item in li]
        # bug approach that I can't fix...
        # for i in [0, 1, -1]:
        #     res = []
        #     if li[i] == "" or li[i] == " ":
        #         res.append(0)
        #     else:
        #         res.append(li[i].text)
        return res[0], res[1], res[-1]
    except Exception as ex:
        print(ex)
        return [None]*3

df['time'] = df.apply(get_time, axis=1)
filtered_df = df[df['time'].isnull() == 0]
filtered_df['time'] = pd.to_datetime(filtered_df['time']).dt.date
filtered_df.sort_values(by=['time'], inplace=True)

filtered_df["text"] = df.apply(get_text, axis=1)
filtered_df["replies"], filtered_df["retweets"], filtered_df["likes"] = zip(*filtered_df["tweet"].map(get_counts))

counts = ["replies", "retweets", "retweets"]

def value_to_float(x):
    if type(x) == float or type(x) == int:
        return x
    if 'K' in x:
        if len(x) > 1:
            return float(x.replace('K', '')) * 1000
        return 1000.0
    if 'M' in x:
        if len(x) > 1:
            return float(x.replace('M', '')) * 1000000
        return 1000000.0
    if 'B' in x:
        return float(x.replace('B', '')) * 1000000000
    return x

# for i in counts:
#     filtered_df[i] = (filtered_df[i].replace(r'[KM]+$', '', regex=True).astype(float) * \
#         filtered_df[i].str.extract(r'[\d\.]+([KM]+)', expand=False)
#         .fillna(1)
#         .replace(['K','M'], [10**3, 10**6]).astype(int))
# filtered_df[counts] = filtered_df[counts].astype(int)

# filtered_df.drop(columns=['tweet'], inplace=True)
# filtered_df.to_csv(fname+".csv", index=False)

# fname = "./Data/(_) @elonmusk @Tesla - Twitter Search"
# fname = "./Data/Elon Musk (@elonmusk) _ Twitter"