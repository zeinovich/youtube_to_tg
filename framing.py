#%%
import pandas as pd
import json


with open('podcast_data.json','r') as file:
    data = json.load(file)

frame = pd.DataFrame(data).T
frame.index.name = 'Title'
frame = frame.reset_index()
frame = frame.set_index(['Performer', 'Title'])
frame = frame.sort_index()
print(frame)
#%%