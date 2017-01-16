#!/usr/bin/env python3

from __future__ import unicode_literals
import os
import logging
from urllib.request import urlopen

import soundcloud
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from sqlalchemy.orm import Session

from credentials import ENGINE, TOKEN
from database import Backup

from ID3 import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

u = Updater(TOKEN)
dp = u.dispatcher
client = soundcloud.Client(access_token='b7d32689d8510caf9e0cbc133b3498dd')


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text="Music Downloader")

class SoundCloudDownload:
   def __init__(self, url, verbose, tags):
      self.url = url
      self.verbose = verbose
      self.tags = tags
      self.download_progress = 0
      self.current_time = time.time()
      self.titleList = []
      self.artistList = []
      self.likes = False   
    
   def addID3(self, title, artist):
      try:
         id3info = ID3("{0}.mp3".format(title))
         # Slicing is to get the whole track name
         # because SoundCloud titles usually have
         # a dash between the artist and some name
         split = title.find("-")
         if not split == -1:
            id3info['TITLE'] = title[(split + 2):] 
            id3info['ARTIST'] = title[:split] 
         else:
            id3info['TITLE'] = title
            id3info['ARTIST'] = artist
         print "\nID3 tags added"
         bot.sendMessage(update.message.chat_id, text="\nID3 tags added")
      except InvalidTagError, err:
         print "\nInvalid ID3 tag: {0}".format(err)
   
   def downloadSongs(self):
      done = False
      for artist, title, streamURL in zip(self.artistList, self.titleList, self.streamURLlist):
         if not done:
            filename = "{0}.mp3".format(title)
            sys.stdout.write("\nDownloading: {0}\n".format(filename))
            try:
               if not os.path.isfile(filename):
                  filename, headers = urllib.urlretrieve(url=streamURL, filename=filename, reporthook=self.report)
                  self.addID3(title, artist)
                  # reset download progress to report multiple track download progress correctly
                  self.download_progress = 0
               elif self.likes:
                  print "File Exists"
                  done = True
               else:
                  print "File Exists"
            except:
               print "ERROR: Author has not set song to streamable, so it cannot be downloaded"
   


   def music(bot, update):
    title, track_url = search(update.message.text)
    session = Session(bind=ENGINE)
    session.add(Backup(title=title, track_url=track_url))
    session.commit()
    session.close()
    download(title, track_url)
    bot.sendAudio(update.message.chat_id,
                  audio=open(title + '.mp3', 'rb'),
                  title=title)
    os.remove(title + '.mp3')


def search(text):
    query = '+'.join(text.lower().split())
    url = 'https://soundcloud.com/search?q=' + query
    content = urlopen(url).read()
    soup = BeautifulSoup(content, 'html.parser')
    tag = soup.find('a', {'rel': 'spf-prefetch'})
    title = tag.text
    track_url = 'https://soundcloud.com' + tag.get('href')
    return title, track_url

def choice(text):
    bot.sendMessage(update.message.chat_id, title(tag.text))
    

def download(title, track_url):
   for artist, title, streamURL in zip(self.artistList, self.titleList, self.streamURLlist):
         if not done:
            filename = "{0}.mp3".format(title)
            sys.stdout.write("\nDownloading: {0}\n".format(filename))
            try:
               if not os.path.isfile(filename):
                  filename, headers = urllib.urlretrieve(url=streamURL, filename=filename, reporthook=self.report)
                  self.addID3(title, artist)
                  # reset download progress to report multiple track download progress correctly
                  self.download_progress = 0
               elif self.likes:
                  print "File Exists"
                  done = True
               else:
                  print "File Exists"
            except:
               print "ERROR: Author has not set song to streamable, so it cannot be downloaded"
   
   def report(self, block_no, block_size, file_size):
      self.download_progress += block_size
      if int(self.download_progress / 1024 * 8) > 1000:
         speed = "{0} Mbps".format(round((self.download_progress / 1024 / 1024 * 8) / (time.time() - self.current_time), 2))
      else:
         speed = "{0} Kbps".format(round((self.download_progress / 1024 * 8) / (time.time() - self.current_time), 2))
      rProgress = round(self.download_progress/1024.00/1024.00, 2)
      rFile = round(file_size/1024.00/1024.00, 2)
      percent = round(100 * float(self.download_progress)/float(file_size))
      sys.stdout.write("\r {3} ({0:.2f}/{1:.2f}MB): {2:.2f}%".format(rProgress, rFile, percent, speed))
      sys.stdout.flush()

        ## Convenience Methods
   def getTitleFilename(self, title):
                '''
                Cleans a title from Soundcloud to be a guaranteed-allowable filename in any filesystem.
                '''
                allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ 0123456789-_()"
                return ''.join(c for c in title if c in allowed)

if __name__ == "__main__":
   if (int(requests.__version__[0]) == 0):
      print "Your version of Requests needs updating\nTry: '(sudo) pip install -U requests'"
      sys.exit()

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler([Filters.text], music))

u.start_polling()
u.idle()
