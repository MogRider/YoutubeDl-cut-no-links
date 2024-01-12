import time
from yt_dlp import YoutubeDL
import os
import shutil
import json
from utils import Utils,PresqueUtiles
from yt_dlp.utils import download_range_func

utils = Utils()
dlUtils = PresqueUtiles()

class Video:

    def __init__(self,options):
        """
        options : {
            ydlopts: {...} with cut?
            url : ...
        }
        """
       
        self.url = options['url']
        with YoutubeDL({'skip_download': True}) as ydl:
            info = ydl.extract_info(self.url, download=False)
        
        self.title = utils.check_letters(
            str(info.get('title')), ['/', '\\', '?', '*', '>', '<', '|'])
        self.auth = str(info.get('uploader'))
        self.thumbnail = str(info.get('thumbnail'))
        self.views = int(info.get('view_count'))
        self.options = options['ydloptions']
        self.paths = options['paths']
        self.format = options['format']

class Playlist:
    
    def __init__(self,options):
        """
        options : {
            ydlopts: {...}
            url : ...
            path : dlpaths
        }
        """
        self.url = options['url']
        ydl_opts = {
            'quiet': True,  # Désactiver la sortie console
            'extract_flat': True,  # Récupérer toutes les URLs à plat
        }
        content = {}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(self.url, download=False)
        if 'entries' in info:
            # Si la playlist contient des vidéos
            self.urls = [entry['url'] for entry in info['entries']]
        else:
            print("Aucune vidéo trouvée dans la playlist.")
            return False
        self.title = utils.check_letters(
            str(info.get('title')), ['/', '\\', '?', '*', '>', '<', '|'])
        self.auth = str(info.get('uploader'))
        self.options = options['ydloptions']
        self.paths = options['paths']
        self.format = options['format']
        
class Downloaders:
    def __init__(self):
        pass

    def download_video(self,video : Video) -> None:
        dir = video.paths[0]
        output_name = os.path.join(dir, video.title)
        video.options['outtmpl'] =  output_name
        with YoutubeDL(video.options) as ydl:
            ydl.download([video.url])#path dans video.options
        utils.printColor('v','Dowloaded %s'%video.title)
        if len(video.paths) > 1:
            for path in video.paths[1:]:
                new = os.path.join(path,video.options['outtmpl']['default'].split('\\')[-1]+video.format)
                shutil.copy(output_name+video.format, new)  # le copier dans le pc
                utils.printColor('v',"%s copiée dans %s"%(video.title,path.split('\\')[-1]))

    def download_playlist(self,playlist : Playlist):
        #meme format option (url playlist)
        videos = playlist.urls
        for i in range (len(playlist.paths)):
            playlist.paths[i] =  os.path.join(playlist.paths[i],playlist.title)
        print(playlist.paths)
        base_path = playlist.paths[0]
        options = {'ydloptions' : utils.merge_dicos(playlist.options,{'outtmpl' : base_path},subdict=False), 'paths' : [base_path]}
        os.makedirs(base_path)
        for video in videos:
            options['url'] = video
            print('options avant : ',options)
            vdobject = Video(options)
            self.download_video(vdobject)  
        if len(playlist.paths) > 1:   
            for path in playlist.paths[1:]:
                ndir = os.path.join(path)
                os.makedirs(ndir)
                utils.copytree(base_path, ndir)
                print(f"%s copiée dans %s"%(playlist.title,ndir))

downloader = Downloaders()

def playlist_bebou(query,options):
    assert 'cut(' not in query, "peut pas cut une playlist (mdrrr t qui)"
    if 'https' in query:
        playlists = [query,None]
    else:
        playlists = dlUtils.get_playlists(query)
    options['url'] = playlists[0]
    PLAYLISTS = []
    PLAYLISTS.append(Playlist(options))
    i =1
    while True:
        options['url'] = playlists[i]
        PLAYLISTS.append(Playlist(options))
        pl = PLAYLISTS[0]
        utils.printColor('j',"\t  %s - %s  ----- %d videos"%(pl.auth,pl.title,len(pl.urls)))
        print("\n(prochaine ds la recherche : %s - %s "%(PLAYLISTS[1].auth,PLAYLISTS[1].title))
        print('\n\t\tDownload / go to next / change query',end='');utils.printValidation(CHANGE_KW)
        resp = str(input('>>>'))
        if resp == 'n':
            del PLAYLISTS[0]
            i+=1
            continue
        elif resp == CHANGE_KW:
            nq = input('Enter new playlist name /url \n>>>')
            playlist_bebou(nq)
        downloader.download_playlist(pl)
        break
    
