# Master Memoir Project – Data Analysis  
**Child Acquisition of Abstract Nouns**  

> *“Studying how children learn abstract nouns such as *democracy*, *liberty*, *freedom* and other conceptual words.”*

 This repository contains the data‑analysis portion of the master’s memoir project. It processes the [FrenchCorpa](https://talkbank.org/childes/access/French/) dataset from [CHILDES](https://talkbank.org/childes/) to annotate the instance of noun in child speech where I extract the tokenisation and part‑of‑speech tags form CLAN analysis. I then produce an annotation .csv file that marks all detected nouns with it's associated annotation with various method (lemma, POS, hyperonymy, valance, imageability, phonetic form, phonetic pattern, frequency in adult speech, frequency in overheard speech, age). 

## Table of Contents

| Section | Description |
|---------|-------------|
| [Project Overview](#project-overview) | What the project is about. |
| [Data](#data) | Source, format, and privacy notes. |
| [Repository Structure](#repository-structure) | How the files are organized. |
| [Setup](#setup) | Installing dependencies. |
| [Usage](#usage) | Running the pipeline. |
| [Output](#output) | What you’ll get. |
| [License](#license) | Legal information. |
| [Contact](#contact) | Who to reach out to. |

---

## Project Overview

The core research question is: **How do children acquire and abstract nouns?**  
Abstract nouns are concepts that cannot be directly perceived by the senses (e.g., *freedom*, *love*, *justice*).  
Our dataset contains child‑spoken transcripts annotated by linguistic experts.  

The **data‑analysis** part of the project does three things:
1. **Parse the preprocessed dataset in a large .csv file** – read all the preprocessed .cha file in a folder and save the data into a .csv file where each lines is an utterance with all it's metadata (role, age ...) in a raw fashion.
2. **Extract Tokenisation & POS‑tagging from CLAN** – read the .csv dataset and parse the %mor information into different column (lemma,POS,flexion).
3. **Annotate the nouns** – read all the lines and create a new .csv dataset where each line is a flagged noun and associate to that noun (from it's lemma) the relevant variable value (hyperonymy, valance, imageability...)


**Table 1 – Overview of the variables studied in the memoir**

| Factor category             | Variable               | Variable type     |
|-----------------------------|------------------------|-------------------|
| **Independent factor**      |                        |                   |
|                             | Age of noun appearance | Continuous numeric|
| **Lexical‑specific factors**|                        |                   |
|                             | Word length            | Discrete numeric  |
|                             | Phonetic pattern       | Nominal           |
|                             | Valence                | Continuous numeric|
|                             | Degree of imageability | Continuous numeric|
|                             | Hypernym score         | Discrete numeric  |
| **Input‑related factors**   |                        |                   |
|                             | Global word frequency  | Continuous numeric|
|                             | Frequency per session  | Continuous numeric|
|                             | Activity types         | Nominal           |
| **Developmental factors**   |                        |                   |
|                             | Lexical diversity      | Continuous numeric|
|                             | Average sentence length| Continuous numeric|

*The table lists the factor categories, the individual variables measured within each category, and the type of variable (numeric / nominal, continuous / discrete).*

---

## Data


**Table 2 – Summary of the French‑language corpora used**

| Corpus      | No. of children | Age range | Total # of recorded sessions |
|-------------|-----------------|-----------|------------------------------|
| Champaud    | 1               | 1;9‑2;5   | 10                           |
| Geneva      | 2               | 1;3‑2;6   | 40                           |
| Hunkeler    | 2               | 1;6‑2;6   | 47                           |
| Kern‑French | 4               | 1;3‑2;2   | 129                          |
| Leveillé    | 1               | 2;1‑3;3   | 33                           |
| French‑Lyon | 5               | 1;0‑3;0   | 393                          |
| Palasis     | 22              | 0;7‑2;0   | 23                           |
| Paris       | 7               | 0;7‑6;3   | 230                          |
| Pauline     | 1               | 1;2‑2;6   | 33                           |
| Yamaguchi   | 1               | 1;11‑4;3  | 31                           |
| York        | 3               | 1;9‑4;3   | 107                          |
| **Total**   | 49              | 0;7‑6;3   | 1,076                        |

*Columns: Corpus name, number of children recorded, age interval, and total number of sessions recorded for all children combined.*

> **Privacy Note** – All the data used is classified as *open access* by CHILDES and is available under the Creative Commons CC BY-NC-SA 3.0 copyright license. (For more detail see [basic rules](https://talkbank.org/0share/rules.html) or [ground rules](https://talkbank.org/0share/index.html))

---

## Repository Structure

```
.
├── data #The data folder is placed outside the project repo
│   ├── data_fan_valence.csv
│   ├── data_lexique382.csv
│   ├── data_semantiqc_imagea.csv
│   └── French-Corpa
│       ├── Champaud010906x.cha
│       ├── Champaud010918.cha
│       └── … (other .cha files)
├── analyse_mots_abstraits #The git folder repo
│   ├── module
│   │   ├── __init__.py
│   │   ├── annotator.py
│   │   ├── childes_parser.py
│   │   ├── custom_panda_saver.py
│   │   └── tokenisation.py
│   ├── old_script
│   │   ├── analyse_all.py
│   │   ├── analyse_charactere.py
│   │   ... (other .py script)
│   ├── .gitignore
│   ├── LICENSE
│   ├── main.py
│   ├── README.md
│   └── TODO.md
└── results #Where the results will be saved
    ├── log.txt
    ├── french_corpa_parsed1.csv
    ├── french_corpa_token1.csv
    ├── french_corpa_annotated1.csv
    ├── child_dico1.csv
    └── over_dico1.csv
```

---

## Setup

```python
doc_path = '/Users/user_name/Documents/Maitrise-analyse' # <- In the main.py file change this line to you current file project directory
```

The project is written in **Python 3.9.21**.  
We recommend using a virtual environment (venv or conda).

```bash
# Create and activate a virtual environment (whit venv)
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate.bat    # Windows

# Install dependencies
pip install -r requirements.txt
```

```bash
# Create and activate a virtual environment (with conda)
conda create --name myenv python=3.9
conda activate myenv

# Install dependencies
pip install -r requirements.txt
```

**Dependencies** (`requirements.txt`)

``` 
nltk==3.9.1
numpy==2.3.3
pandas==2.3.2
regex==2024.11.6
tqdm==4.67.1
```
**Other optional dependencies (for old_script)**
``` 
pylangacq==0.19.1
regex==2024.11.6
rpy2==3.6.3
spacy==3.8.2
torch==2.7.0+cu128
spacy_syllables==3.0.2
``` 


## Usage

`main_script.py` is the single entry‑point that runs the three main phases of the project:

| Phase | What it does | Output file(s) |
|-------|--------------|----------------|
| **Parsing** | Reads every `.cha` file in *raw_data_folder_location*, converts the raw dialogue into a dataframe.| `french_corpa_parsed1.csv` |
| **Tokenisation** | From the parsed dataframe, splits each utterance into individual tokens. | `french_corpa_token1.csv` |
| **Annotation** | Applies the annotator to the tokenized data, producing a fully annotated corpus and two dictionaries. | `french_corpa_annotated1.csv`, `child_dico1.csv`, `over_dico1.csv` |

All results are stored under *result_folder_location*, and a `log.txt` file is appended with a short description of the run.

---

### 1.  Configure the script

Edit the **configuration section** (top of the file) to point to your directories and to enable/disable steps:

```python
# Paths ------------------------------------------------------------
data_folder_location      = 'A://Maitrise-analyse/data'
raw_data_folder_location  = 'A://Maitrise-analyse/data/French-Corpa'
result_folder_location    = 'A://Maitrise-analyse/results'

# Step toggles ------------------------------------------------------
parsing      = True      # set to False if you already have a parsed file
tokenization = True
annotation   = True

# Log label ---------------------------------------------------------
name_of_version = 'Version 1'   # used in log.txt
```

If you only want to run a specific phase, set the other flags to `False`.

---

### 2.  Run the script

From the terminal, navigate to the folder that contains `main_script.py` and execute:

```bash
python main_script.py
```

> On Windows you may need to use `py` or `python3` instead of `python` depending on your installation.

The script will create (or overwrite) the csv files in the *results* folder. Any errors during the run are printed to the console.

---

### 3.  Inspect the results

Open the resulting csv files with a spreadsheet program or a text editor:

| File | What you’ll see |
|------|-----------------|
| `french_corpa_parsed1.csv` | Raw dialogue converted to a tab‑separated format. |
| `french_corpa_token1.csv` | Same data, but each utterance split into tokens. |
| `french_corpa_annotated1.csv` | Tokens annotated with POS tags, lemmas, etc. |
| `child_dico1.csv` | Dictionary of child‑used tokens. |
| `over_dico1.csv` | Tokens that were not found in the child dictionary. |
| `log.txt` | Header with `name_of_version` and any parameter notes. |

---

### 4.  Troubleshooting

| Symptom | Likely cause | Quick fix |
|---------|--------------|-----------|
| `ModuleNotFoundError: No module named 'module.childes_parser'` | The script isn’t being run from the project root. | Run `python main_script.py` from the folder that contains the `module` package. |
| `Permissions error when writing files` | The result folder is read‑only or you lack write rights. | Verify that you have write permissions, or change *result_folder_location* to a writable path. |
| `Empty or truncated csv files` | One of the earlier steps failed silently. | Check the console output; the helper `save_string_to_file` prints any exceptions. |

---

## Output
```
id	occurence	lemma	POS	score_hyper	score_valance	score_imagea	phonetic    pattern	freq_lem_film	freq_lem_livre	freq_overheard	age
2	la soupe manger veut pas Grégoire .	soupe	n	5.75	5.73	79.76	sup	CVC	32.26	38.04	103.17007754888753	645.5
2	la soupe manger veut pas Grégoire .	manger	n	1.8333333333333333			mɑ̃ʒe	CV-CV	5.62	4.05	324.0359836373002	645.5
...
```

The annotated file (`french_corpa_annotated1.csv`) can be directly imported into statistical software (R, SPSS, Python) for frequency counts, chi‑square tests, or regression modelling.

---
 

## License

This project is licensed under the **MIT License** – see the [LICENSE](LICENSE) file for details.

---

## Contact

| Name | Email | Role |
|------|-------|------|
| Félix Thibaud | thibaud.felix@courrier.uqam.ca | Master Student |
| Marine Le Mene Guigoures | le_mene_guigoures.marine@uqam.ca | Supervisor |
| Grégoire Winterstein | winterstein.gregoire@uqam.ca | Supervisor |


Feel free to contact us for questions, suggestions, or collaboration ideas.

---