import os
import requests as rq
import shutil
import re
from colorama import Fore, Style
import time


class Utils:

    def __init__(self):

        self.colors = {
        'v' : Fore.GREEN,
        'r' : Fore.RED,
        'b' : Fore.BLUE,
        'w' : Fore.WHITE,
        'j' : Fore.YELLOW,
    } 
        self.change_keys = None
        
    @staticmethod
    def printValidation(ckw):
        print('['+Fore.GREEN,'o',Style.RESET_ALL,'/',Fore.RED,'n',Style.RESET_ALL,'/'+ckw+']',sep='')
        
    def printColor(self,color,*args,end='\n'):
        print(self.colors[color],*args,Style.RESET_ALL,end=end)
    
        # enlever les doublons d une liste
    @staticmethod
    def removeDb(liste):
        filt = []
        seen = set()
        for item in liste:
            if item not in seen:
                filt.append(item)
                seen.add(item)
        return filt
    # print en rouge
    @staticmethod
    def copytree(src: str, dst: str, symlinks=False, ignore=None) -> None:
        # copier un dossier
        for item in os.listdir(src):
            s = os.path.join(src, item)
            d = os.path.join(dst, item)
            if os.path.isdir(s):
                shutil.copytree(s, d, symlinks, ignore)
            else:
                shutil.copy2(s, d)
    
    @staticmethod
    def check_letters(word,letters: list | tuple | str, rp=False):
        # remplacer si les titres de videos ne sont pas valides pour les fichiers windows (ou autre utilisation)
        for letter in letters:
            if letter in word:
                word = word.replace(letter, '')
        #remove space & #...
        if rp:
            word = word.replace(' ','_')
            if '#' in word:
                word = word[:re.search('#',word).start()]
                
        return word
    
    @staticmethod
    def convsec(time: int | float | str) -> int | str:
            # decimal to h:m:s ou l'inverse
            if isinstance(time, str):
                parts = time.split(':')
                hours = int(parts[-3]) if len(parts) > 2 else 0
                minutes = int(parts[-2]) if len(parts) > 1 else 0
                seconds = int(parts[-1])
                ntime = hours * 3600 + minutes * 60 + seconds
            elif isinstance(time, int) | isinstance(time, float):
                time = int(time)
                h = time // 3600
                m = (time-h*3600) // 60
                s = str(time-m*60-h*3600).zfill(2)
                ntime = f'{str(h).zfill(2)}:{str(m).zfill(2)}:{s}'
            return ntime

    def tmnow(self,st: float):
        return self.convsec(time.time() - st)    

    @staticmethod    
    def latest_file(dir):
        return [[os.path.join(dir, i), os.path.getmtime(
        os.path.join(dir, i))] for i in os.listdir(dir)][-1][0]
    @staticmethod
    def merge_dicos(dico,*dicos,subdict=True):
        """
        dico de base et les autres à fusionner, 
        subdict : si les clé se mettent en direct dico[clé] ou si sous dico dico[dic[clé]],
        dicos : [dictionnaire,nom](plus simple)
        """
        if subdict:
            for dic,name in dicos:
                for clé in dic.keys():
                    dico[name][clé] = dic[clé]
        else:
            for dic in dicos:
                for clé in dic.keys():
                    dico[clé] = dic[clé]
        return dico
    @staticmethod
    def parse_cut(query):
        start,end =  re.findall(r'\b(?:\d+:\d+:\d+|\d+(?::\d+)?(?::\d+)?)\b',query)[:2]
        return start,end

utils = Utils()
class PresqueUtiles:
    @staticmethod
    def get_playlists(query):
        r = rq.get(f"https://www.youtube.com/results?search_query= \
        {query}&sp=EgIQAw%253D%253D").text
        # recherche de la query
        links = []
        # chercher les videos id issus de la recherche et les mettre sous forme de liens
        for match in re.finditer("\"playlistId\":", r):
            linkoo = r[match.end():match.end()+100].split("\"")
            links.append(f"https://www.youtube.com/playlist?list={linkoo[1]}")
        # url (meme taille)
        links= utils.removeDb(links)
    
        return links#[lien1,2,....]
    
    @staticmethod
    def get_videos(query):
        r = rq.get(f"https://www.youtube.com/results?search_query={query}").text
        # recherche de la query
        ids = []
        for match in re.finditer("\"videoId\":", r):
            ids.append(r[match.end():match.end()+50].split("\"")[1])
        # chercher les videos id issus de la recherche et les mettre sous forme de lien
        # url (meme taille)
        links = utils.removeDb(
            [f"https://youtu.be/{id}" for id in ids])
        return links# [lien1,lien2...]
