# -*- coding: utf-8 -*-
# ---------------------------------------------------------
# Author: Félix Thibaud
# Created on: 2025-04-13
# Description: CHILDES parser
# MIT License
# ---------------------------------------------------------

import os
import regex as re
from tqdm import tqdm
import pandas as pd
import statistics

def parse_metadata(transcript, filename, transcript_id, participant_ids):
    '''
    Parsing one metadata from one .cha file
    into a python dict
    
    Parameters
    ----------
    transcript : 
    Parameter description
    
    Returns
    -------
    dict : all the metadata content in a dict
    dict : all the participant_id from the global parsing
    '''
    # collect all metadata lines
    raw_metadata = [line for line in transcript if line and line[0].startswith('@')]
    basic_line = ['@Begin\n','@End\n','@UTF8\n']
    participants, ids = [], []

    for line in raw_metadata:
        # Ensure the line has at least 2 elements
        if len(line) < 2:
            if line[0] not in basic_line:
                print(f"⚠️ Skipping a line in {filename} metadata")
                print('line :', line)
            continue
        tag, content = line[0], line[1]
        if tag == '@Participants:':
            participants = [p.strip() for p in content.split(',')]
        elif tag == '@ID:':
            ids.append(content.split('|'))  # should have 10 elements

    # prepare metadata dictionary
    meta = {
        'codeb': [], 'roleb': [], 'file_name': [], 'transcript_id': [],
        'participant_id': [], 'participant_name': [], 'lang': [], 'corpus': [], 'code': [],
        'age': [], 'sex': [], 'group': [], 'SES': [], 'role': [],
        'education': [], 'custom': []
    }

    for idx, participant in enumerate(participants):
        parts = participant.split()
        if len(parts) < 2 or idx >= len(ids):
            continue  # skip malformed or unmatched entries
        # assign a unique overall corpus participant_id 
        unique_name = parts[-2] + ' ' + ids[idx][1]
        
        if unique_name not in participant_ids:
            count_id = len(participant_ids) + 1
            participant_ids[unique_name] = count_id
        
        meta['codeb'].append(parts[-2])
        meta['roleb'].append(parts[-1])
        meta['file_name'].append(filename)
        meta['transcript_id'].append(transcript_id)
        meta['participant_id'].append(participant_ids[unique_name])
        meta['participant_name'].append(unique_name)

        id_fields = ids[idx] + [''] * (10 - len(ids[idx]))  # pad if missing
        (lang, corpus, code, age, sex, group, ses, role, edu, custom) = id_fields[:10]

        meta['lang'].append(lang)
        meta['corpus'].append(corpus)
        meta['code'].append(code)
        meta['age'].append(age)
        meta['sex'].append(sex)
        meta['group'].append(group)
        meta['SES'].append(ses)
        meta['role'].append(role)
        meta['education'].append(edu)
        meta['custom'].append(custom)

    return meta, participant_ids



def age_to_days(age):
    '''
    Converting the CHILDES age fromat (like 1;02;10) to days
    '''
    days = None
    if type(age) is str and age != '':
        year_month_day = age.split(';')
        year = int(year_month_day[0])
        month_day = year_month_day[1]
        if '.' in month_day:
            month_day = month_day.split('.')
            try:
                month = int(month_day[0])
            except:
                month = 0
            try:
                day = int(month_day[1])
            except:
                day = 0
        else: 
            month = 0
            day = 0
        days = (year * 365) + (month * 30.5) + day
    #else:
        #print('age : ',age)
    return days

