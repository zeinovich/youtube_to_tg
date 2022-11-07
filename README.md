# youtube_to_tg
I'm building a bot that downloads Youtube videos with some extra functionality.
1) Choose video or audio only
2) Choose video or audio codec if you need (e.g. sound producers may need it)
3) Choose video quality from a list of available
4) Download files up to 1.5Gb with use of agent

*Features 2,3,4 are still in development 
- The information about all processes is stored in postgresql database 
- Some stats is done in stats.py just for fun
- It near future bot will be deployed on server (with help of my fellow admin)

NOTE:
 - if video is short and getting processed fast, Youtube tends to temporarily block IP
 - somewhy thumbs are not shown on lock screen (iOS)
 - raises error on 2 particular videos (KeyError: streamingData), probably because those are age-restricted and require oauth
 
That's how it looks


![image](https://user-images.githubusercontent.com/114425094/192600205-d83dd84e-c61a-4a7f-aa07-8a92dd9baacb.png)


Requirments:
- Python >3.8
- Python packages: pytube, pyrogram (with tgcrypto), telebot, psycopg2
