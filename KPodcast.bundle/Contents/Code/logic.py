# -*- coding: utf-8 -*-
def LOG(str):
	try :
		import xbmc, xbmcaddon
		try:
			xbmc.log("[%s-%s]: %s" %(xbmcaddon.Addon().getAddonInfo('id'), xbmcaddon.Addon().getAddonInfo('version'), str), level=xbmc.LOGNOTICE)
			log_message = str.encode('utf-8', 'ignore')
		except:
			log_message = 'KPODCAST Exception'
		xbmc.log("[%s-%s]: %s" %(xbmcaddon.Addon().getAddonInfo('id'), xbmcaddon.Addon().getAddonInfo('version'), log_message), level=xbmc.LOGNOTICE)
		return
	except:
		pass

	try:
		Log(str)
		return
	except:
		pass

def ChangeHTMLChar(str):
	from HTMLParser import HTMLParser
	return HTMLParser().unescape(str.decode('utf8'))


TOP_MENU_LIST = ['팟빵:PODBBANG', '팟티:PODTY', 'iTunes Podcasts:ITUNES', 'EBS 오디오북:EBS']

def GetMenuList(type):
	isPlay = False
	ret = None
	if type == 'PODBBANG':
		ret = MENU_PODBBANG
	elif type == 'PODTY':
		ret = MENU_PODTY
	elif type == 'ITUNES':
		ret = MENU_ITUNES
	return ret

def GetContentList(type, param, pageNo):
	if type == 'PODBBANG':	return GetPodbbangProgramList(param, pageNo)
	elif type == 'PODTY':	return GetPodtyProgramList(param, pageNo)

def GetEpisodeList(type, id, page):
	if type == 'PODBBANG':
		return GetPodbbangEpisodeList(id, page)
	elif type == 'PODTY':
		return GetPodtyEpisodeList(id, page)
	elif type == 'ITUNES':
		return GetItunesEpisodeList(id, page)
	elif type == 'EBS':
		return GetEBSEpisodeList(id, page)

def GetURL(type, param):
	if type == 'EBS':
		return GetEBSURL(param)


###############################################################################
import urllib, urllib2, cookielib
import json
import re
from logic import *

MENU_PODBBANG = [
	'종합순위:',
	'시사 및 정치:0',
	'코미디:7',
	'도서:1',
	'영화:3',
	'경제:4',
	'어학:5',
	'교육 및 기술:6',
	'스포츠:8',
	'음악:9',
	'여행:21',
	'건강 및 의학:10',
	'문화 및 예술:19',
	'취미:11',
	'유아동:18',
	'정부 및 기관:13',
	'게임:16',
	'종교:12',
	'지역:20',
	'해외 팟캐스트:15' ]
MENU_PODTY = [
	'차트:',
	'뉴스&정치:10',
	'IT&기술:15',
	'코미디:3',
	'음악:9',
	'영화&음악:16',
	'교육&외국어:4',
	'게임&취미:5',
	'스포츠:14',
	'예술:1',
	'시사:6',
	'건강:7',
	'육아&가정:8',
	'종교:11',
	'과학&의학:12',
	'사회&문화:13'
	]


PODTY_URL = 'https://www.podty.me'
PODBBANG_URL = 'http://www.podbbang.com'

def GetPodbbangProgramList(category, pageNo='1'):
	url = PODBBANG_URL + '/ranking?kind=daily' if category is None or category == 'None' else PODBBANG_URL + '/ranking/category?kind=daily&cate=' + category
	url = url + '&start=' + str(((int(pageNo)-1)*100)+1)
	hasMore = 'Y' if category is None or category == 'None' else 'N'
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = response.read()
	#cate dummy id title dummy summary
	#regax = 'cate\"\>.*\"\>(.*?)\<(.*\s*){4}.*\/ch\/(.*?)\".*\"\>(.*?)\<(.*\s*){3}.*title\=\"(.*?)\<'
	#regax = 'cate\"\>.*\"\>(.*?)\<.*\s*.*\s*.*\s*.*\s*.*\/ch\/(.*?)\".*\"\>(.*?)\<.*\s*.*title.*\s*.*title.*\s*.*title\=\"(.*?)'
	regax = 'cate\"\>.*\"\>(.*?)\<(.*\s*){4}.*\/ch\/(.*?)\".*\"\>(.*?)\<(.*\s*){3}.*title\=\"(.*?)\<.*'
	r = re.compile(regax)
	m = r.findall(data)
	ret = []
	for item in m:
		info = {}
		info['cate'] = item[0]
		info['id'] = item[2]
		info['title'] = ChangeHTMLChar(item[3])
		if info['title'] == '':
			info['title'] = '19+'
		info['summary'] = ChangeHTMLChar(item[5])
		info['img'] = 'http://img.podbbang.com/img/pb_m/thumb/x88/%s.png' % info['id']
		ret.append(info)
	return hasMore, ret

