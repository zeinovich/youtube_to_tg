from pytube import YouTube, Playlist
import os, time, sys
import moviepy.editor
from pathlib import Path
import functools
from pyrogram import Client
import json
import requests
from config import api_id, api_hash, channel_name, playlist_links, path

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
        print(f'    {func.__name__} executed in {(end - start):.3f}s')
        print('--------------\n')
        return result
    return timing

def get_urls(self) -> list:
    urls = []
    for playlist in self:
        pl_urls = Playlist(playlist)
        urls.extend(iter(pl_urls))
    return urls

def to_database(link, database: dict) -> dict:
    try:
        you_video = YouTube(link)

    except Exception:
        print(f"[ERROR] Link #{links.index(link)+1} has an error in it")

    title = ''.join(ch for ch in you_video.title if ch.isalnum() or ch in [' ','-',',',';',':','#'])
    performer = you_video.author
    if title not in database.keys():
        database[title] = {'Performer': performer, 'Link': link, 'Path': '', 
                            'Video': False, 'Thumb': '', 'Audio': False, 'Duration': 0,
                            'Audio Path': '', 'Sent': False, 'Processed': False} 
    return database      
    
@counter
@timing_wrapper
def download_link(title, database: dict) -> None:
    link = database[title]['Link']
    try:
        you_video = YouTube(link)

    except Exception:
        print(f"[ERROR] Link #{links.index(link) + 1} has an error in it")

    if not database[title]['Video']:
        print(f'    Downloading: {title}')
        you_download = you_video.streams.get_highest_resolution()
        print(f'    {you_download.filesize/1024/1024:.2f} Mb')
        try:
            you_download.download(f'{path}/video', filename=f'{title}.mp4')
            database[title]['Video'] = True
            database[title]['Path'] = f'{path}/video/{title}.mp4'
            database[title]['Duration'] = you_video.length
            database[title]['Thumb'] = you_video.thumbnail_url
            sys.stdout.write("\033[K")
            print('    Downloaded ')
        except Exception as e:
            print(f'[ERROR] Exception raised while downloading {title}\n {e}')
    else:
        print('    Already downloaded')

def get_audio(title, database) -> None:
    f = Path(database[title]['Path'])
    ext = f.suffix
    if ext == '.mp4':
        f = str(f)
        if not database[title]['Audio']:
            video = moviepy.editor.VideoFileClip(f)
            audio = video.audio
            audio_path = f'{path}/audio/{title}.mp3'
            audio.write_audiofile(audio_path)
            database[title]['Audio'] = True
            database[title]['Audio Path'] = audio_path
            video.close()
            audio.close()
    else:
        print("    Not a video")

def download_thumb(title, database):
    url = database[title]['Thumb']
    thumb = requests.get(url, allow_redirects=True)
    f = f'{path}/thumbnails/{title}.png'
    open(f, 'wb').write(thumb.content)
    database[title]['Thumb'] = f

def tg_upload(title, database: dict) -> None:
    if not database[title]['Sent']:
        print('    Uploading to telegram channel')
        path = database[title]['Audio Path']
        performer = database[title]['Performer']
        duration = database[title]['Duration']
        thumb = database[title]['Thumb']
        app.send_audio(f'{channel_name}', path, performer=performer, title=title, duration=duration, thumb=thumb)
        database[title]['Sent'] = True
        print('    Successfully')
    else:
        print('MP3 in tg')

@timing_wrapper
def main():    
    os.chdir(f'{path}')
    Path('video').mkdir(exist_ok=True)
    Path('audio').mkdir(exist_ok=True)
    Path('thumbnails').mkdir(exist_ok=True)

    global links 
    links = get_urls(playlist_links)

    with open('podcast_data.json','r') as file:
        database = json.load(file)

    for link in links:
        database = to_database(link, database)

    global app
    app = Client("tg_uploader", api_id=api_id, api_hash=api_hash)
    app.start()

    for title in database.keys():
        if not database[title]['Processed']:
            try:
                download_link(title, database)
                download_thumb(title, database)
                get_audio(title, database)
                tg_upload(title, database)
                database[title]['Processed'] = True
            except KeyboardInterrupt:
                print('-------Canceled--------')
            except Exception as e:
                print(f'[ERROR] Exception raised while processing {title}\n{e}')
            finally:
                with open('podcast_data.json','w') as file:
                    json.dump(database, file, indent=4)

    app.stop()

if __name__ == '__main__':
    main()