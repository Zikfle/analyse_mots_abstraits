# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 23:11:32 2024

@author: Zikfle
"""



from nltk.corpus import wordnet
import statistics
     


My_sysn = wordnet.synsets('cherry', None, 'eng', True)


# 1 => analyse le premier mot du syn
# 2 => analyse tout les mots du syn

task = 1

# seulement le premier syn
if task == 1:
    for sens in My_sysn:
        print(sens)
    
    My_sysn = My_sysn[2]
    print("First meaning:", My_sysn.name())
        
    print(My_sysn.definition())
    print("The Hypernym for the word is:",My_sysn.hypernyms(),'\n')
    print("The Hyponyms for the word is:",My_sysn.hyponyms(),'\n')
    print("The Hyponyms  score iss:",len(My_sysn.hyponyms()),'\n')
    print("The Hypernyms path:",My_sysn.hypernym_paths(),'\n')     
    print("The Hypernyms score is:",len(My_sysn.hypernym_paths()[0]),'\n')
    print("The min depth is:",My_sysn.min_depth(),'\n')

# pour chaque syn
elif task == 2:
    print(My_sysn,'\n')
    list_hyper = []
    list_hypo = [] 
    all_path = []
    
    for word in My_sysn[:]:
        
        My_sysn = word
        
        print("Sens:", My_sysn.name())
        print(My_sysn.definition())
        hyper = My_sysn.hypernyms()
        hypo = My_sysn.hyponyms()
        min_path = My_sysn.min_depth()
        if hyper != []:
            list_hyper.extend(My_sysn.hypernyms())
        if hypo != []:
            list_hypo.extend(My_sysn.hyponyms())
        if min_path != []:
            all_path.append(My_sysn.min_depth())
    
    
    moyenne = statistics.mean(all_path)
    print('liste des hyper : ' , list_hyper,'\n')
    print('liste des hypo : ' , list_hypo,'\n')
    print('nombre d_hyper : ' , len(list_hyper),'\n')
    print('nombre d_hypo : ', len(list_hypo),'\n')
    print('liste depth : ', all_path,'\n')
    print('moyenne de path : ', moyenne)
    
    
    