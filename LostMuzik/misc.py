#
# Copyright (C) 2021-2023 by LostBots@Github, < https://github.com/LostBots >.
#
# This file is part of < https://github.com/LostBots/LostMuzik > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/LostBots/LostMuzik/blob/master/LICENSE >
#
# All rights reserved.
#

import socket
import time

import heroku3
from pyrogram import filters

import config
from LostMuzik.core.mongo import pymongodb

from .logging import LOGGER

SUDOERS = filters.user()

HAPP = None
_boot_ = time.time()


def is_heroku():
    return "heroku" in socket.getfqdn()


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(config.HEROKU_API_KEY),
    "https",
    str(config.HEROKU_APP_NAME),
    "HEAD",
    "main",
]


def dbb():
    global db
    db = {}
    LOGGER(__name__).info(f"Veritabanı Başlatıldı.")


def sudo():
    global SUDOERS
    OWNER = config.OWNER_ID
    if config.MONGO_DB_URI is None:
        for user_id in OWNER:
            SUDOERS.add(user_id)
    else:
        sudoersdb = pymongodb.sudoers
        sudoers = sudoersdb.find_one({"sudo": "sudo"})
        sudoers = [] if not sudoers else sudoers["sudoers"]
        for user_id in OWNER:
            SUDOERS.add(user_id)
            if user_id not in sudoers:
                sudoers.append(user_id)
                sudoersdb.update_one(
                    {"sudo": "sudo"},
                    {"$set": {"sudoers": sudoers}},
                    upsert=True,
                )
        if sudoers:
            for x in sudoers:
                SUDOERS.add(x)
    LOGGER(__name__).info(f"Yetkililer Yüklendi.")


def heroku():
    global HAPP
    if is_heroku:
        if config.HEROKU_API_KEY and config.HEROKU_APP_NAME:
            try:
                Heroku = heroku3.from_key(config.HEROKU_API_KEY)
                HAPP = Heroku.app(config.HEROKU_APP_NAME)
                LOGGER(__name__).info(f"Heroku Uygulaması Yapılandırılmış")
            except BaseException:
                LOGGER(__name__).warning(
                    f"Lütfen Heroku API Anahtarınızın ve Uygulama adınızın heroku'da doğru şekilde yapılandırıldığından emin olun."
                )
