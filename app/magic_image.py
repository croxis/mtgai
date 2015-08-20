__author__ = 'Nafnlaus'
CACHE_DIR = "/tmp/imgen"

word_list = "creature|battlefield|artifact|library|magic|trample|flying|sacrifice|life|damage|vigilance|protection|spirit|arcane"

import re
import sys
import json
import os
import time
import random
import math

import requests

from flask import request

from . import app

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
            if i:
                s.append(i)
    return s


def fetch(query, color):
    query.replace(" ", "+")
    user_ip = request.remote_addr
    if user_ip == '127.0.0.1':
        user_ip = json.loads(requests.get("http://jsonip.com").text)["ip"]
    copyright_check = "&as_rights=(cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial).-(cc_nonderived)"

    base_url = 'https://ajax.googleapis.com/ajax/services/search/images?' \
               'v=1.0&imgcolor=' + color + copyright_check + '&q=' + query + '&start=%d&userip=' + user_ip
    # base_url = 'https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=YOUR_CSE_ID&q=flower&searchType=image&fileType=jpg&imgSize=small&alt=json'

    start = 0  # Google's start query string parameter for pagination.
    #while start < 60:  # Google will only return a max of 56 results.
    if True:
        try:
            r = requests.get(base_url % start)
        except TypeError:
            app.logger.error("Unable to get url: " + base_url + ' | ' + str(start))
            return
        # Be nice to Google and they'll be nice back :)
        time.sleep(1.5)
        '''r = None
        for i in range(5):
            print("URL:", base_url % start)
            r = requests.get(base_url % start)
            start += 4  # 4 images per page.
            time.sleep(1.5)
            if r:
                break'''
        if r == None:
            #continue
            return
        loads = None
        try:
            loads = json.loads(r.text)['responseData']['results']
        except TypeError:
            #continue
            return
        if not loads:
            #continue
            return
        for image_info in loads:
            url = image_info['unescapedUrl']
            return url
    # No images found.
    return None


def find_search_terms(card):
    mana = card.cost.format().lower()
    card_text = card.text.text.replace("@", "").replace("\\", "").replace("$", "").replace(".", "").replace(',', '').replace(':', '')
    words = list(filter(None, card_text.split(" ")))[:30]
    search_words0 = []
    for i in range(len(words)):
        for j in range(random.randint(0, len(words) - i)):
            search_words0.append(words[j:len(words) - i])
    card_type = card.types
    search_words1 = []
    for i in range(len(words)):
        for j in range(random.randint(0,len(words) - i)):
            search_words1.append(words[j:len(words) - i])
    search_words0.append(card_type)
    search_words1.append(card_type)
    words = []
    for line in card.text.text.split("\\"):
        words += re.findall(r"\b(" + word_list + r")\b",
                            line[:-1].lower().replace("creatures",
                                                      "creature").replace(
                                "sacrifices", "sacrifice").replace("mana",
                                                                   "magic"))
    search_words2 = words  # []
    colors = []
    if card_type == "artifact":
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
                    if len(entry) == m:
                        search_terms.append(entry + [color])
    search_terms = trim(search_terms[:1000])

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
