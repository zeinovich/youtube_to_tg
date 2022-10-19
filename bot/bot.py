import os
from pathlib import Path
from datetime import datetime
from cursor import Cursor
from pytube import Playlist
from video import Video
import psycopg2
import telebot

def get_urls(self) -> list:
    urls = []
    for playlist in self:
        pl_urls = Playlist(playlist)
        urls.extend(iter(pl_urls))
    return urls

def main():
    global PATH
    PATH = os.getenv('PATH')
    API_KEY = os.getenv('API_KEY')
    PASSWORD = os.getenv('PASSWORD')

    os.chdir(PATH)
    Path('audio').mkdir(exist_ok=True)
    Path('thumbnails').mkdir(exist_ok=True)

    global bot
    bot = telebot.TeleBot(API_KEY)

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
                video = Video(video_id)
                video.add_to_db(curs)
                video.download()
                video.upload(bot, chat_id)

        bot.polling(none_stop=True)
        
    except KeyboardInterrupt:
        print(f'[STOP] {datetime.now()} -> KeyboardInterrupt')
        curs.close()
        conn.close()
    
if __name__ == '__main__':
    main()