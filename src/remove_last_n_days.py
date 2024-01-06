import pandas as pd
from datetime import datetime, timedelta

STORED_ITEMS = 'data/stored_posts.csv'
LAST_N_DAYS = 2
posts = pd.read_csv(STORED_ITEMS, index_col=False)
DATE_COL = 'date'
print(posts[DATE_COL])
print(posts['date_added'])
date_in_past = datetime.now().date() - timedelta(days=LAST_N_DAYS)
posts[DATE_COL] = pd.to_datetime(posts[DATE_COL])
minus_last_n_days = posts[posts[DATE_COL].dt.date <= date_in_past]
minus_last_n_days.to_csv(STORED_ITEMS, index=False)
posts[DATE_COL] = pd.to_datetime(posts[DATE_COL])
print("TOTAL ITEMS BEFORE:", len(posts.index))
print("TOTAL ITEMS AFTER:", len(minus_last_n_days.index))