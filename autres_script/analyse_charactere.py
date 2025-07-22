# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-01-28
# Description: Annotation automatique des données du corpus French Corpa CHILDES
# MIT License
# ---------------------------------------------------------

import os
import pandas as pd
import re


cur_path = os.path.abspath(os.getcwd())
data_path = os.path.join(cur_path, "data")
module_path = os.path.join(cur_path, "annotation")

df = pd.read_csv(os.path.join(data_path, "data_french_corpa.csv"))

#print(df.columns)

df = df.loc[df['corpus_name'] != ('French-Lyon')]
df = df.loc[df['corpus_name'] != ('Geneva')]
all_participant = df['speaker_name']

subdf = df[['collection_id','transcript_id','corpus_name','utterance_order','speaker_role','speaker_name','gloss','target_child_age']]
subdf = subdf.sort_values(['collection_id','transcript_id','utterance_order'], ascending=[True, True, True])

regex = "[^a-zA-ZàâäæçéèêëîïôöœùûüÿÀÂÄÆÇÉÈÊËÎÏÔŒÙÛÜŸ '\+-_ʁǝəɛøɛ̃øɔɑ̃ʒʃɥìːñƭɵ]"

#regex = "[a-zA-ZàâäæçéèêëîïôöœùûüÿÀÂÄÆÇÉÈÊËÎÏÔŒÙÛÜŸ ']" # tout les charactère standard du fr + espace + apostrophe
#regex = "[+]" #plus (indique forme composé)
#regex = "[_]" #underscore (indique forme composé)
#regex = "[-]" #tiret (mot composé ou autre)
#regex = "[ʁǝəɛøɛ̃øɔɑ̃ʒʃɥ]" #transcritpion phonétique (Paris)
#regex = "[ìːñƭɵ]" #exception finale


patern=re.compile(regex)
uter_with_special = []
for index, row in df.iterrows():
    uter = row['gloss']
    coll = row['corpus_name']
    uter = str(uter)
    if(re.search(patern, uter)):
        uter_with_special.append(uter)
        uter_with_special.append(coll)

print(uter_with_special)
print(len(uter_with_special))