def video_bebou(query,options):
    if 'cut(' in query:
        cut,query = query.split(')')[:2]
        start,end = utils.parse_cut(cut)
        print(start,end)
        start,end = utils.convsec(start),utils.convsec(end)
        assert start < end,"start must be < to end"
        print(start,end)
        options['ydloptions']['download_ranges'] = download_range_func(chapters=None,ranges=[[start,end]])
        options['ydloptions']['force_keyframes_at_cuts'] = True
    if 'https' in query:
        videos = [query,None]
    else:
        videos = dlUtils.get_videos(query)
    options['url'] = videos[0]
    VIDEOS = []
    VIDEOS.append(Video(options))
    i =1
    while True:
        options['url'] = videos[i]
        VIDEOS.append(Video(options))
        vd = VIDEOS[0]
        print('\n\n\n%d views - minia : %s'%(vd.views,vd.thumbnail))
        utils.printColor('j',"\t  %s - %s"%(vd.auth,vd.title))
        print('(prochaine dans la recherche : %s - %s)'%(VIDEOS[1].auth,VIDEOS[1].title))
        print('\n\t\t Download/ go to next/ change query',end='');utils.printValidation(CHANGE_KW)
        resp = str(input('>>>'))
        if resp == 'n':
            del VIDEOS[0]
            i+=1
            continue
        elif resp == CHANGE_KW:
            nq = input('Enter new playlist name /url \n>>>')
            video_bebou(nq)
        else:
            downloader.download_video(vd)
            break
    
if __name__ == '__main__':
    with open('config.json','r') as f:
        config = json.load(f)
    
    audio_options = config['audio']
    video_options = config['video']
    SEP = config['querySep']# % de base
    PLAYLIST_KW = config['playlistKW']
    VIDEO_KW = config['videoKW']#telecharge l'audio de base
    CHANGE_KW = config['newQueryKW']
    VIDEO_SAVE_DIRECTORIES = config['videoSaveDirs']# ex :local + un chemin vers drive
    AUDIO_SAVE_DIRECTORIES = config['audioSaveDirs']# meme chose pour les audios
    utils.forced = config['forceNames']# remplacer les espaces dans le fichier de sortie et enlever les #...
    
    utils.printColor('v','\r\n%s'%CHANGE_KW, end='')
    print('             : to change query during dl')
    utils.printColor('v','\r%s'%SEP, end='')
    print(f'             : separateur (q1{SEP} q2{SEP} q3{SEP} etc)')
    utils.printColor('v','\r%s'%PLAYLIST_KW, end='')
    print("     : telecharger une playlist")
    utils.printColor('v','\r%s'%VIDEO_KW, end='')
    print('        : video mp4')
    utils.printColor('v','\rcut', end='')
    print('           :cut(h:m:s / h:m:s) query')# ex : cut( 10:0 / 1:11:14) inoxtag fortnite VIDEO_KW) pour telecharger le dernier live fortnite de Ines de la minute 10 à 1:11:14 de video (/ pas obligé))(gadget mais bon stylé ?)
    utils.printColor('b','\n\tSearch for a Video | Enter URL')
    
    queries = str(input(">>>"))
    queries = queries.split(SEP)
    start = time.time()
    
    options = {}
    for query in queries:
        
        if VIDEO_KW in query:
            query = query.replace(VIDEO_KW,'')
            options['ydloptions'] = video_options
            options['paths'] = VIDEO_SAVE_DIRECTORIES
            options['format'] = '.mp4'
        else:
            options['ydloptions'] = audio_options
            options['paths'] = AUDIO_SAVE_DIRECTORIES
            options['format'] = '.mp3'
        
        if PLAYLIST_KW in query:
            query = query.replace(PLAYLIST_KW,'')
            playlist_bebou(query,options)

        else:
            video_bebou(query,options)   
       
print("Script finished in %d"%utils.tmnow(start))