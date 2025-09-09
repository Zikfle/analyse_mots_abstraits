# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-08-26
# Description: testing CHAT parser
# MIT License
# ---------------------------------------------------------

import pylangacq
import os
from tqdm import tqdm


#get working path
cur_path = os.path.abspath(os.getcwd())
data_path = os.path.join(cur_path, "French-Corpa")
data_path = 'A://Maitrise-analyse/CHILDES parser/French-Corpa/'

print('-----------------------------------------------------------')
print('Reading all the cha. files and saving it into a Python Dict')
print('-----------------------------------------------------------')

transcript_save = {}

filelist = os.listdir(data_path)
filelist.sort()
#print(filelist)

for file in tqdm(filelist[:10]):
    if file.endswith(".cha"):
        file_path = os.path.join(data_path, file)
        #print(file)

        with open(file_path, encoding="utf-8") as f:
            lines = [line for line in f if not line.startswith("%gra:")]

        try:
            reader = pylangacq.Reader.from_strs(["".join(lines)], [file_path],parallel=False)
        except ValueError as e:
            print(f"Skipping {file} due to misalignment: {e}")
            continue

        #print(reader.head())
        print(reader.headers())
        print(reader.words(by_utterances=True))
        eve_tokens = reader.tokens(by_utterances=True)
        print(eve_tokens)
        print(len(eve_tokens))
        print(len(reader.words(by_utterances=True)))



exit()

reader = pylangacq.Reader.from_dir(data_path)

print(reader.info())