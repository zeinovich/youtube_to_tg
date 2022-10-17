import os, sys
from pathlib import Path
from datetime import date
import requests
from config import path
from cursor_module import Cursor
from pytube import YouTube, Playlist
from pyrogram import Client
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
        print(f"[ERROR] Link #{video_ids.index(video_id) + 1} has an error in it")

    video_id = you_video.video_id
    check_exists = curs.check_exists('videos', video_id)
    if not check_exists:
        author = you_video.author
        title = ''.join(ch for ch in you_video.title if ch.isalnum() or ch in [' ','-',',',';',':','#'])
        description = you_video.description
        duration = you_video.length
        curs.insert(columns=['video_id', 'author', 'title', 'duration'], 
                    values=[f"'{video_id}'", f"'{author}'", f"'{title}'", f"'{duration}'"], 
                    table='videos')
    
def download_link(video_id) -> None:
    link = f'https://www.youtube.com/watch?v={video_id}'
    try:
        you_video = YouTube(link)

    except Exception:
        print(f"[ERROR] Link #{video_ids.index(link) + 1} has an error in it")

    title = curs.select(columns=['title'],
                        table='videos',
                        where=f"video_id = '{video_id}'")[0][0]

    print(f'    Downloading: {title}')
    you_download = you_video.streams.filter(only_audio=True).first()
    f_size = you_download.filesize/1024/1024
    print(f'    {f_size:.0f} Mb')
    try:
        you_download.download(f'{path}/audio', filename=f'{title}.mp3')
        audio_path = f'{path}/audio/{title}.mp3'
        thumb = you_video.thumbnail_url
        download_thumb(thumb, video_id)
        sys.stdout.write("\033[K")
        print('    Downloaded ')
        curs.update(table='videos', 
                    set=f"audio_path = '{audio_path}', thumb = '{thumb}'", 
                    where=f"video_id = '{video_id}'")
    except Exception as e:
        print(f'[ERROR] Exception raised while downloading {title}\n {e}')


def download_thumb(url, video_id) -> None:
    thumb = requests.get(url, allow_redirects=True)
    f = f'{path}/thumbnails/{video_id}.png'

    with open(f, 'wb') as file:
        file.write(thumb.content)

def tg_upload(video_id, chat_id) -> None:
    print('    Uploading to telegram channel')

    title, author, duration, thumb, audio_path = curs.select(
    ['title, author, duration, thumb, audio_path'], 
    table='videos', where=f"video_id = '{video_id}'")[0]

    bot.send_audio(chat_id=chat_id, audio = open(audio_path, 'rb'), performer=author, title=title, duration=duration, thumb=thumb)
    curs.insert(columns=['video_id', 'chat_id', 'date'], 
                values=[f"'{video_id}'", f"'{chat_id}'", f"'{date.today()}'"], 
                table='users')
    print('    Successfully')

def main():
    os.chdir(f'{path}')
    Path('audio').mkdir(exist_ok=True)
    Path('thumbnails').mkdir(exist_ok=True)

    global bot
    api_key = '##'
    bot = telebot.TeleBot(api_key)

    conn = psycopg2.connect(database='youtube', user='postgres', password='##', host='localhost', port='5432')
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

            global video_ids
            video_ids = [link.split('watch?v=')[1] for link in links]
            
            # video_id, title, author, description, duration, thumb, audio_path
            for video_id in video_ids:
                audio_path = curs.select(['audio_path'], 'videos', f"video_id = '{video_id}'")[0]
                print(audio_path)
                if not audio_path:
                    to_database(video_id)
                    bot.send_message(message.chat.id, 'Video added to database')
                    download_link(video_id)
                    bot.send_message(message.chat.id, 'Video downloaded')
                
                chat_id = message.chat.id
                bot.send_message(chat_id, 'Uploading...')
                tg_upload(video_id, chat_id)

        bot.polling(none_stop=True)
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        curs.close()
        conn.close()
    
if __name__ == '__main__':
    main()