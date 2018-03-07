from logic import *
NAME = 'KPodcast'
PREFIX = '/music/kpodcast'
ICON = 'icon-default.jpg'
ART = 'art-default.jpg'

####################################################################################################
def Start():
    ObjectContainer.title1 = NAME
    DirectoryObject.thumb = R(ICON)
    HTTP.CacheTime = 0

####################################################################################################
@handler(PREFIX, NAME, thumb = ICON, art = ART)
def MainMenu():
	oc = ObjectContainer()
	try:
		for menu in TOP_MENU_LIST:
			tmp = menu.split(':')
			oc.add(
			    DirectoryObject(
				key = 
				    Callback(
					Menu,
					title = unicode(tmp[0]),
					type = tmp[1]
				    ),
				title = unicode(tmp[0]),
				thumb = R("%s.png" % tmp[1])
			    )
			)
	except Exception as e:
		LOG('<<<Exception>>> MainMenu: %s' % e)
	return oc

####################################################################################################
@route(PREFIX + '/Menu')
def Menu(title, type):
	oc = ObjectContainer(title2 = unicode(title))
	try:
		list = GetMenuList(type)
		for item in list:
			tmp = item.split(':')
			title = tmp[0]
			param = tmp[1]
			oc.add(
			    DirectoryObject(
				key = 
				    Callback(
					ContentList,
					title = tmp[0],
					type = type,
					param = param,
				    ),
				title = unicode(tmp[0]),
				thumb = R("%s.png" % type)
			    )
			)
	except Exception as e:
		LOG('<<<Exception>>> Menu: %s' % e)
	return oc

####################################################################################################
@route(PREFIX + '/ContentList')
def ContentList(title, type, param, param2=None, pageNo='1'):
	oc = ObjectContainer(title2 = unicode(title))
	try:
		hasMore = 'N'
		if type == 'PODBBANG' or type == 'PODTY':
			hasMore, data = GetContentList(type, param, pageNo)
			LOG('HASMORE %s' % hasMore)
			for item in data:
				title = item['title']
				oc.add(
				    DirectoryObject(
					key = 
					    Callback(
						EpisodeList,
						title = item['title'],
						type = type,
						param = item['id']
					    ),
					title = unicode(item['title']),
					summary = unicode(item['summary']),
					thumb = item['img']
				    )
				)
		elif type == 'ITUNES' and (param == 'Audio' or param == 'Video'):
			data = GetItunesGenre(param)
			for item in data:
				oc.add(
				    DirectoryObject(
					key = 
					    Callback(
						ContentList,
						title = item['name'],
						type = type,
						param = item['json']
					    ),
					title = unicode(item['name']),
					#summary = unicode(item['summary']),
					#thumb = item['img']
				    )
				)
		elif type == 'ITUNES' and (param != 'Audio' and param != 'Video'):
			data = GetItunesProgramList(param)
			for item in data:
				plot = item['summary'] + '\n\n' + item['releaseDate']
				oc.add(
				    DirectoryObject(
					key = 
					    Callback(
						EpisodeList,
						title = item['name'],
						type = type,
						param = item['id']
					    ),
					title = unicode(item['name']),
					summary = unicode(plot),
					thumb = item['img']
				    )
				)

		if pageNo != '1':
			oc.add(DirectoryObject(
				key = Callback(ContentList, title=title, type=type, param=param, pageNo=str(int(pageNo)-1)),
				title = unicode('<< 이전 페이지')
			))
		if hasMore == 'Y':
			oc.add(DirectoryObject(
				key = Callback(ContentList, title=title, type=type, param=param, pageNo=str(int(pageNo)+1)),
				title = unicode('다음 페이지 >>')
			))

	except Exception as e:
		LOG('<<<Exception>>> ContentList: %s' % e)
	return oc


