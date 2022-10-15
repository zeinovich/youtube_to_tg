from pytube import YouTube, Playlist
import os, time, sys
from pathlib import Path
import functools
from pyrogram import Client
import pandas as pd
import requests
from config import session, api_id, api_hash, channel_name, playlist_links, path

#counter decorator
class counter:
    def __init__(self, func):
        self.func = func
        self.num_of_rep = 0

    def __call__(self, *args, **kwargs):
        self.num_of_rep += 1
        if self.func.__name__ == 'download_link':
            print(f'Video #{self.num_of_rep}')
        elif self.func.__name__ == 'get_audio':
            print(f'Audio #{self.num_of_rep}')
        return(self.func(*args, **kwargs))
    
def timing_wrapper(func):
    @functools.wraps(func)
    def timing(*args, **kwargs):
        start = time.perf_counter()
        print('--------------')
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f'[INFO] {func.__name__} executed in {(end - start):.3f}s')
        print('--------------\n')
        return result
    return timing

def get_urls(self) -> list:
    urls = []
    for playlist in self:
        pl_urls = Playlist(playlist)
        urls.extend(iter(pl_urls))
    return urls

def to_database(link, database: pd.DataFrame) -> pd.DataFrame:
    try:
        you_video = YouTube(link)

    except Exception:
        print(f"[ERROR] Link #{links.index(link)+1} has an error in it")

    video_id = you_video.video_id
    if video_id not in database.index:
        title = ''.join(ch for ch in you_video.title if ch.isalnum() or ch in [' ','-',',',';',':','#'])
        performer = you_video.author
        database.loc[video_id, 'title'] = title
        database.loc[video_id, 'author'] = performer
        database.loc[video_id, 'thumb'] = you_video.thumbnail_url   
        database.loc[video_id, 'duration'] = you_video.length
        database.loc[video_id, 'audio'] = False
        database.loc[video_id, 'audio_path'] = None
        database.loc[video_id, 'sent'] = False

    return database      
    
@counter
@timing_wrapper
def download_link(video_id, database: pd.DataFrame) -> None:
    link = f'https://www.youtube.com/watch?v={video_id}'
    try:
        you_video = YouTube(link)

    except Exception:
        print(f"[ERROR] Link #{links.index(link) + 1} has an error in it")

    if not database.loc[video_id, 'audio']:
        title = database.loc[video_id, "title"]
        print(f'    Downloading: {title}')
        you_download = you_video.streams.filter(only_audio=True).first()
        print(f'    {you_download.filesize/1024/1024:.0f} Mb')
        try:
            you_download.download(f'{path}/audio', filename=f'{title}.mp3')
            database.loc[video_id, 'audio_path'] = f'{path}/audio/{title}.mp3'
            database.loc[video_id, 'duration'] = you_video.length
            database.loc[video_id, 'thumb'] = you_video.thumbnail_url
            sys.stdout.write("\033[K")
            print('    Downloaded ')
        except Exception as e:
            print(f'[ERROR] Exception raised while downloading {title}\n {e}')
    else:
        print('    Already downloaded')

def download_thumb(video_id, database: pd.DataFrame) -> None:
    url = database.loc[video_id, 'thumb']
    thumb = requests.get(url, allow_redirects=True)
    f = f'{path}/thumbnails/{video_id}.png'
    open(f, 'wb').write(thumb.content)
    database.loc[video_id, 'thumb'] = f

def tg_upload(video_id, database: pd.DataFrame) -> None:
    print('    Uploading to telegram channel')

    title = database.loc[video_id, 'title']
    path = database.loc[video_id, 'audio_path']
    performer = database.loc[video_id, 'author']
    duration = database.loc[video_id, 'duration']
    thumb = database.loc[video_id, 'thumb']

    app.send_audio(f'{channel_name}', path, performer=performer, title=title, duration=duration, thumb=thumb)
    database.loc[video_id, 'sent'] = True

    print('    Successfully')

@timing_wrapper
def main():    
    os.chdir(f'{path}')
    Path('audio').mkdir(exist_ok=True)
    Path('thumbnails').mkdir(exist_ok=True)

    global links 
    links = get_urls(playlist_links)

    with open('podcast_data.csv','r', encoding='utf8') as file:
        database = pd.read_csv(file, index_col=0)

    for link in links:
        database = to_database(link, database)

    global app
    app = Client(f"{session}", api_id=api_id, api_hash=api_hash)
    app.start()

    for video_id in database.index:
        if not database.loc[video_id, 'sent']:
            try:
                download_link(video_id, database)
                download_thumb(video_id, database)
                tg_upload(video_id, database)
            except KeyboardInterrupt:
                print('-------Canceled--------')
            except Exception as e:
                print(f'[ERROR] Exception raised while processing {video_id}\n[ERROR] {e}')
            finally:
                with open('podcast_data.csv','w', encoding='utf8') as file:
                    database.to_csv(file)

    app.stop()

if __name__ == '__main__':
    main()