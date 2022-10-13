#%%
import json
import psycopg2
from pytube import YouTube, Playlist
import pandas as pd
import numpy as np

with open('podcast_data.json','r') as file:
    database = json.load(file)
# %%
db = pd.DataFrame(database).T
# %%
db.index.name = 'Title'
# %%
for idx in db.index.tolist():
    video = YouTube(f'https://www.youtube.com/watch?v={idx}')
    db.loc[idx, 'Thumb'] = video.thumbnail_url
    db.loc[idx, 'Duration'] = video.length
    db.loc[idx, 'video_id'] = video.video_id
    db.loc[idx, 'Description'] = video.description
# %%
db = db.reset_index()
# %%
idx = db.pop('video_id')
db.insert(0, 'video_id', idx) 
# %%
db.index = db['video_id']
# %%
desc = db.pop('Description')
db.insert(3, 'Description', desc)
# %%
db.pop('Link')
# %%
db.pop('Path')
db.pop('Audio Path')

# %%
table1 = db[['id', 'Title', 'Performer', 'Description', 'Duration']]
# %%
table2 = db[['id', 'Thumb', 'Audio', 'Sent', 'Processed']]
# %%
from pyrogram import Client
#%%
app = Client('tg_uploader', api_id=19940337, api_hash="b32ab2208f4a50dfb5d9a062b7bc72f9")
app.start()
# %%
msgs = app.get_messages('@zeinovich_podcasts')
# %%
# %%
