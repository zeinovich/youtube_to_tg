from pytube import YouTube
from cursor import Cursor
from telebot import TeleBot
import os, requests
from datetime import datetime

PATH = os.getenv('PATH')

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
                self.streams.filter(only_audio=True).first().download(output_path=f'{PATH}/audio', filename=self.video_id)
            else:
                self.streams.filter(res='1080p').first().download(output_path=f'{PATH}/videos', filename=self.video_id)
        except Exception as e:
            print(e)
            
    def download_thumb(self):
        with open(f'{PATH}/audio/{self.video_id}.jpg', 'wb') as f:
            f.write(requests.get(self.thumbnail_url, allow_redirects=True).content)
    
    def upload(self, bot: TeleBot, chat_id: int, curs: Cursor):
        audio_path = f'{PATH}/audio/{self.video_id}.mp3'
        thumb_path = f'{PATH}/thumbnails/{self.video_id}.png'
        video_path = f'{PATH}/videos/{self.video_id}.mp4'
        if self.only_audio:
            with open(audio_path, 'rb') as audio, open(thumb_path, 'rb') as thumb:
                bot.send_audio(chat_id=chat_id, audio=audio, 
                                title=self.title, duration=self.duration, 
                                performer=self.author, thumb=thumb)
        else:
            with open(video_path, 'rb') as video, open(thumb_path, 'rb') as thumb:
                bot.send_video(chat_id=chat_id, video=video, 
                                title=self.title, duration=self.duration, 
                                performer=self.author, thumb=thumb)
        
        curs.insert(columns=['video_id', 'chat_id', 'date', 'only_audio'], 
                    values=[f"'{self.video_id}'", f"'{chat_id}'", f"'{datetime.now()}'", f"'{self.only_audio}'"], 
                    table='users')

    def __repr__(self):
        return f'{self.title}'

    def __str__(self):
        return f'{self.title}'