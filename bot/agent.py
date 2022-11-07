from pyrogram import Client
from video import Video
from datetime import datetime 

class Agent(Client):
    def __init__(self, api_id, api_hash, session_name):
        super().__init__(name=session_name, api_id=api_id, api_hash=api_hash)

    def upload(self, video: Video, channel_id: str, PATH):
        if video.only_audio:
            path = f'{PATH}/audios/{video.video_id}.mp3'
            print(f'[INFO] {datetime.now()} -> AGENT is uploading to telegram')
            message = self.send_audio(chat_id=channel_id, audio=path)
        else:
            path = f'{PATH}/videos/{video.video_id}.mp4'
            print(f'[INFO] {datetime.now()} -> AGENT is uploading to telegram')
            message = self.send_video(chat_id=channel_id, video=path)
        return message.id

    def __exit__(self, *args):
        return super().__exit__(*args)

    def __enter__(self):
        return super().__enter__()
    