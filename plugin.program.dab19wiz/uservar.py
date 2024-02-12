import xbmcaddon

addon_id = xbmcaddon.Addon().getAddonInfo('id')

'''#####-----Build File-----#####'''
buildfile = 'http://dabutcher.org/19/test.xml'

'''#####-----Notifications File-----#####'''
notify_url  = 'http://dabutcher.org/19/notify19.txt'

'''#####-----Excludes-----#####'''
excludes  = [addon_id, 'packages', 'backups', 'plugin.video.whatever']
