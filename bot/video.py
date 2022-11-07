from pytube import YouTube
from cursor import Cursor
from telebot import TeleBot
import os, requests
from datetime import datetime

PATH = os.getcwd()
class Video(YouTube):
    def __init__(self, video_id, only_audio=True):
        super().__init__(f'https://www.youtube.com/watch?v={video_id}')
        self.video_id = video_id
        self.author = self.author
        self.title = self.title
        self.duration = self.length
        self.only_audio = only_audio
    
    def add_to_db(self, curs: Cursor):
        check_exists = curs.check_exists('videos', self.video_id)
        if not check_exists:
            curs.insert(columns=['video_id', 'author', 'title', 'duration'], 
                        values=[f"'{self.video_id}'", f"'{self.author}'", f"'{self.title}'", f"'{self.duration}'"], 
                        table='videos')

    def download(self):
        try:
            if self.only_audio:
                print(f'[INFO] {datetime.now()} -> Downloading: {self.title}')
                au = self.streams.filter(only_audio=True).first()
                print(f'[INFO] {datetime.now()} -> Size = {(au.filesize / (1024 ** 2)):.1f} MB')
                au.download(output_path=f'{PATH}/audios', filename=f'{self.video_id}.mp3',
                            skip_existing=True)
            else:
                vid = self.streams.filter(res='1080p').first()
                print(f'[INFO] {datetime.now()} -> Size = {(vid.filesize / (1024 ** 2)):.1f} MB')
                vid.download(output_path=f'{PATH}/videos', filename=f'{self.video_id}.mp4')
            print(f'[INFO] {datetime.now()} -> Downloading is finished')
        except Exception as e:
            print(e)
            
    def download_thumb(self):
        print(f'[INFO] {datetime.now()} -> Downloading thumbnail')
        with open(f'{PATH}/thumbnails/{self.video_id}.png', 'wb') as f:
            r = requests.get(self.thumbnail_url, allow_redirects=True)
            f.write(r.content)
    
    def upload(self, bot: TeleBot, chat_id: int, curs: Cursor, file_id: str):
        thumb_path = f'{PATH}/thumbnails/{self.video_id}.png'
        if self.only_audio:
            with open(thumb_path, 'rb') as thumb:
                print(f'[INFO] {datetime.now()} -> BOT is uploading to telegram')
                bot.send_audio(chat_id=chat_id, audio=file_id, 
                                title=self.title, duration=self.duration, 
                                performer=self.author, thumb=thumb)
        else:
            with open(thumb_path, 'rb') as thumb:
                print(f'[INFO] {datetime.now()} -> BOT is uploading to telegram')
                bot.send_video(chat_id=chat_id, video=file_id, 
                                title=self.title, duration=self.duration, 
                                performer=self.author, thumb=thumb)
        print(f'[INFO] {datetime.now()} -> Uploading is finished')
        
        curs.insert(columns=['video_id', 'chat_id', 'date', 'only_audio'], 
                    values=[f"'{self.video_id}'", f"'{chat_id}'", f"'{datetime.now()}'", f"'{self.only_audio}'"], 
                    table='users')

    def upload_beta(self, bot: TeleBot, chat_id: int, curs: Cursor):
        thumb_path = f'{PATH}/thumbnails/{self.video_id}.png'
        video_path = f'{PATH}/videos/{self.video_id}.mp4'
        audio_path = f'{PATH}/audios/{self.video_id}.mp3'
        if self.only_audio:
            with open(audio_path, 'rb') as audio, open(thumb_path, 'rb') as thumb:
                print(f'[INFO] {datetime.now()} -> BOT is uploading to telegram')
                if audio.__sizeof__() < 50 * (1024 ** 2):
                    bot.send_audio(chat_id=chat_id, audio=audio, 
                                    title=self.title, duration=self.duration, 
                                    performer=self.author, thumb=thumb)
        else:
            with open(video_path, 'rb') as video, open(thumb_path, 'rb') as thumb:
                print(f'[INFO] {datetime.now()} -> BOT is uploading to telegram')
                if video.__sizeof__() < 50 * (1024 ** 2):
                    bot.send_video(chat_id=chat_id, video=video, 
                                    title=self.title, duration=self.duration, 
                                    performer=self.author, thumb=thumb)
        print(f'[INFO] {datetime.now()} -> Uploading is finished')
        
        curs.insert(columns=['video_id', 'chat_id', 'date', 'only_audio'], 
                    values=[f"'{self.video_id}'", f"'{chat_id}'", f"'{datetime.now()}'", f"'{self.only_audio}'"], 
                    table='users')

    def __repr__(self):
        return f'{self.title}'

    def __str__(self):
        return f'{self.title}'