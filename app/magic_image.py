__author__ = 'Nafnlaus'
CACHE_DIR = "/tmp/imgen"

word_list = "creature|battlefield|artifact|library|magic|trample|flying|sacrifice|life|damage|vigilance|protection"

import re
import sys
import json
import os
import time
import random
import math
import hashlib
import io
import socket

import requests
#from PIL import Image
from requests.exceptions import ConnectionError

from flask import request

TMP_FILE = CACHE_DIR + "/tmp.jpg"
STORE_DIR = CACHE_DIR + "/store"
if not os.path.exists(STORE_DIR):
    os.makedirs(STORE_DIR)

copyright_check = ""
if len(sys.argv) > 1 and sys.argv[1][0].upper() == "T":
    copyright_check = "&as_rights=(cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial).-(cc_nonderived)"


def trim(list):
    s = []
    for i in list:
        if i not in s:
            s.append(i)
    return s


def fetch(query, color):
    user_ip = request.remote_addr
    copyright_check = "&as_rights=(cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial).-(cc_nonderived)"
    base_url = 'https://ajax.googleapis.com/ajax/services/search/images?' \
               'v=1.0&imgcolor=' + color + copyright_check + '&q=' + query + '&start=%d&userip=' + user_ip
    # base_url = 'https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_CSE_ID&q=flower&searchType=image&fileType=jpg&imgSize=small&alt=json'

    start = 0  # Google's start query string parameter for pagination.
    while start < 60:  # Google will only return a max of 56 results.
        r = None
        for i in range(5):
            r = requests.get(base_url % start)
            if r:
                break
        if r == None:
            continue
        loads = None
        try:
            loads = json.loads(r.text)['responseData']['results']
        except TypeError:
            continue
        if not loads:
            continue
        for image_info in loads:
            url = image_info['unescapedUrl']
            try:
                #image_r = requests.get(url)
                return url
            except ConnectionError as e:
                print('could not download %s' % url)
                continue

            # Remove file-system path characters from name.
            '''file = open(TMP_FILE, 'w')
            try:
                Image.open(io.BytesIO(image_r.content)).save(file, 'JPEG')
            except IOError as e:
                # Throw away gifs
                continue
            file.close()

            # Have we used this one before?
            md5sum = hashlib.md5(open(TMP_FILE, 'rb').read()).hexdigest()
            newpath = STORE_DIR + "/" + md5sum + ".jpg"
            if os.path.exists(newpath):
                os.unlink(TMP_FILE)  # Already used
            else:
                os.rename(TMP_FILE, newpath)
                # Be nice to Google and they'll be nice back :)
                time.sleep(1.5)
                return newpath'''

    start += 4  # 4 images per page.

    # Be nice to Google and they'll be nice back :)
    time.sleep(1.5)

    # No images found.
    return None


def find_search_terms(card):
    #print("Card:", card)
    #words = card[0][:-1].lower().split("|")
    words = card[:-1].lower().split("|")
    #print("Words:", words)
    mana = ""
    if len(words) > 1:
        mana = words[1]
    words = words[0].split(" ")
    search_words0 = []
    for i in range(len(words)):
        for j in range(len(words) - i):
            search_words0.append(words[j:len(words) - i])
    words = card[1][:-1].lower().split(" - ")
    type = words[0].split(" ")
    try:
        words = words[1].split(" ")
    except IndexError:
        words = []
    search_words1 = []
    for i in range(len(words)):
        for j in range(len(words) - i):
            search_words1.append(words[j:len(words) - i])
    if type != ["instant"] and type != ["enchantment"] and type != [
        "creature"]:
        search_words1.append(type)
    words = []
    for line in card[2:]:
        words += re.findall(r"\b(" + word_list + r")\b",
                            line[:-1].lower().replace("creatures",
                                                      "creature").replace(
                                "sacrifices", "sacrifice").replace("mana",
                                                                   "magic"))
    search_words2 = words  # []
    colors = []
    if type == "artifact":
        colors.append("orange")
    if re.search("g", mana) and re.search("w", mana):
        colors.append("yellow")
    if re.search("b", mana) and re.search("w", mana):
        colors.append("teal")
    if re.search("b", mana) and re.search("r", mana):
        colors.append("purple")
    if re.search("r", mana) and re.search("w", mana):
        colors.append("pink")
    if re.search("r", mana) and re.search("g", mana):
        colors.append("brown")
    if re.search("g", mana):
        colors.append("green")
    if re.search("b", mana):
        colors.append("blue")
        colors.append("teal")
    if re.search("d", mana):
        colors.append("black")
        colors.append("gray")
    if re.search("w", mana):
        colors.append("gray")
        colors.append("white")
    if re.search("r", mana):
        colors.append("red")
        colors.append("orange")
    colors.append("any")

    search_words0.append([])
    search_words1.append([])

    search_words0 = trim(search_words0)
    search_words1 = trim(search_words1)
    search_words2 = trim(search_words2)
    colors = trim(colors)

    search_terms = []
    for color in colors:
        for m in [5, 4, 3, 2, 1, 0]:
            for i in search_words1:
                for j in search_words0:
                    entry = i + j
                    if len(entry) < m:
                        random.shuffle(search_words2)
                        for k in search_words2:
                            entry.append(k)
                            if len(entry) >= m:
                                break
                    search_terms.append(entry + [color])

    search_terms = trim(search_terms)

    if len(search_terms) > 2:
        shift = int(math.sqrt(len(search_terms)) * 1.5) + 1
        for i in range(len(search_terms)):
            start = random.randrange(len(search_terms))
            end = start + random.randrange(-shift, shift)
            if end < 0:
                start -= end;
                end = 0
            elif end >= len(search_terms):
                start -= (end - len(search_terms) + 1)
                end = len(search_terms) - 1
            if start < 0:
                start = 0
            elif start >= len(search_terms):
                start = len(search_terms) - 1
            if start == end:
                continue
            tmp = search_terms[start]
            search_terms[start] = search_terms[end]
            search_terms[end] = tmp

    search_terms.sort(key=len, reverse=True)

    if len(search_terms) > 2:
        shift = int(math.sqrt(len(search_terms)) * 2.5) + 1
        for i in range(int(len(search_terms) / 2) + 1):
            start = random.randrange(len(search_terms))
            end = start + random.randrange(-shift, shift)
            if end < 0:
                start -= end;
                end = 0
            elif end >= len(search_terms):
                start -= (end - len(search_terms) + 1)
                end = len(search_terms) - 1
            if start < 0:
                start = 0
            elif start >= len(search_terms):
                start = len(search_terms) - 1
            if start == end:
                continue
            tmp = search_terms[start]
            search_terms[start] = search_terms[end]
            search_terms[end] = tmp

    # print(search_words0, search_words1, search_words2, colors)
    # print(search_terms)

    return search_terms

if __name__ == "__main__":
    card = sys.stdin.readlines()
    terms = find_search_terms(card)
    found = None
    for term in terms:
        color = term[-1]
        query = "+".join(term[:-1])
        found = fetch(query + '+"fantasy"+paintings+-card', color)
        if found:
            break
    if found:
        print("IMAGE:", found)
    else:
        print("ERROR: Couldn't find any images  :(")
    print()