def GetPodtyProgramList(category, pageNo='1'):
	url = PODTY_URL + '/chart/podty/daily' if category is None else PODTY_URL + '/chart/daily?catId=' + category
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = response.read()
	regax = 'ranking\">(.*?)<.*\s*.*\s*.*\/cast\/(.*?)\">.*\"\s*(.*?)\"\s*.*alt=\"(.*?)\".*\s*.*\s*.*\">(.*?)\<.*\s*.*\"\>(.*?)\<'
	p = re.compile(regax)
	m = p.findall(data)
	ret = []
	for item in m:
		info = {}
		info['cate'] = item[5]
		info['id'] = item[1]
		info['title'] = ChangeHTMLChar(item[3])
		info['summary'] = ChangeHTMLChar(item[4])
		info['img'] = item[2]
		info['index'] = item[0]
		ret.append(info)
	
	return 'N', ret


def GetPodtyEpisodeList(id, page):
	url = ('https://www.podty.me/cast/%s/episodes?page=%s&dir=desc' % (id, page))
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = response.read()
	regax = 'class=\"btnNext\"'
	has_more = 'Y' if data.find(regax) != -1 else 'N'
	regax = 'uri\=\"(.*?)\".*type\=\"(.*?)\".*name\=\"(.*?)\"(.*\s*){3}.*date\"\>(.*?)\<(.*\s*){4}(.*?)\s'
	r = re.compile(regax)
	m = r.findall(data)
	ret = []
	for item in m:
		info = {}
		info['title'] = ChangeHTMLChar(item[2])
		info['video'] = 'Y' if item[1] == 'video/mp4' else 'N'
		info['duration'] = None
		if len(item) > 5:
			tmp = item[6].split(':')
			if len(tmp) == 3:
				info['duration'] = int(tmp[2]) + int(tmp[1]) * 60 + int(tmp[0])*3600
		info['plot'] = ChangeHTMLChar(item[2] + '\n' + item[4])
		info['url'] = item[0]
		ret.append(info)
	return has_more, ret

def GetPodbbangEpisodeList(id, page):
	url = ('http://app-api4.podbbang.com/channel?channel=%s&order=desc&count=30&page=%s' % (id, page))
	request = urllib2.Request(url)
	request.add_header('Podbbang', 'os=iOS&osver=4.4.2&ver=4.35.271&device=MQAG2KH/A&device_id=359090030208175&id=4349893&auth_code=cdc986a2d1184895178e8129231a39cc6c7c31ab&nick=&is_login=N&is_adult=N')
	request.add_header('user-agent', 'Dalvik/1.6.0 (Linux; U; Android 4.4.2; Nexus 6 Build/KOT49H)')
	response = urllib2.urlopen(request)
	data = json.load(response, encoding='utf8')
	has_more = 'Y' if int(data['data']['total_count']) > int(page)*30 else 'N'
	ret = []
	for item in data['list']:
		info = {}
		info['url'] = item['file_url']
		info['title'] = ChangeHTMLChar(item['title'].encode('utf8'))
		info['plot'] = ChangeHTMLChar(item['summary'].encode('utf8')) +  '\n' + item['date']
		info['duration'] = item['duration']
		info['video'] = 'N' if item['type'] == 'audio' else 'Y'
		#info['date'] = item['date']
		ret.append(info)
	return has_more, ret

###############################################################################
import urllib, urllib2
import json
import re
from logic import *

MENU_ITUNES = [	'Audio:Audio', 'Video:Video']
GENRE_LIST_URL = 'http://itunes.apple.com/WebObjects/MZStoreServices.woa/ws/genres?id=26'
STORE_ID = '143466'  # Korea