####################################################################################################
@route(PREFIX + '/EpisodeList')
def EpisodeList(title, type, param, param2=None, pageNo='1'):
	oc = ObjectContainer(title2 = unicode(title))
	try:
		hasMore, data = GetEpisodeList(type, param, pageNo)
		for item in data:
			if item['video'] == 'N' and Client.Product != 'Plex for iOS':
				oc.add(
					CreateTrackObject(
						url = item['url'],
						title = unicode(item['title']),
						summary = item['plot'],
						thumb = None
					)
				)
			else:
				oc.add(
					CreateVideoClipObject(
						url = item['url'], title = unicode(item['title']), thumb = None, art = ART,
						summary = unicode(item['plot']), type=type, save_param=None, 
						include_container = False
					)
				)
		if pageNo != '1':
			oc.add(DirectoryObject(
				key = Callback(EpisodeList, title=title, type=type, param=param, pageNo=str(int(pageNo)-1)),
				title = unicode('<< 이전 페이지')
			))
		if hasMore == 'Y':
			oc.add(DirectoryObject(
				key = Callback(EpisodeList, title=title, type=type, param=param, pageNo=str(int(pageNo)+1)),
				title = unicode('다음 페이지 >>')
			))
	except Exception as e:
		LOG('<<<Exception>>> EpisodeList: %s' % e)
	return oc

####################################################################################################
@route(PREFIX + '/Quality')
def Quality(title, type, code, summary, thumb, save_param, music_yn='N'):
	oc = ObjectContainer(title2 = unicode(title))
	message = '시청불가'
	try:
		pass
	except Exception as e:
		LOG('<<<Exception>>> Quality: %s' % e)
	if len(oc) == 0:
		oc.add(DirectoryObject(key = Callback(Label, message=message), title = unicode(message)))
	return oc

####################################################################################################
@route(PREFIX + '/CreateVideoClipObject', include_container = bool)
def CreateVideoClipObject(url, title, thumb, art, summary, type, save_param, 
                          optimized_for_streaming = True,
                          include_container = False, *args, **kwargs):

    vco = VideoClipObject(
        key = Callback(CreateVideoClipObject,
		url = url, title = title, thumb = thumb, art = art, summary = summary,
		type=type, save_param=save_param,
		optimized_for_streaming = optimized_for_streaming,
		include_container = True),
        rating_key = url,
        title = title,
        thumb = thumb,
        art = art,
        summary = summary,
        items = [
            MediaObject(
                parts = [
                    PartObject(
                        key = HTTPLiveStreamURL(Callback(PlayVideo, url = url, type=type, save_param=save_param))
                    )
                ],
                optimized_for_streaming = optimized_for_streaming,
            )
        ]
    )

    if include_container:
        return ObjectContainer(objects = [vco])
    else:
        return vco

####################################################################################################
@route(PREFIX + '/createtrackobject', include_container = bool)
def CreateTrackObject(url, title, summary, thumb, include_container=False, *args, **kwargs):
	container = Container.MP4
	audio_codec = AudioCodec.AAC
	track_object = TrackObject(
		key = Callback(CreateTrackObject, url=url, title=title, summary=summary, thumb=thumb, include_container=True),
		rating_key = url,
		title = title,
		summary = summary,
		items = [
			MediaObject(
				parts = [
					PartObject(key=url)
				],
				container = container,
				audio_codec = audio_codec,
				audio_channels = 2
			)
		], 
		thumb = Resource.ContentsOfURLWithFallback(thumb)
	)

	if include_container:
		return ObjectContainer(objects=[track_object])
	else:
		return track_object

####################################################################################################
@indirect
@route(PREFIX + '/PlayVideo.m3u8')
def PlayVideo(url, type, save_param):
	#try:
	#	if save_param is not None:
	#		SaveWatchedList(save_param)
	#except Exception as e:
	#	LOG('<<<Exception>>> PlayVideo: %s' % e)
	return IndirectResponse(VideoClipObject, key = url)

####################################################################################################
@route(PREFIX + '/label')
def Label(message):
	oc = ObjectContainer(title2 = unicode(message))
	oc.add(DirectoryObject(key = Callback(Label, message=message),title = unicode(message)))
	return oc
