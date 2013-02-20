ART = 'art-default.jpg'
ICON = 'icon-default.png'
REGEX = '%s = new Array\((.+?)\);'
ZAP_TO_URL = 'http://%s:%s/web/zap?sRef=%s'
CHANNEL_URL = 'http://%s:%s/web/getservices?sRef=%s'
STREAM_URL = 'http://%s:%s/%s'

####################################################################################################
def Start():

	Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = 'Dreambox'
	DirectoryObject.thumb = R(ICON)

####################################################################################################
@handler('/video/dreambox', 'Dreambox', art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer(view_group='List', no_cache=True)

	if Prefs['host'] and Prefs['port_web'] and Prefs['port_video']:
		url = 'http://%s:%s/web/getservices' % (Prefs['host'], Prefs['port_web'])
		
		try:
			urlHtml = HTML.ElementFromURL(url)
		
		except:
			Log("Couldn't connect to Dreambox.") 
			return None
		
		ServiceReference = urlHtml.xpath("//e2servicereference/text()")
		ServiceName = urlHtml.xpath("//e2servicename/text()")

		for item in range(len(ServiceReference)):
				oc.add(DirectoryObject(
					key = Callback(BouquetsMenu, sender=ServiceName[item], index=ServiceReference[item], name=ServiceName[item]),
					title = ServiceName[item]
				))

	oc.add(PrefsObject(title='Preferences', thumb=R('icon-prefs.png')))

	return oc

#@route("/bouquets/{sender}/{index}/{name}")
def BouquetsMenu(sender, index, name):
	url = CHANNEL_URL % (Prefs['host'], Prefs['port_web'], String.Quote(index))
	try:
		urlHtml = HTML.ElementFromURL(url)
	except:
		Log("Couldn't get channels.") 
		return None
	ChannelReference = urlHtml.xpath("//e2servicereference/text()")
	ChannelName = urlHtml.xpath("//e2servicename/text()")
	
	oc = ObjectContainer(title2=name, view_group='List', no_cache=True)

	for item in range(len(ChannelReference)):
		oc.add(TvStationMenu(sender=ChannelName[item], channel=ChannelReference[item]))

	return oc

####################################################################################################
#@route("/tvstation/{sender}/{channel}/{thumb}/{include_oc}")
def TvStationMenu(sender, channel, thumb=R(ICON), include_oc=False):

	video = VideoClipObject(
		#url = STREAM_URL % (Prefs['host'], Prefs['port_video'], channel),
		key = Callback(TvStationMenu, sender=sender, channel=channel, thumb=thumb, include_oc=True),
		rating_key = channel,
		title = sender,
		thumb = thumb,
		items = [
			MediaObject(
				parts = [PartObject(key=HTTPLiveStreamURL(Callback(PlayVideo, channel=channel)))]
			)
		]
	)

	if include_oc:
		oc = ObjectContainer()
		oc.add(video)
		return oc
	else:
		return video


####################################################################################################
#@route("/play/{channel}")
def PlayVideo(channel):
	# Tune in to the stream
	stream = STREAM_URL % (Prefs['host'], Prefs['port_video'], channel)
	Log(stream)
	return Redirect(stream)