def parse_lines(transcript, metadata, transcript_name):
    '''
    Parsing each lines from a cha. file to dataframe
    
    Parameters
    ----------
    transcript : a pre processed transcript version of a .cha file, 
    line by line, and seperated in two part 1- the tag of the line and 
    2- the content of the line
    metadata : the metadata of that .cha file as a dict
    transcript: the file name as a string

    Returns
    -------
    df : a dataframe where each line contains the line content and the metadata
    associated with it's corresponding value
    '''
    def get_target_age(meta):
        if 'Target_Child' not in meta['role']:
            return None
        ages = [age_to_days(meta['age'][i]) for i, r in enumerate(meta['role']) if r == 'Target_Child' and meta['age'][i]]
        return statistics.mean(ages) if ages else None

    # List and dict
    data, current = [], {'utterance': '', 'gra': '', 'mor': '', 'pho': '', 'act': '', 'com': '', 'sit': ''}
    code, oldtype, target_age = '', '*', get_target_age(metadata)
    tag_fields = {'%gra:','%mor:','%pho:','%act:','%com:','%sit:'}
    id_line = 0

    for type_tag, content in (l for l in transcript if len(l) == 2):
        id_line += 1
        # continuation line
        if not type_tag:
            if oldtype == '*': current['utterance'] += ' ' + content
            elif oldtype in tag_fields: current[oldtype[1:-1]] += ' ' + content
            continue

        # new speaker: save previous utterance
        if type_tag.startswith('*') and current['utterance']:
            data.append({'transcript_name': transcript_name, 'code': code, **current})
            current = {k: '' for k in current}
        
        # update current fields
        if type_tag.startswith('*'):
            code = type_tag[1:-1]
            current['utterance'] = content
        elif type_tag in tag_fields:
            current[type_tag[1:-1]] = content
        oldtype = type_tag

    # save last utterance
    if current['utterance']:
        data.append({'transcript_name': transcript_name, 'code': code, **current})

    # If no utterance found, return empty DataFrame
    if not data:  # nothing parsed
        print(f"⚠️ Skipping {transcript_name}: no speaker lines found.")
        return pd.DataFrame(columns=[
            'transcript_name', 'transcript_id', 'corpus', 'transcript_order',
            'participant_id', 'code', 'role', 'age', 'target_age', 'utterance',
            'mor', 'gra', 'pho', 'act', 'com', 'sit'
        ])

    # --- Merge metadata ---
    df = pd.DataFrame(data)
    meta_df = pd.DataFrame(metadata)
    ''' # for debugging
    if len(df) == 0:
        print(transcript)
        print("DEBUG:", transcript_name)
        print("df columns:", df.columns.tolist())
        print("meta_df columns:", meta_df.columns.tolist())
        print("data length:", len(df))
    '''
    df = df.merge(meta_df, on='code', how='left')
    df['target_age'] = target_age
    df['transcript_order'] = range(1, len(df) + 1)
    df['age'] = df['age'].apply(age_to_days)
    ''' # --- For checking the result ---

    for line in transcript:
        print(line)
    for utter in df['utterance']:
        print(utter)
    '''
    return df

def parse_chat_folder(data_path):
    '''
    Parsing each .cha file in a given folder
    
    Parameters
    ----------
    data_path : the full folder data_path as a string

    Returns
    -------
    df : a dataframe containing all the lines and associated metadata of all
    the .cha file present in the targeted folder
    '''
    print('-----------------------------------------------------------')
    print(f'Reading all the cha. files in {data_path} and saving it into a Python Dict')
    print('-----------------------------------------------------------')

    transcript_save = {}

    filelist = os.listdir(data_path)
    filelist.sort()
    print('Nb. of files : ',len(filelist))
    for file in tqdm(filelist[:]):
        if file.endswith(".cha"):
            transcript = open(os.path.join(data_path,file),'r',encoding = 'utf-8')
            transcript_lines = transcript.readlines()
            transcript_as_list = []
            for idx, line in enumerate(transcript_lines):
                line = line.split('\t')
                if len(line) == 2:
                    line[1] = re.sub('\x15.*\x15','',line[1])
                    line[1] = re.sub('\n','',line[1])
                transcript_as_list.append(line)
            transcript_save[file] = transcript_as_list

    #print(transcript_save)

    transcript_id = 0
    participant_ids = {}
    all_dfs = []

    print('---------------------------------------------------------')
    print('Parsing each .cha file into a DataFrame')
    print('---------------------------------------------------------')

    for transcript_name in tqdm(transcript_save.keys()):
        transcript_id += 1
        transcript = transcript_save[transcript_name]
        metadata , participant_ids = parse_metadata(transcript,transcript_name,transcript_id,participant_ids)
        parsed_transcript = parse_lines(transcript,metadata,transcript_name)
        all_dfs.append(parsed_transcript)

    # keep only non-empty DataFrames
    all_dfs = [df for df in all_dfs if not df.empty]
    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)
    else:
        final_df = pd.DataFrame()
    final_df.index.name = 'id'
    print(final_df)
    
    return final_df

# ---------------------------------------------------------
# Param
# ---------------------------------------------------------

run_as_test = False
saving = False
save_name = 'french_corpa_parsed1.tsv'

# run main function
if run_as_test == True:
    data_folder_location = "/Users/zikfle/Documents/Maitrise-analyse/data/French-Corpa"
    result_folder_location = 'A://Maitrise-analyse/results'

    final_df = parse_chat_folder(data_folder_location)
    print(final_df['participant_id'])
    if saving == True:
        print('---------------------------------------------------------')
        print('Saving the result in a csv file')
        print('---------------------------------------------------------')

        #saving the result
        out_file = os.path.join(result_folder_location, save_name)
        if os.path.exists(out_file):
            #  Ask the user if we should overwrite it
            answer = input(f"File '{out_file}' already exists. Overwrite? (y/n): ").strip().lower()
            if not answer.startswith('y'):
                print("Skipping save – user declined to overwrite.")
                # Optionally exit or simply skip the save step
                # sys.exit(0)   # if you really want to abort the script
            else:
                # User consented – proceed with overwrite
                final_df.to_csv(out_file, sep='\t', encoding='utf-8')
                print('-' * 50)
                print('Saving successful')
                print('-' * 50)
        else:
            final_df.to_csv(out_file, sep='\t', encoding='utf-8')

            print('---------------------------------------------------------')
            print('Saving successful')
            print('---------------------------------------------------------')
    
    else:
        print('---------------------------------------------------------')
        print('Saving set to false')
        print('---------------------------------------------------------')
    
