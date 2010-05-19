#!/Usr/bin/env python

DEBUG = False
FORCE_CACHE = False

import feedparser
#from RSS import CollectionChannel, TrackingChannel, ns # decode RSS from hackaday
import codecs
from BeautifulSoup import BeautifulSoup, Tag, NavigableString, BeautifulStoneSoup
import Image
import httplib2
import time
import os 
import shutil
import re
import Image
import hashlib
from datetime import datetime, timedelta, date
import random

from django.core.management import setup_environ
import settings
setup_environ(settings)
from django.template import Template, Context
from no3z_www.main.models import Noticia

dia = datetime.today()
tuple = dia.timetuple()


DIR = settings.MEDIA_ROOT+'/images/'

THUMBS_DIRECTORY = DIR
DEPLOY_DIRECTORY = DIR
		
"""Removes thumbnails older than a quarter hour"""
def clean_thumbs_directory():
	now = time.time()
	for f in os.listdir(THUMBS_DIRECTORY):
		filename = os.path.join(THUMBS_DIRECTORY, f)
		last_edit = os.stat(filename).st_mtime
 		if now - last_edit > 60*15:
			os.unlink(filename)

"""Download (and cache) <url> file to imgs/thumbs/. Returns saved file name. """
def download_img(url, file_name):
	print 'downloading ' + url
	h = httplib2.Http("no3z_cache", timeout=10)
	resp, content = h.request(url)	
	f = open(file_name, "w")
	f.write(content) 
	f.close()
	return file_name
		
"""Resize an image (rewriting it)"""
def thumbnail(file, x=120, y=100):
    print "thumbnailing " + file
    image = Image.open(file)
    image.thumbnail([x, y], Image.ANTIALIAS)
    image.save(file, image.format)
    return file
	
"""Download ad resize an img from a given URL"""
def download_and_thumbnail(url, x=120, y=100):
	format = url.rsplit('.', 1)[1]		# www.site.com/path/img.jpg -> .jpg
	format = format.split('&', 1)[0] 	# could be: .jpg?w=100&y=200&...
	hashfun = hashlib.md5()
	hashfun.update(url)
	file_name = os.path.join(THUMBS_DIRECTORY, str(hashfun.hexdigest()) + '.' + format)
	if not os.path.exists(file_name):
		download_img(url, file_name)
		thumb_name = thumbnail(file_name, x=x, y=y)
		thumb_name = thumb_name[len(DEPLOY_DIRECTORY):]	# cut off starting 'pub/'
		return thumb_name
	thumb_name = file_name[len(DEPLOY_DIRECTORY):]	# cut off starting 'pub/'
	return thumb_name

def download_feed(url, file_name):
	content = None
	try:
		print "downloading " + url
		h = httplib2.Http("no3z_cache", timeout=10)
		resp, content = h.request(url,"GET")
	except httplib2.ServerNotFoundError:
		return None
			
	file_name = os.path.join("feeds", file_name)
	f = open(file_name, "w")
	f.write(content) 
	f.close()
	return file_name	

def get_feed(url, file_name):
	if DEBUG:
		file_name = 'feeds/'+file_name
	else:
		try:
			file_name = download_feed(url, file_name)
		except Exception, e:
			print e
			return []
	rss = feedparser.parse(file_name)
	
	for entry in rss.entries:
		entry.description = remove_html_tags(entry.description) 

	return rss.entries

"""If the link is an image, puts a thumbnail of the picture inside the description"""	
def description_thumbs(entries):
	for entry in entries:
		if entry.link.endswith('.jpg') or entry.link.endswith('.jpeg') or entry.link.endswith('.png'):
			thumb = download_and_thumbnail(entry.link, x=200, y=200)			
			entry.description = '<img src=\''+ thumb +'\'><br/>' + entry.description
		elif entry.link.startswith('http://imgur.com/'):
			# TODO: add .gif support 
			if entry.link.endswith('.jpg') or entry.link.endswith('.png'):
				print entry.link
				thumb = download_and_thumbnail(entry.link+'.jpg')
				entry.description = '<img src=\''+ thumb +'\'><br/>' + entry.description
	return entries
	
def images_from_html(html):
	soup = BeautifulSoup(html)	
	tags = soup.findAll('img')
#	for img in images_from_html():
#		print img['src']
	return tags
	
def links_from_html(html):
	# TODO: Use regex here please
	soup = BeautifulSoup(html)
	tags = soup.findAll('a')
	return tags

def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def get_feed_and_images(url,file_name):
	entries = get_feed(url, file_name)
	
	for entry in entries:
		addr = None
		try:
			imgs = images_from_html(entry.content[0].value)
			for img in imgs:
				addr = img['src']
				if addr != None:
					break
		except:
			print 'No image header'

		if addr == None: 
			continue
		thumb = download_and_thumbnail(addr)
		entry.description = remove_html_tags(entry.description)
		entry['img'] = thumb
	return entries
	

def get_reddit_videos():
	feeds = []
	feeds.append(get_reddit_like_feed('http://www.reddit.com/r/geek/.rss', 'r_geek', find_description=False))
	feeds.append(get_reddit_like_feed('http://www.reddit.com/r/technology/.rss', 'r_technology', False))
	feeds.append(get_reddit_like_feed('http://www.reddit.com/r/science/.rss', 'r_science', False))
	feeds.append(get_reddit_like_feed('http://www.reddit.com/r/scifi/.rss', 'r_scifi', False))
	feeds.append(get_reddit_like_feed('http://www.reddit.com/r/gaming/.rss', 'r_gaming', False))
	
	videos = []
	for feed in feeds:
		for entry in feed:
			if entry.link.startswith('http://www.youtube.com/watch?v='):
				# extract code from http://www.youtube.com/watch?v=3yaY98GTCYM#t=3m45s
				youtube_code = entry.link.split('http://www.youtube.com/watch?v=')[1]
				youtube_code = youtube_code.split('#')[0].split('&')[0]
				entry['thumb'] = 'http://i2.ytimg.com/vi/' + youtube_code + '/default.jpg'
				entry.title = cut_title(entry.title)
				videos.append(entry)
	return videos
	
def get_slashdot_feed():
	entries = get_feed("http://rss.slashdot.org/Slashdot/slashdot", "slashdot");
	for entry in entries:
		entry.description = remove_html_tags(entry.description) 
	return entries	
	


def get_context():
	punset = get_feed_and_images("http://www.eduardpunset.es/category/apoyo-psicologico/feed","punset")
	inteligencia = get_feed_and_images("http://www.inteligenciaemocionalysocial.com/feed","inteligencia")
	#nasa = get_feed_and_images("http://www.nasa.gov/rss/image_of_the_day.rss","nasa")
	nasa2 = get_feed_and_images("http://globolalia.wordpress.com/2010/feed/","nasa2")
	docuheaven = get_feed_and_images('http://documentaryheaven.com/feed/', 'docuheaven')	
	vigilant = get_feed_and_images("http://vigilantcitizen.com/?feed=rss2","vigilant")
	temp = punset +  inteligencia + docuheaven + vigilant + nasa2
	images = []
	for it in temp:
		if hasattr(it,"img"):
			images.append(it)
	context_table = {'all' : images,}
        for it in images:
            note = Noticia(title=it.title,
						   description=it.description,
						   author=it.author,
						   image='images/'+it.img,
						   link=it.link,
                           pubDate = datetime.today(),
						   )
            try:
                note.save()
            except:
                continue
            
	return context_table
