# youtube_to_tg
Due to recent political issues, Spotify and Youtube have suspended their subscriptions in Russia. As avid podcast listener, I felt frustrated not able to listen to any eng podcast without having youtube always opened on my phone. So I decided to build this project. It took me about a month of time-to-time work to get it smooth. (Important to note, I didn't get deep into youtube's policy on that, so I keep my channel anonymous here)

It gets link to youtube playlist, extracts .mp3 and uploads to your channel of choice

- To start you need to log in Telegram API with your phone number (https://core.telegram.org/#getting-started) 
- With your api_key and api_hash, initialize Pyrogram session (https://docs.pyrogram.org/intro/quickstart) 
- Then pass path/to/folder where needed, link to your Telegram public channel and link to playlist 
- The information about all processes is stored in podcast_data.csv (mine is not empty as an example) 
- A little stats are done in stats.py just for fun

NOTE:
 - if video is short and getting processed fast, Youtube tends to temporarily block your IP
 - somewhy thumbs are not shown on lock screen (iOS)
 - raises error on 2 particular videos (KeyError: streamingData), seems like those are age-restricted and Youtube requires auth
 
That's how it looks


![image](https://user-images.githubusercontent.com/114425094/192600205-d83dd84e-c61a-4a7f-aa07-8a92dd9baacb.png)


Requirments:
- Python >3.8
- Python packages: pytube, pyrogram (with tgcrypto)
