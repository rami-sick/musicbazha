#!/usr/bin/env python3

from __future__ import unicode_literals
import os
import logging
from urllib.request import urlopen

import youtube_dl
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from sqlalchemy.orm import Session

from credentials import ENGINE, TOKEN
from database import Backup

import logging
import json
import math
from aiotg import Bot

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

u = Updater(TOKEN)
dp = u.dispatcher


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text="به بات موزیک بازها خوش آمدید ... برای پیدا کردن موزیک مورد نظر اسم خواننده و ترانه مورد نظر را ارسال کنید.."
                                                 "تمامی حقوق متعلق است به"
                                                 "PeDitX"
                                                 "@peditx")



def music(bot, update):
    title, video_url = search(update.message.text)
    session = Session(bind=ENGINE)
    session.add(Backup(title=title, video_url=video_url))
    session.commit()
    session.close()
    download(title, video_url)
    bot.sendAudio(update.message.chat_id,
                  audio=open(title + '.mp3', 'rb'),
                  title=title)
    os.remove(title + '.mp3')


def search(text):
    query = '+'.join(text.lower().split())
    url = 'https://www.youtube.com/results?search_query=' + query
    content = urlopen(url).read()
    soup = BeautifulSoup(content, 'html.parser')
    tag = soup.find('a', {'rel': 'spf-prefetch'})
    title = tag.text
    video_url = 'https://www.youtube.com' + tag.get('href')
    return title, video_url



def download(title, video_url):
    ydl_opts = {
        'outtmpl': title + '.%(ext)s',
        'format': 'bestaudio/best', 'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([video_url])


dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler([Filters.text], music))

u.start_polling()
u.idle()

def search_tracks(chat, query, page=1):
    logger.info("%s searching for %s", chat.sender, query)

    limit = 8
    offset = (page - 1) * limit

    cursor = text_search(query).skip(offset).limit(limit)
    count = await cursor.count()
    results = await cursor.to_list(limit)

    if count == 0:
        chat.send_text(not_found)
        return

    # Return single result if we have exact match for title and performer
    if results[0]['score'] > 2:
        limit = 1
        results = results[:1]

    newoff = offset + limit
    show_more = count > newoff

    if show_more:
        pages = math.ceil(count / limit)
        kb = [['(%d/%d) Show more for "%s"' % (page, pages, query)]]
        keyboard = {
            "keyboard": kb,
            "resize_keyboard": True
        }
    else:
        keyboard = { "hide_keyboard": True }

    for track in results:
        send_track(chat, keyboard, track)


def inline_result(track):
    return {
        "type": "audio",
        "id": track["file_id"],
        "audio_file_id": track["file_id"],
        "title": "{} - {}".format(
            track.get("performer", "Unknown Artist"),
            track.get("title", "Untitled")
        )
    }
