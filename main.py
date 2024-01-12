import time
from yt_dlp import YoutubeDL
import os
import shutil
import json
from utils import Utils,PresqueUtiles
from yt_dlp.utils import download_range_func
from contextlib import suppress
utils = Utils()
dlUtils = PresqueUtiles()

class BadVideo(Exception):
    pass

class Video:

    def __init__(self,options):
        """
        options : {
            ydlopts: {...} with cut?
            url : ...
        }
        """
       
        self.url = options['url']
        try:
            with YoutubeDL({'skip_download': True}) as ydl:
                info = ydl.extract_info(self.url, download=False)
        except Exception as e:
            raise BadVideo((e,"unable to extract infos (bad video),skipping"))
        self.title = utils.check_letters(
            str(info.get('title')), ['/', '\\', '?', '*', '>', '<', '|'])
        self.auth = str(info.get('uploader'))
        self.thumbnail = str(info.get('thumbnail'))
        temp_views = str(info.get('view_count'))
        print(temp_views)
        self.views = temp_views[:len(temp_views)%3]+' '
        for i in range(len(temp_views)%3,len(temp_views),3):
            with suppress(IndexError):
                self.views += temp_views[i:i+3]+' '
        self.views = self.views[:-1]
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
            'quiet': True,  # No output
            'extract_flat': True,  # Flats urls
        }
        content = {}
        try:    
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
        except Exception as e:
            raise BadVideo((e,"unable to extract infos (bad video),skipping"))
        if 'entries' in info:
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
        try:    
            with YoutubeDL(video.options) as ydl:
                ydl.download([video.url])
        except Exception as e:
            raise BadVideo((e,"unable to download video (bad video),skipping"))
        utils.printColor('v','Dowloaded %s'%video.title)
        if len(video.paths) > 1:
            for path in video.paths[1:]:
                new = os.path.join(path,video.options['outtmpl']['default'].split('\\')[-1]+video.format)
                shutil.copy(output_name+video.format, new)  # copy to other dirs
                utils.printColor('v',"%s copiée dans %s"%(video.title,path.split('\\')[-1]))

    def download_playlist(self,playlist : Playlist):
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
            try:
                vdobject = Video(options)
                self.download_video(vdobject)  
            except(BadVideo):
                continue
        if len(playlist.paths) > 1:   
            for path in playlist.paths[1:]:
                ndir = os.path.join(path)
                os.makedirs(ndir)
                utils.copytree(base_path, ndir)
                print(f"%s copiée dans %s"%(playlist.title,ndir))

downloader = Downloaders()

def playlist_bebou(query,options):
    assert 'cut(' not in query, "cannot cut playlist (mdrrr t qui)"
    if 'https' in query:
        playlists = [query,None]
    else:
        playlists = dlUtils.get_playlists(query)
    options['url'] = playlists[0]
    PLAYLISTS = []
    i=-1
    while i < len(playlists):
        i+=1
        options['url'] = playlists[i]
        with suppress(BadVideo):
            PLAYLISTS.append(Playlist(options))
            break
    i+=1
    while i < len(playlists):
        options['url'] = playlists[i]
        try:
            PLAYLISTS.append(Playlist(options))
        except BadVideo:
            i+=1
            continue
        pl = PLAYLISTS[0]
        utils.printColor('j',"\t  %s - %s  ----- %d videos"%(pl.auth,pl.title,len(pl.urls)))
        print("\n(next found : %s - %s "%(PLAYLISTS[1].auth,PLAYLISTS[1].title))
        print('\n\t\tDownload / go to next / change query',end='');utils.printValidation(CHANGE_KW)
        resp = str(input('>>>'))
        if resp == 'n':
            del PLAYLISTS[0]
            i+=1
            continue
        elif resp == CHANGE_KW:
            nq = input('Enter new playlist name /url(no specifier) \n>>>')#ne pas remettre VIDEO_KW etc
            playlist_bebou(query=nq,options=options)
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
    while i < len(videos):
        i+=1
        options['url'] = videos[i]
        with suppress(BadVideo):
            VIDEOS.append(Video(options))
            break
    i =1
    while i < len(videos):
        options['url'] = videos[i]
        try:
            VIDEOS.append(Video(options))
        except BadVideo:
            i+=1
            continue
        vd = VIDEOS[0]
        print('\n\n\n%s views - thumbnail/minia : %s'%(vd.views,vd.thumbnail))
        utils.printColor('j',"\t  %s - %s"%(vd.auth,vd.title))
        print('(next found : %s - %s)'%(VIDEOS[1].auth,VIDEOS[1].title))
        print('\n\t\t Download/ go to next/ change query',end='');utils.printValidation(CHANGE_KW)
        resp = str(input('>>>'))
        if resp == 'n':
            del VIDEOS[0]
            i+=1
            continue
        elif resp == CHANGE_KW:
            nq = input('Enter new video name/url(no specifier needed) \n>>>')#ne pas remettre fplaylist ou autre
            video_bebou(query=nq,options=options)
        else:
            downloader.download_video(vd)
            break
    
if __name__ == '__main__':
    with open('config.json','r') as f:
        config = json.load(f)
    
    audio_options = config['audio']
    video_options = config['video']
    SEP = config['querySep']# % base
    PLAYLIST_KW = config['playlistKW']
    VIDEO_KW = config['videoKW']#telecharge l'audio de base
    CHANGE_KW = config['newQueryKW']
    VIDEO_SAVE_DIRECTORIES = config['videoSaveDirs']# ex :local + un chemin vers drive
    AUDIO_SAVE_DIRECTORIES = config['audioSaveDirs']# video/audio dirs can be None(null) if not needed (don't want any videos for example)
    utils.forced = config['forceNames']# no spaces no #humour and shit stuff
    print(AUDIO_SAVE_DIRECTORIES,VIDEO_SAVE_DIRECTORIES)
    assert (AUDIO_SAVE_DIRECTORIES != [] and VIDEO_SAVE_DIRECTORIES != []),"No directories for video/audio"
    
    utils.printColor('v','\r\n%s'%CHANGE_KW, end='')
    print('             : to change query during dl')
    utils.printColor('v','\r%s'%SEP, end='')
    print(f'             : separateur (q1{SEP} q2{SEP} q3{SEP} etc)')
    utils.printColor('v','\r%s'%PLAYLIST_KW, end='')
    print("     : telecharger une playlist")
    utils.printColor('v','\r%s'%VIDEO_KW, end='')
    print('        : video mp4')
    utils.printColor('v','\rcut', end='')
    print('           :cut(h:m:s / h:m:s) query')# ex : cut( 10:0 / 1:11:14) inoxtag fortnite VIDEO_KW) pour telecharger le dernier live fortnite de Ines de la minute 10 à 1:11:14 de video (/ pas obligé)
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
       
print("Script finished in %s"%utils.tmnow(start))