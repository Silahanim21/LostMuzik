import os
import asyncio
from datetime import timedelta
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeAllGroupChats

import config
from ..logging import LOGGER

private_commands = [
    BotCommand("start", "🎧 Botu başlatır"),
    BotCommand("yardim", "📖 Yardım menüsünü gösterir"),
]

group_commands = [
    BotCommand("oynat", "🔼 Müziği oynatır"),
    BotCommand("voynat", "📹 Videoyu oynatır"),
    BotCommand("atla", "⏭️ Sonraki Parçaya Geçer"),
    BotCommand("duraklat", "⏸️ Çalan Parçayı Durdurur"),
    BotCommand("devam", "▶️ Çalan Parçayı Devam Ettirir"),
    BotCommand("son", "⏹️ Çalan Parçayı Kapatır"),
    BotCommand("karistir", "🔀 Çalan Parçayı Karıştırır"),
    BotCommand("dongu", "🔄 Çalan Parçayı Tekrarlar"),
    BotCommand("sira", "📖 Çalma Listelerini Gösterir"),
    BotCommand("ilerisar", "⏩ Parçayı İleri Sarar"),
    BotCommand("gerisar", "⏪ Parçayı Geri Sarar"),
    BotCommand("playlist", "📖 Çalma Listenizi Gösterir"),
    BotCommand("bul", "📩 Seçtiğiniz Parçayı İndirir"),
    BotCommand("ayarlar", "⚙️ Bot Ayarlarını Gösterir"),
    BotCommand("restart", "🔃 Botu Yeniden Başlatır"),
    BotCommand("reload", "❤️‍🔥 Yönetici Önbelleğini Günceller"),
]

async def set_commands(client):
    await client.set_bot_commands(private_commands, scope=BotCommandScopeAllPrivateChats())
    await client.set_bot_commands(group_commands, scope=BotCommandScopeAllGroupChats())

class ArchMusic(Client):
    def __init__(self):
        LOGGER(__name__).info("Bot Başlatılıyor")
        super().__init__(
            "ArchMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
        )
        self.restart_interval = timedelta(hours=1)  # Varsayılan olarak 1 saat

    async def start(self):
        await super().start()
        try:
            get_me = await self.get_me()
            self.username = get_me.username
            self.id = get_me.id

            video_url = "https://telegra.ph/file/36221d40afde82941ffff.mp4"
            caption = "Bot Başlatılıyor... 🔮"
            
            try:
                await self.send_video(
                    config.LOG_GROUP_ID,
                    video=video_url,
                    caption=caption,
                )
            except Exception as e:
                LOGGER(__name__).error(
                    "Bot log grubuna erişemedi. Log kanalınıza botunuzu eklediğinizden ve yönetici olarak terfi ettirdiğinizden emin olun!"
                )
                sys.exit()

            await set_commands(self)  

            a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if a.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error(
                    "Lütfen Logger Grubunda Botu Yönetici Olarak Terfi Ettirin"
                )
                sys.exit()

        except Exception as e:
            LOGGER(__name__).error(f"Bot başlatılırken hata oluştu: {e}")
            sys.exit()

        if get_me.last_name:
            self.name = f"{get_me.first_name} {get_me.last_name}"
        else:
            self.name = get_me.first_name

        LOGGER(__name__).info(f" {self.name} olarak başlatıldı")

        self.schedule_restart()  

    async def restart_bot(self):
        LOGGER(__name__).info("Bot yeniden başlatılıyor...")
        try:
            await self.send_message(config.LOG_GROUP_ID, "Bot otomatik olarak yeniden başlatılıyor...")
            await asyncio.sleep(2)  # İsteğe
            os.system("kill -9 {}".format(os.getpid()))
            os.system("bash start")
        except Exception as e:
            LOGGER(__name__).error(f"Hata ile yeniden başlatılırken: {e}")

    def schedule_restart(self):
        loop = asyncio.get_event_loop()
        
        async def restart_at_intervals():
            while True:
                await asyncio.sleep(self.restart_interval.total_seconds())
                await self.restart_bot()

        loop.create_task(restart_at_intervals())
