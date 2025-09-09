# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-02-09
# Description: Testing reading Wonef
# MIT License
# ---------------------------------------------------------
import os
import pandas as pd
import xml.etree.ElementTree as ET


cur_path = os.path.abspath(os.getcwd())
data_path = os.path.join(cur_path, "data")

tree = ET.parse(os.path.join(data_path, "data_wonef.xml"))  # Adjust filename
root = tree.getroot()

id, liter, hyper, defi = [], [], [], []

for synset in root.findall(".//SYNSET"):
    synset_id = synset.find("ID").text  # Get synset ID

    # Get synonyms (all LITERAL elements inside SYNONYM)
    literal = [literal.text for literal in synset.findall(".//SYNONYM/LITERAL")]
    
    # Get hyperonyms (ILR where type="hype")
    hyperonyms = [ilr.text for ilr in synset.findall(".//ILR[@type='hypernym']")]
    
    # Get definition (if present)
    definition = synset.find("DEF").text if synset.find("DEF") is not None else ""

    # Store data

    id.append(synset_id)
    liter.append(literal)
    hyper.append(hyperonyms)
    defi.append(definition)


dico = {'id' : id, 'mot' : liter, 'hyperonyme' : hyper, 'definition' : defi }

df = pd.DataFrame(dico)

dictionnaire = {}

for index, line in df.iloc[:].iterrows():
    mot = line['mot']
    if mot[0] != '_EMPTY_':
        for sens in mot:
            if sens not in dictionnaire:
                dictionnaire[sens] = 1
            else:
                dictionnaire[sens] += 1


df.to_csv('wonef_short.csv', sep = ',', encoding='utf-8')
