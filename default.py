import xbmcplugin
import xbmcgui
import xbmcaddon
import sys
import urllib, urllib2
import re


addon = xbmcaddon.Addon(id='plugin.video.gameone')

thisPlugin = int(sys.argv[1])

baseLink = "http://www.gameone.de/"
apiLink = "http://www.gameone.de/api/mrss/"

def mainPage():
    global thisPlugin
    
    addDirectoryItem("TV", {"action":"showTV","link":"http://www.gameone.de/tv"}, "")
    #Blog
    #Games
    addDirectoryItem("Playtube", {"action":"showPlaytube","link":"http://www.gameone.de/playtube"}, "")
    addDirectoryItem("Podcast", {"action":"showPodcast","link":"http://feeds.feedburner.com/mtvgameone?format=xml"}, "")
    
    xbmcplugin.endOfDirectory(thisPlugin)
    
def showTV(link):
    page = load_page(urllib.unquote(link))
    
    extractEpisode = re.compile("<li>\n<a href=\"(.*)\" class=\"image_link\"><img alt=\".*?\" src=\"(.*?)\" /></a>\n<h5>\n<a href='.*?' title='(.*?)'>\n(.*?)\n</a>")
    
    for episode in extractEpisode.finditer(page):
        menu_name = episode.group(4)+" ("+episode.group(3)+")"
        menu_link = baseLink + episode.group(1)
        menu_pic = episode.group(2)
        addDirectoryItem(menu_name, {"action":"playEpisode","link":menu_link}, menu_pic, False)
    
    xbmcplugin.endOfDirectory(thisPlugin)

def showPlaytube(link):
    page = load_page(urllib.unquote(link))
    
    #Channels
    extractChannels = re.compile("<ul class='channels'>(.*?)</ul>",re.DOTALL)
    extractChannel = re.compile("<a class='name' href='(.*?)' title='(.*?)'>")
    
    channels = extractChannels.search(page).group(1)
    
    for channel in extractChannel.finditer(channels):
        menu_name = channel.group(2)
        menu_link = channel.group(1)
        addDirectoryItem(menu_name, {"action":"showPlaytubeChannel","link":menu_link}, "", True)

    xbmcplugin.endOfDirectory(thisPlugin)

def showPodcast(link):
    page = load_page(urllib.unquote(link))
    
    extractPodcast = re.compile("<item>.*?<title>(.*?)</title>.*?:origLink>(.*?)</feedburner.*?</item>",re.DOTALL)
    
    for podcast in extractPodcast.finditer(page):
        menu_name = podcast.group(1)
        menu_link = podcast.group(2)
        addDirectoryItem(menu_name, {"action":"playPodcast","link":menu_link}, "", False)
    
    xbmcplugin.endOfDirectory(thisPlugin)
        
    
    
def showPlaytubeChannel(link):
    page = load_page(urllib.unquote(link))
    
    extractEpisodes = re.compile("<ul class='(videos teasers|teasers videos)*'>(.*?)</ul>\n<div class='clear'>",re.DOTALL)
    episodes = extractEpisodes.search(page).group(2)
    extractEpisode = re.compile("<li class='.*?'>.*?<div class='.*?'>.*?<a href=\"(.*?)\">(.*?)</a>.*?<a href=\".*?\" class=\"img_link\"><img alt=\".*?\" src=\"(.*?)\" />",re.DOTALL)
    
    for episode in extractEpisode.finditer(episodes):
        menu_name = episode.group(2)
        menu_link = episode.group(1)
        menu_pic = episode.group(3)
        addDirectoryItem(menu_name, {"action":"playEpisode","link":menu_link}, menu_pic, False)
    
    
    extractNextPage = re.compile("<a href=\"([^\".]*?)\" class=\"next_page\" rel=\"next\">(.*?)</a>")
    nextPage = extractNextPage.search(page)
    if nextPage is not None:
        menu_link = baseLink + nextPage.group(1)
        menu_name = nextPage.group(2)
        addDirectoryItem(menu_name, {"action":"showPlaytubeChannel","link":menu_link}, "", True)
    
    xbmcplugin.endOfDirectory(thisPlugin)


def playEpisode(link):
    page = load_page(urllib.unquote(link))
    
    extractMediaId = re.compile("var so = new SWFObject\(\"http://media.mtvnservices.com/(.*?)\",\"embeddedPlayer\", \"[0-9]*\", \"[0-9]*\", \"(.*?)\", \".*?\"\);")
    mediaId = extractMediaId.search(page).group(1)
    
    page = load_page(apiLink+mediaId)
    extractMediaXML = re.compile("<media:content duration='[0-9\.]*' .*?type='text/xml' url='(.*?)'></media:content>")
    extractMediaName = re.compile("<title>(.*?)</title>")
    mediaXML = extractMediaXML.search(page).group(1)
    mediaName = extractMediaName.search(page).group(1)
    
    page = load_page(mediaXML)
    extractRtmpUrls = re.compile("<rendition.*? height=[\"\']+([0-9]*)[\"\']+.*?>[\n\ \t]*<src>(.*?)</src>[\n\ \t]*</rendition>")
    
    streamUrl = ""
    streamHeight = 0
    
    for rtmpItem in extractRtmpUrls.finditer(page):
        if rtmpItem.group(1)>streamHeight:
            streamUrl = rtmpItem.group(2)
    
    item = xbmcgui.ListItem(mediaName, path=streamUrl)
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def playPodcast(link):
    item = xbmcgui.ListItem(path=urllib.unquote(link))
    xbmcplugin.setResolvedUrl(thisPlugin, True, item)

def load_page(url):
    print url
    req = urllib2.Request(url)
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link

def addDirectoryItem(name, parameters={}, pic="", folder=True):
    li = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=pic)
    if not folder:
        li.setProperty('IsPlayable', 'true')
    url = sys.argv[0] + '?' + urllib.urlencode(parameters)
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=li, isFolder=folder)

def remove_html_special_chars(inputStr):
    inputStr = inputStr.replace("&#8211;", "-")
    inputStr = inputStr.replace("&#8216;", "'")
    inputStr = inputStr.replace("&#8217;", "'")#\x92
    inputStr = inputStr.replace("&#8220;","\"")#\x92
    inputStr = inputStr.replace("&#8221;","\"")#\x92
    inputStr = inputStr.replace("&#8230;", "'")
   
    inputStr = inputStr.replace("&#039;", chr(39))# '
    inputStr = inputStr.replace("&#038;", chr(38))# &
    return inputStr
    
def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    
    return param
    
if not sys.argv[2]:
    mainPage()
else:
    params = get_params()
    if params['action'] == "showTV":
        showTV(params['link'])
    elif params['action'] == "showPlaytube":
        showPlaytube(params['link'])
    elif params['action'] == "showPodcast":
        showPodcast(params['link'])
    elif params['action'] == "showPlaytubeChannel":
        showPlaytubeChannel(params['link'])
    elif params['action'] == "playEpisode":
        playEpisode(params['link'])
    elif params['action'] == "playPodcast":
        playPodcast(params['link'])
    else:
        mainPage()
