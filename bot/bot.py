import os
from pathlib import Path
from datetime import datetime
from cursor import Cursor
from pytube import Playlist
from video import Video
#from agent import Agent
from dotenv import load_dotenv
import psycopg2
import telebot

def get_urls(self) -> list:
    urls = []
    for playlist in self:
        pl_urls = Playlist(playlist)
        urls.extend(iter(pl_urls))
    return urls

def get_ids(message) -> list:
    if 'watch?v=' in message.text:
        links = [message.text.strip()]
        bot.reply_to(message, "You've sent a video link")
        return [link.split('watch?v=')[1] for link in links]

    elif 'playlist?list=' in message.text:
        links = get_urls([message.text.strip()])
        bot.reply_to(message, "You've sent a playlist link")
        return [link.split('watch?v=')[1] for link in links]
    else:
        bot.reply_to(message, 'Invalid link')
        return

def process_audio(message, video_ids) -> None:
    chat_id = message.chat.id
    for video_id in video_ids:
        video = Video(video_id)
        video.add_to_db(curs)
        video.download()
        video.download_thumb()
        #file_id = agent.upload(video, '@dump_youtube', PATH)
        #video.upload(bot, chat_id, file_id)
        video.upload_beta(bot, chat_id, curs)

def process_video(message, video_ids) -> None:
    chat_id = message.chat.id          
    for video_id in video_ids:
        video = Video(video_id, only_audio=False)
        video.add_to_db(curs)
        video.download()
        video.download_thumb()
        #file_id = agent.upload(video, '@dump_youtube', PATH)
        #video.upload(bot, chat_id, file_id)
        video.upload_beta(bot, chat_id, curs)

def main():
    global PATH
    PATH = os.getcwd()
    print(f'[INFO] {datetime.now()} -> Working directory: {PATH}')
    load_dotenv()
    API_KEY = os.getenv('API_KEY')
    #API_ID = os.getenv('API_ID')
    #API_HASH = os.getenv('API_HASH')
    #SESSION_NAME = os.getenv('SESSION_NAME')
    
    USER = os.getenv('USER')
    PASSWORD = os.getenv('PASSWORD')
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')

    Path('audios').mkdir(exist_ok=True)
    Path('videos').mkdir(exist_ok=True)
    Path('thumbnails').mkdir(exist_ok=True)

    global bot
    bot = telebot.TeleBot(API_KEY)
    print(f'[INFO] {datetime.now()} -> Bot started')

    #global agent
    #agent = Agent(session_name=SESSION_NAME, api_id=API_ID, api_hash=API_HASH)
    #agent.start()
    #print('Agent started')

    global curs
    conn = psycopg2.connect(database='youtube', user=USER, password=PASSWORD, host=HOST, port=PORT)
    conn.autocommit = True
    curs = Cursor(conn)
    print(f'[INFO] {datetime.now()} -> Connected to database')   
    
    try:
        @bot.message_handler(commands=['start'])
        def start(message):
            bot.send_message(message.chat.id, '/audio - to download audio\n/video - to download video')            

        @bot.message_handler(commands=['audio'])
        def process_msg(message) -> None:
            bot.send_message(message.chat.id, 'Send me a link to the video or playlist')
            @bot.message_handler(content_types=['text'])
            def process_au(message) -> None:
                video_ids = get_ids(message)
                process_audio(message, video_ids)

        @bot.message_handler(commands=['video'])
        def process_msg(message) -> None:
            bot.send_message(message.chat.id, 'Send me a link to the video or playlist')
            @bot.message_handler(content_types=['text'])
            def process_vid(message) -> None:
                video_ids = get_ids(message)
                process_video(message, video_ids)

        bot.polling(non_stop=True)
        
    except Exception as e:
        print(f'[ERROR] {datetime.now()} -> {e.with_traceback(None)}')
        bot.stop_polling()
        #agent.stop()
        curs.close()
        
    except KeyboardInterrupt:
        print(f'[STOP] {datetime.now()} -> KeyboardInterrupt')
        curs.close()
        conn.close()
        #agent.stop()
    
if __name__ == '__main__':
    main()