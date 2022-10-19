from pyrogram import Client
from video import Video

class Agent(Client):
    def __init__(self, api_id, api_hash, session_name):
        super().__init__(session_name, api_id, api_hash)
        self.start()

    def upload(self, video: Video, channel_id: int):
        message = self.send_audio(chat_id=channel_id, audio=video.audio_path)
        return message.id
    