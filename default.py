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
    addDirectoryItem("Games", {"action":"showGames","link":"http://www.gameone.de/games"}, "")
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
    
    showNextPage(page,"showPlaytubeChannel")
    xbmcplugin.endOfDirectory(thisPlugin)

def showNextPage(page, action):
    extractNextPage = re.compile("<a href=\"([^\".]*?)\" class=\"next_page\" rel=\"next\">(.*?)</a>")
    nextPage = extractNextPage.search(page)
    if nextPage is not None:
        menu_link = baseLink + nextPage.group(1)
        menu_name = nextPage.group(2)
        addDirectoryItem(menu_name, {"action":action,"link":menu_link}, "", True)

def showPodcast(link):
    page = load_page(urllib.unquote(link))
    
    extractPodcast = re.compile("<item>.*?<title>(.*?)</title>.*?:origLink>(.*?)</feedburner.*?</item>",re.DOTALL)
    
    for podcast in extractPodcast.finditer(page):
        menu_name = podcast.group(1)
        menu_link = podcast.group(2)
        addDirectoryItem(menu_name, {"action":"playPodcast","link":menu_link}, "", False)
    
    xbmcplugin.endOfDirectory(thisPlugin)

def showGames(link):
    #page = load_page(urllib.unquote(link))
    addDirectoryItem("Suche", {"action":"searchGame"}, "")
    addDirectoryItem("Beliebte Games", {"action":"showGamesFavorite","link":urllib.unquote(link)}, "")
    for x in range(ord("A"),ord("A")+26):
        addDirectoryItem(chr(x), {"action":"showGamesLetter","link":baseLink + "/games/by_letter/"+chr(x)}, "")
    addDirectoryItem("#", {"action":"showGamesLetter","link":baseLink + "/games/by_letter/"+"%23"}, "")
    xbmcplugin.endOfDirectory(thisPlugin)

def showGamesLetter(link):
    url = baseLink + "/games/by_letter/" + link
    page = load_page(urllib.unquote(link))
    
    extractGames = re.compile("<div class='by_letter_item'>.*?<img .*?src=\"(.*?)\".*?<a href=\"(.*?)\">(.*?)</a>",re.DOTALL)

    for gameItem in extractGames.finditer(page):
        menu_pic = gameItem.group(1)
        menu_link = gameItem.group(2)
        menu_name = gameItem.group(3)
    
        addDirectoryItem(menu_name, {"action":"showGamesLetterGame","link":menu_link}, menu_pic)
    
    showNextPage(page, "showGamesLetter")
    xbmcplugin.endOfDirectory(thisPlugin)
    
def showGamesLetterGame(link):
    page = load_page(urllib.unquote(link))
    gameCategory = re.compile("<div class='game_video_list' id='.*?'>.*?<h3>(.*?)</h3>(.*?)</ul>\n\n</div>",re.DOTALL)  
    
    gameCategoryVideo = re.compile("<li class='.*?'>.*?<img.*?src=\"(.*?)\" />.*?<h5><a href=\"(.*?)\">(.*?)</a>.*?\n</li>",re.DOTALL)
    
    for category in gameCategory.finditer(page):
        category_title = category.group(1)
        category_content = category.group(2)
        for video in gameCategoryVideo.finditer(category_content):
            video_img = video.group(1)
            video_link = video.group(2)
            video_title = category_title + " - " + video.group(3)
            addDirectoryItem(video_title, {"action":"playEpisode","link":video_link}, video_img, False)

    xbmcplugin.endOfDirectory(thisPlugin)
    
def showGamesFavorite(link):
    page = load_page(urllib.unquote(link))
    
    mostViewed = re.compile("<div id='most_viewed'>.*?</div>",re.DOTALL)
    mostViewedVideo = re.compile("<h5><a href=\"(.*?)\">(.*?)</a></h5>")
    
    mostViewedContent = mostViewed.search(page).group(0)
    
    for video in mostViewedVideo.finditer(mostViewedContent):
        addDirectoryItem(video.group(2), {"action":"showGamesLetterGame","link":video.group(1)}, "", True)
    
    xbmcplugin.endOfDirectory(thisPlugin)

def searchGame():
    keyboard = xbmc.Keyboard("")
    keyboard.doModal();
    searchString = keyboard.getText()
    searchString = searchString.strip()
    searchString = urllib.quote_plus(searchString)
    
    if searchString == "":
        return False
    
    searchUrl = "http://www.gameone.de/search/games?q=%s&tag=&user_id=" % (searchString)
    
    searchGameResult(searchUrl)

def searchGameResult(searchUrl):
    page = load_page(urllib.unquote(searchUrl))
    
    games = re.compile("<li class=''>.*?<h5><a href=\"(.*?)\">(.*?)</a></h5>.*?<img.*?src=\"(.*?)\" />.*?</li>",re.DOTALL)
    
    for game in games.finditer(page):
        video_link=game.group(1)
        video_title=game.group(2)
        video_img = game.group(3)
        addDirectoryItem(video_title, {"action":"showGamesLetterGame","link":video_link}, video_img, True)

    showNextPage(page, "searchGameResult")
    
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
    extractRtmpUrls = re.compile("<rendition.*?height=[\"\']+([0-9]*)[\"\']+.*?>[\n\ \t]*<src>(.*?)</src>[\n\ \t]*</rendition>")
    
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
    elif params['action'] == "showGames":
        showGames(params['link'])
    elif params['action'] == "showGamesLetter":
        showGamesLetter(params['link'])
    elif params['action'] == "showGamesLetterGame":
        showGamesLetterGame(params['link'])
    elif params['action'] == "showGamesFavorite":
        showGamesFavorite(params['link'])
    elif params['action'] == "searchGame":
        searchGame()
    elif params['action'] == "searchGameResult":
        searchGameResult(params['link'])
    elif params['action'] == "playEpisode":
        playEpisode(params['link'])
    elif params['action'] == "playPodcast":
        playPodcast(params['link'])
    else:
        mainPage()