def GetItunesGenre(type, includeSubgenre=False):
	request = urllib2.Request(GENRE_LIST_URL)
	request.add_header('X-Apple-Store-Front', STORE_ID)
	response = urllib2.urlopen(request)
	data = json.load(response, encoding='utf8')
	data = data['26']
	list = []
	info = {}
	info['name'] = 'TOP' #data['name']
	info['json'] = data['rssUrls']['topAudioPodcasts'] if type == 'Audio' else data['rssUrls']['topVideoPodcasts']
	list.append(info)
	keys = data['subgenres'].keys()
	for i in range(0, len(keys)):
		genre = data['subgenres'][keys[i]]
		info = {}
		info['name'] = genre['name']
		info['json'] = genre['rssUrls']['topAudioPodcasts'] if type == 'Audio' else genre['rssUrls']['topVideoPodcasts']
		list.append(info)
		if includeSubgenre and 'subgenres' in genre:
			sub_keys = genre['subgenres'].keys()
			for j in range(0, len(sub_keys)):
			#for sub_genre in genre['subgenres']:
				sub_genre = genre['subgenres'][sub_keys[j]]
				info = {}
				info['name'] = genre['name'] + ' - ' + sub_genre['name']
				info['json'] = sub_genre['rssUrls']['topAudioPodcasts'] if type == 'Audio' else sub_genre['rssUrls']['topVideoPodcasts']
				list.append(info)
		
	return list


def GetItunesProgramList(url):
	url = url.replace('/json', '/limit=50/json')
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = json.load(response, encoding='utf8')
	data = data['feed']
	list = []
	for item in data['entry']:
		info = {}
		info['name'] = item['title']['label']
		count = len(item['im:image'])
		info['img'] = item['im:image'][count-1]['label']
		info['summary'] = ' ' if 'summary' not in item else item['summary']['label']
		info['id'] = item['id']['attributes']['im:id']
		info['artist'] = item['im:artist']['label']
		info['releaseDate'] = '' if 'releaseDate' not in item else item['im:releaseDate']['label'].split('T')[0]
		list.append(info)
	return list

def GetItunesEpisodeList(id, pageNo):
	url = 'http://itunes.apple.com/lookup?id=' + id
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = json.load(response, encoding='utf8')
	feedurl = data['results'][0]['feedUrl']
	url = data['results'][0]['trackViewUrl']
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = response.read()
	regax = 'title=\"(.*?)\".*video-preview-url=\"(.*?)\".*'
	r = re.compile(regax)
	m = r.findall(data)
	list = []
	if len(m) > 0:
		for item in m:
			info = {}
			info['url'] = item[1]
			info['title'] = ChangeHTMLChar(item[0])
			#info['duration'] = item[2][:4]
			info['video'] = 'Y'
			info['plot'] = info['title']
			list.append(info)
	else:
		regax = 'audio-preview-url=\"(.*?)\".*title=\"(.*?)\".*'
		r = re.compile(regax)
		m = r.findall(data)
		for item in m:
			info = {}
			info['url'] = item[0]
			info['title'] = ChangeHTMLChar(item[1])
			#info['duration'] = item[2][:4]
			info['video'] = 'N'
			info['plot'] = info['title']
			list.append(info)
	return 'N', list

###############################################################################
def GetEBSEpisodeList(id, pageNo):
	url = 'http://home.ebs.co.kr/audiobook/replay/4/list?c.page=%s&searchKeywordValue=0&orderBy=NEW&searchConditionValue=0&courseId=BP0PHPK0000000048&vodSort=NEW&searchStartDtValue=0&brdcDsCdFilter=RUN&searchKeyword=&userId=&searchEndDt=&searchCondition=&searchEndDtValue=0&stepId=01BP0PHPK0000000048&searchStartDt=&' % pageNo
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = response.read()
	list = []
	regax = 'fn_view\((.*?)\); return false;\">(.*?)<'
	r = re.compile(regax)
	m = r.findall(data)
	for item in m:
		info = {}
		info['id'] = item[0].split(',')[0].replace('\'', '')
		info['title'] = ChangeHTMLChar(item[1])[13:]
		info['plot'] = ''
		info['video'] = 'N'
		info['url'] = 'dummy'
		list.append(info)
	
	hasMore = 'Y' if len(list) == 20 else 'N'
	return hasMore, list

def GetEBSURL(id):
	url = 'http://home.ebs.co.kr/audiobook/replay/4/view?courseId=BP0PHPK0000000048&stepId=01BP0PHPK0000000048&prodId=10314&pageNo=1&lectId=%s&lectNm=&bsktPchsYn=&prodDetlId=&oderProdClsCd=&prodFig=&vod=A&oderProdDetlClsCd=' % id
	request = urllib2.Request(url)
	response = urllib2.urlopen(request)
	data = response.read()
	regax = 'ZoenAuthDecode\(\'(.*?)\''
	r = re.compile(regax)
	m = r.findall(data)
	if len(m) == 1:
		return m[0]
	else:
		return None
