import os, sys
from pathlib import Path
from datetime import datetime
import requests
from cursor_module import Cursor
from pytube import YouTube, Playlist
import psycopg2
import telebot

def get_urls(self) -> list:
    urls = []
    for playlist in self:
        pl_urls = Playlist(playlist)
        urls.extend(iter(pl_urls))
    return urls

def to_database(video_id) -> None:
    link = f'https://www.youtube.com/watch?v={video_id}'
    try:
        you_video = YouTube(link)

    except Exception:
        print(f"[ERROR] {datetime.now()} -> Link #{video_ids.index(video_id) + 1} has an error in it")

    video_id = you_video.video_id
    check_exists = curs.check_exists('videos', video_id)
    if not check_exists:
        author = you_video.author
        title = you_video.title
        duration = you_video.length
        curs.insert(columns=['video_id', 'author', 'title', 'duration'], 
                    values=[f"'{video_id}'", f"'{author}'", f"'{title}'", f"'{duration}'"], 
                    table='videos')
    
def download_link(video_id) -> None:
    link = f'https://www.youtube.com/watch?v={video_id}'
    try:
        you_video = YouTube(link)

    except Exception:
        print(f"[ERROR] {datetime.now()} -> Link #{video_ids.index(link) + 1} has an error in it")

    title = curs.select(columns=['title'],
                        table='videos',
                        where=f"video_id = '{video_id}'")[0][0]

    print(f'[INFO] {datetime.now()} -> Downloading: {title}')
    bot.send_message(chat_id, f'Downloading: {title}')
    you_download = you_video.streams.filter(only_audio=True, audio_codec="opus").first()
    f_size = you_download.filesize/1024/1024
    print(f'[INFO] {datetime.now()} -> {f_size:.0f} Mb')
    try:
        you_download.download(f'{PATH}/audio', filename=f'{video_id}.mp3')
        download_thumb(video_id)
        sys.stdout.write("\033[K")
        print(f'[INFO] {datetime.now()} -> Downloaded ')
    except Exception as e:
        print(f'[ERROR] {datetime.now()} -> Exception raised while downloading {title}\n {e}')


def download_thumb(video_id) -> None:
    url = f'https://i.ytimg.com/vi/{video_id}/sddefault.jpg'
    thumb = requests.get(url, allow_redirects=True)
    f = f'{PATH}/thumbnails/{video_id}.png'

    with open(f, 'wb') as file:
        file.write(thumb.content)

def tg_upload(video_id) -> None:
    print(f'[INFO] {datetime.now()} -> Uploading to telegram')
    audio_path = f'{PATH}/audio/{video_id}.mp3'
    thumb_path = f'{PATH}/thumbnails/{video_id}.png'
    title, author, duration = curs.select(
    ['title', 'author', 'duration'], 
    table='videos', where=f"video_id = '{video_id}'")[0]
    print(f'[INFO] {datetime.now()} -> Uploading: {title}')
    bot.send_message(chat_id, f'Uploading: {title}')
    with open(audio_path, 'rb') as audio, open(thumb_path, 'rb') as thumb:
        bot.send_audio(chat_id=chat_id, audio=audio, title=title, 
                        performer=author, duration=duration, 
                        thumb=thumb)

    curs.insert(columns=['video_id', 'chat_id', 'date'], 
                values=[f"'{video_id}'", f"'{chat_id}'", f"'{datetime.now()}'"], 
                table='users')
    print(f'[INFO] {datetime.now()} -> Uploaded')

def main():
    global PATH
    PATH = os.getenv('PATH')
    API_KEY = os.getenv('API_KEY')
    PASSWORD = os.getenv('PASSWORD')

    os.chdir(PATH)
    Path('audio').mkdir(exist_ok=True)
    Path('thumbnails').mkdir(exist_ok=True)

    global bot
    api_key = API_KEY
    bot = telebot.TeleBot(api_key)

    conn = psycopg2.connect(database='youtube', user='postgres', password=PASSWORD, host='localhost', port='5432')
    conn.autocommit = True
    global curs
    curs = Cursor(conn)
    try:
        @bot.message_handler()
        def process_msg(message) -> None:    
            if 'watch?v=' in message.text:
                links = [message.text]
                bot.reply_to(message, "You've sent a video link")
            elif 'playlist?list=' in message.text:
                links = get_urls([message.text])
                bot.reply_to(message, "You've sent a playlist link")
            else:
                bot.reply_to(message, 'Invalid link')
                return
            
            global chat_id
            chat_id = message.chat.id

            global video_ids
            video_ids = [link.split('watch?v=')[1] for link in links]
            
            # video_id, title, author, description, duration, thumb, audio_path
            for video_id in video_ids:
                to_database(video_id)
                download_link(video_id)
                tg_upload(video_id)

        bot.polling(none_stop=True)
        
    except KeyboardInterrupt:
        print(f'[STOP] {datetime.now()} -> KeyboardInterrupt')
        curs.close()
        conn.close()
    
if __name__ == '__main__':
    main()