import regex as re
import sys
import os
import pandas as pd
import datetime as dt
from langchain_text_splitters import RecursiveCharacterTextSplitter

patterns = {
    "preamble": re.compile(r'("id":"\d{4}")(.*?)Uhr.{0,150}(Alterspräsidentin|Alterspräsident|Vizepräsidentin|Vizepräsident|Vizekanzlerin|Vizekanzler|Präsidentin|Präsident|Kanzlerin|Kanzler).{0,50}?:', re.DOTALL), #I swear this makes sense!
    "appendix": re.compile(r'(\(Schluß der Sitzung: \d+(.|:)\d+ Uhr.?\)|\\nAnlagen zum Stenographischen Bericht|\\nAnlage 1)(.*?)("id":"\d{4})', re.DOTALL),
    "appendix_last": re.compile(r'(\(Schluß der Sitzung: \d+(.|:)\d+ Uhr.?\)|\\nAnlagen zum Stenographischen Bericht|\\nAnlage 1)(.*?)', re.DOTALL),    # Last appendix without "id" at the end
    "party_speaker": re.compile(r'\w+ \(\w+\)\s?:', re.DOTALL),                                                                                             # Generic pattern for speeches, e.g. 'Speaker (Party) :'                                           
    "party_speaker_CDU": re.compile(r'\w+ \(CDU/CSU\)\s?:', re.DOTALL),                                                                                     # Specific pattern for CDU speeches
    "party_speaker_FDP_random": re.compile(r'\w+ \(F.D.P.\)\s?:', re.DOTALL),                                                                               # For an ungodly reason the FDP was briefly referred to as F.D.P. 1999-2000. I suspect this is a conspiracy to sabotage my thesis and social science in general.
    "party_speaker_new": re.compile(r'\[\w+\]\s?', re.DOTALL),                                                                                          # New pattern for speeches after 2013. The previous pattern 'Speaker (Party) :' was replaced with 'Speaker [Party] :' in the Bundestag protocol.
    "party_speaker_CDU_new": re.compile(r'\[CDU+/CSU\]\s?:', re.DOTALL),                                                                                # Specific pattern for CDU speeches            
    "minister_speaker": re.compile(r', (Bundesminister|Bundesministerin)\s(der|für|des)', re.DOTALL),                                                   # Ministers are usually addressed with 'Bundesminister der ... i.e. Finanzen'   
    "chancellor_speaker": re.compile(r', (?:(Bundes|Vize)?[Kk]anzlerin?):', re.DOTALL),                                                                 # Chancellor speeches are usually addressed with 'Bundeskanzlerin:' or 'Vizekanzlerin:'      
    "reactions": re.compile(r'\(\w\w+ (.*?)\)', re.DOTALL),                                                                           # Reactions are usually in the form '(Applaus)', '(Beifall)', '(Zuruf)', these simple reactions are removed here
    "remarks": re.compile(r'\((?!CDU/CSU|CDU|CSU|SPD|FDP|F.D.P.|AfD|Die Linke|Bündnis 90/Die Grünen|Bündnis 90 / Die Grüne|Die Grünen|LINKE|PDS|Piraten|NPD|REP|DVU|ÖDP|Tierschutzpartei|MLPD|DKP|BP|SSW|Fraktionslos)[^(]*?:[^()]+\)', re.DOTALL) # Excludes party markers i.e. --> Joachim Gauck (CDU) : I need to keep these to identify individual speeches which
}

def documentImporter(file_path, document_id):
    """
    Imports a text file and returns its content.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            TextInhalt = file.read()
            TextClean = TextInhalt
        return TextClean
    else:
        print(f"File not found: {file_path}")
        return None
    

def dategetter(RawText):

    datelist = re.findall(r'"datum":"\d{4}-\d{2}-\d{2}"', RawText)
    date_list = []
    for n_date in datelist:
        date_str = n_date.split('"')[3]  # Extract the date string from the match
        date_list.append(date_str)

    # Only every even entry is relevant. This is the case because the ID is included in each document twice. Removing the uneven entries
    date_list = date_list[::2]
    
    return date_list


def isolate_session_content(RawText):
    '''The sequence of removing preamble (Table of content, list of appendices etc.) and appendix (Appendix, list of speakers etc.) is important.
    If the appendix is removed first, the preamble will not be removed correctly, because it relies on the presence of the appendix to identify the end of the preamble.'''
    # Remove preamble first
    textIsolated = patterns["preamble"].sub(r'\1\3', RawText)

    # Remove appendix patterns
    textIsolated = patterns["appendix"].sub(r'\4', textIsolated)
    textIsolated = patterns["appendix_last"].sub("", textIsolated)

    return textIsolated

def split_sessions_by_id(text):
    # Find all start positions of the pattern
    matches = list(re.finditer(r'"id":"\d{4}"', text))
    sessions = []
    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        sessions.append(text[start:end])
    return sessions

def reactions_remarks_processing(text):
    remarksList = re.findall(patterns["remarks"], text)
    text = re.sub(patterns["remarks"], "", text)
    text = re.sub(patterns["reactions"], "", text)
    return text, remarksList

def split_text_into_chunks(text: str, chunk_size: int = 1000, chunk_overlap: int = 100) -> list[str]:
    """
    Splits the input text into chunks of specified size with overlap.
    
    Args:
        text (str): The text to be split.
        chunk_size (int): The size of each chunk.
        chunk_overlap (int): The number of characters to overlap between chunks.
        
    Returns:
        list[str]: A list of text chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=True,
        separators=[
            patterns['party_speaker'].pattern,
            patterns['party_speaker_CDU'].pattern,
            patterns['chancellor_speaker'].pattern,
            patterns['minister_speaker'].pattern,
            patterns['party_speaker_FDP_random'].pattern,
            patterns['party_speaker_new'].pattern,
            patterns['party_speaker_CDU_new'].pattern,
        ]
    )
    
    return text_splitter.split_text(text)