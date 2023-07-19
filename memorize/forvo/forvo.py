from __future__ import annotations
from bs4 import BeautifulSoup
from typing import List, Dict
import requests
from os import path
import os
import re
import base64
from PyQt5.QtCore import QStandardPaths, QCoreApplication
from pathlib import Path
from urllib.parse import quote, unquote
from dataclasses import dataclass

import pdb

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
datapath = QStandardPaths.writableLocation(QStandardPaths.DataLocation)
Path(path.join(datapath, "_forvo")).mkdir(parents=True, exist_ok=True)

@dataclass
class Pronunciation:
    language: str
    headword: str
    query_word: str
    votes: int
    origin: str
    download_url: str
    is_ogg: bool
    id: int
    text: str


class Forvo:
    def __init__(self, word, lang):
        self.url = "https://forvo.com/word/" + quote(word)
        self.url_search = "https://forvo.com/search/" + quote(word) + "/en"
        self.pronunciations: List[Pronunciation] = []
        self.session = requests.Session()
        self.language = lang

    def get_pronunciations(self) -> Forvo:
        #print(f"URL[{self.url}]")
        res = requests.get(self.url, headers=HEADERS)
        if res.status_code == 200:
            page = res.text
        else:
            raise Exception("failed to fetch forvo page")
        html = BeautifulSoup(page, "lxml")
        #print(f"html[{html}]")
        available_langs_els = html.find_all(
            id=re.compile(r"language-container-\w{2,4}"))
        available_langs = [
            re.findall(
                r"language-container-(\w{2,4})",
                el.attrs["id"])[0] for el in available_langs_els]
        if self.language not in available_langs:
            return self
        #print(f"available_langs[{available_langs}]")
        for lang in available_langs_els:
            print(f"***lang:[{lang}]")
        lang_container = [
            lang for lang in available_langs_els if re.findall(
                r"language-container-(\w{2,4})",
                lang.attrs["id"])[0] == self.language][0]
        #print(f"lang_container:[{lang_container}]")
        pronunciations_els = lang_container.find_all(class_="pronunciations")

        pronunciation_items = pronunciations_els[0].find_all(
            class_="pronunciations-list")[0].find_all("li")

        word = self.url.rsplit('/', 2)[-1]
        headword_el = pronunciations_els[0].find_all('em')[0]
        headword = headword_el.find_all(text=True)[0].text
        headword = " ".join(headword.split()[:-2])

        for pronunciation_item in pronunciation_items:
            pdb.set_trace()
            if len(pronunciation_item.find_all(class_="more")) == 0:
                continue
            pronunciation_dls = re.findall(
                r"Play\(\d+,'.+','.+',\w+,'([^']+)",
                pronunciation_item.find_all(
                    id=re.compile(r"play_\d+"))[0].attrs["onclick"])
            vote_count = pronunciation_item.find_all(class_="more")[0].find_all(
                class_="main_actions")[0].find_all(
                id=re.compile(r"word_rate_\d+"))[0].find_all(class_="num_votes")[0]
            vote_count_inner_span = vote_count.find_all("span")
            if len(vote_count_inner_span) == 0:
                vote_count = 0
            else:
                vote_count = int(
                    str(re.findall(r"(-?\d+).*", vote_count_inner_span[0].contents[0])[0]))
            pronunciation_dls = re.findall(
                r"Play\(\d+,'.+','.+',\w+,'([^']+)",
                pronunciation_item.find_all(
                    id=re.compile(r"play_\d+"))[0].attrs["onclick"])
            is_ogg = False
            if len(pronunciation_dls) == 0:
                pronunciation_dl = re.findall(
                    r"Play\(\d+,'[^']+','([^']+)",
                    pronunciation_item.find_all(
                        id=re.compile(r"play_\d+"))[0].attrs["onclick"])[0]
                dl_url = "https://audio00.forvo.com/ogg/" + \
                    str(base64.b64decode(pronunciation_dl), "utf-8")
                is_ogg = True
            else:
                pronunciation_dl = pronunciation_dls[0]
                dl_url = "https://audio00.forvo.com/audios/mp3/" + \
                    str(base64.b64decode(pronunciation_dl), "utf-8")
            #data_id = int(
            #    pronunciation_item.find_all(
            #        class_="more")[0].find_all(
            #        class_="main_actions")[0].find_all(
            #        class_="share")[0].attrs["data-id"])
            username = pronunciation_item.find_all(
                class_="info", recursive=False)[0].find_all(
                    class_="ofLink")
            if len(username) == 0:
                for pronunciation_item_content in pronunciation_item.contents:

                    if not hasattr(pronunciation_item_content, "contents"):
                        continue

                    tempOrigin = re.findall(
                                "Pronunciation by(.*)",
                                pronunciation_item_content.contents[0],
                                re.S)
                                
                    if len(tempOrigin) != 0:
                        origin = tempOrigin[0].strip()
                        break
            else:
                origin = username[0].contents[0]
            pronunciation_object = Pronunciation(self.language,
                                                 headword,
                                                 word,
                                                 vote_count,
                                                 origin,
                                                 dl_url,
                                                 is_ogg,
                                                 -1, #data_id, can't obtain anymore
                                                 )

            self.pronunciations.append(pronunciation_object)
        return self

    def get_pronunciations_in_search(self) -> Forvo:
        res = requests.get(self.url_search, headers=HEADERS)
        if res.status_code == 200:
            page = res.text
        else:
            raise Exception("failed to fetch forvo page")
        html = BeautifulSoup(page, "lxml")
        
        word = self.url_search.rsplit('/', 2)[-1]
         
        pronunciations_els = html.find_all('ul', attrs={'class': re.compile('^word-play-list.*')})

        pronunciation_items = []
        for pronunciations_el in pronunciations_els:
            pronunciation_items = pronunciation_items + pronunciations_el.find_all('li', attrs = {'class': None})

        #for pronunciation_item in pronunciation_items:
        for idx, pronunciation_item in enumerate(pronunciation_items):
            try:
                pronunciation_dls = re.findall(
                    r"Play\(\d+,'.+','.+',\w+,'([^']+)",
                    pronunciation_item.find_all(
                        id=re.compile(r"play_\d+"))[0].attrs["onclick"])
            except Exception:
                #print("Error Parsing Audio")
                #print(f"{pronunciation_item}")
                continue

            is_ogg = False
            if len(pronunciation_dls) == 0:
                pronunciation_dl = re.findall(
                    r"Play\(\d+,'[^']+','([^']+)",
                    pronunciation_item.find_all(
                        id=re.compile(r"play_\d+"))[0].attrs["onclick"])[0]
                dl_url = "https://audio00.forvo.com/ogg/" + \
                    str(base64.b64decode(pronunciation_dl), "utf-8")
                is_ogg = True
            else:
                pronunciation_dl = pronunciation_dls[0]
                dl_url = "https://audio00.forvo.com/audios/mp3/" + \
                    str(base64.b64decode(pronunciation_dl), "utf-8")


            title = pronunciation_item.find_all('a', attrs = {'class': 'word'})[0].text
            #print(f"TITLE***[{title}]")
            #print(f"dl_url***[{dl_url}]")    

            pronunciation_object = Pronunciation(self.language,
                                                 "", #headword
                                                 word,
                                                 -1, #vote_count
                                                 "", #origin
                                                 dl_url,
                                                 is_ogg,
                                                 -1, #data_id, can't obtain anymore
                                                 title,
                                                 )

            self.pronunciations.append(pronunciation_object)
        return self


def fetch_audio_all(word: str, lang: str) -> Dict[str, str]:
    sounds = Forvo(word, lang).get_pronunciations().pronunciations
    if len(sounds) == 0:
        return {}
    result = {}
    for item in sounds:
        result[item.origin + "/" + item.headword] = item.download_url
    return result


def fetch_audio_best(word: str, lang: str) -> Dict[str, str]:
    sounds = Forvo(word, lang).get_pronunciations().pronunciations
    if len(sounds) == 0:
        return {}
    sounds = sorted(sounds, key=lambda x: x.votes, reverse=True)
    return {
        sounds[0].origin +
        "/" +
        sounds[0].headword: sounds[0].download_url}

def fetch_audio_in_search(word: str, lang: str) -> Dict[str, str]:
    sounds = Forvo(word, lang).get_pronunciations_in_search().pronunciations
    if len(sounds) == 0:
        return {}
    result = {}
    for item in sounds:
        result[item.text] = item.download_url
    #print(f"result[{result}]")
    return result

if __name__ == "__main__":
    print(fetch_audio_all("delicate", "en"))
    #print(fetch_audio_best("goodbye", "en"))
