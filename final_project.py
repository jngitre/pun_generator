import nltk
from nltk.corpus import wordnet as wn
import requests
import json
import csv
import numpy as np
import pandas as pd
from numpy import genfromtxt
import random

# sound_df = pd.read_csv("UNISYN_1_3/unilex", delimiter=":", header=None)
# might not need WAN after all, would only use for improvements
assoc_df = pd.read_csv("Cue_Target_Pairs/Cue_Target_Pairs.A-B.csv")
assoc_df = pd.concat([assoc_df, pd.read_csv("Cue_Target_Pairs/Cue_Target_Pairs.C.csv")[1:]], sort=True)
assoc_df = pd.concat([assoc_df, pd.read_csv("Cue_Target_Pairs/Cue_Target_Pairs.D-F.csv")[1:]], sort=True)
assoc_df = pd.concat([assoc_df, pd.read_csv("Cue_Target_Pairs/Cue_Target_Pairs.G-K.csv")[1:]], sort=True)
assoc_df = pd.concat([assoc_df, pd.read_csv("Cue_Target_Pairs/Cue_Target_Pairs.L-O.csv")[1:]], sort=True)
assoc_df = pd.concat([assoc_df, pd.read_csv("Cue_Target_Pairs/Cue_Target_Pairs.P-R.csv")[1:]], sort=True)
assoc_df = pd.concat([assoc_df, pd.read_csv("Cue_Target_Pairs/Cue_Target_Pairs.S.csv")[1:]], sort=True)
assoc_df = pd.concat([assoc_df, pd.read_csv("Cue_Target_Pairs/Cue_Target_Pairs.T-Z.csv")[1:]], sort=True)
assoc_df.set_index("CUE", inplace=True)

def soundsLike(w1):
    # homophone key
    hom_api = 'http://api.datamuse.com/words?rel_hom=' + w1
    hom_json = requests.get(hom_api).json()
    sounds_like = [word["word"] for word in hom_json if word["word"] != w1]

    # sounds like key
    sl_api = 'http://api.datamuse.com/words?sl=' + w1
    sl_json = requests.get(sl_api).json()
    [sounds_like.append(word["word"]) for word in sl_json]
    return sounds_like

def findRelation(w1, relation = "RelatedTo", pos = "NN"):
    cn_url = 'http://api.conceptnet.io/c/en/' + w1
    cn_json = requests.get(cn_url).json()

    # traverse through all pages in the api
    pages = [cn_json]
    its = 0
    if "view" in cn_json:
        while ("nextPage" in cn_json["view"]) and (its <= 4):
            cn_url = 'http://api.conceptnet.io/' + cn_json["view"]["nextPage"]
            pages.append(requests.get(cn_url).json())
            its += 1

    # find words with the desired relation to w1
    good_words = []
    for page in pages:
        for edge in page["edges"]:
            if edge["rel"]["label"] == relation: # or edge["rel"]["label"] == "RelatedTo":
                if edge["start"]["label"] == w1: target = "end"
                else: target = "start"
                if edge[target]["language"] == 'en':
                        good_words.append(edge[target]["label"])

    # make sure words are the desired part of speech
    good_words = nltk.pos_tag(good_words)
    good_words = [tup[0] for tup in good_words if tup[1] == pos]
    good_words = list(set(good_words))
    return good_words

def howisalikeb(s2):
    s3_0_cands = findRelation(s2)
    print (s3_0_cands)
    rando = random.randint(0, len(s3_0_cands)-1)

    s3_cands = soundsLike(s3_0_cands[rando])
    print (s3_cands[:5])
    s3 = s3_cands[0]

    s1_cands = findRelation(s3)
    print (s1_cands)
    if s1_cands:
        rando_3 = random.randint(0, len(s1_cands)-1)
        s1 = s1_cands[rando_3]
    else:
        s1 = ""
        return ("No final candidates. Try again")

    return ("\nHow is a {0} like a {1}? They are both {2}.".format(s1,s2,s3))

print (howisalikeb("dog"))
