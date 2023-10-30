from enum import StrEnum
from pathlib import Path
import re
import shutil
import sys

import eyed3


try:
    assimil_audiofiles = Path(sys.argv[1])
except IndexError:
    print(f"USAGE: {Path(__file__).name} <Folder with ASSIMIL audio files>")
    sys.exit(1)

lesson_files = sorted(assimil_audiofiles.glob('L*/*.[mM][pP]3'))
metadata = {}
rows = []
media_folder_created = False
media_folder = ''

class Type(StrEnum):
    SENTENCE = 'sentences'
    EXERCISE = 'exercises'
    TITLE = 'title'
    @classmethod
    def from_string(cls, s):
        s = s.upper()
        if s.startswith('S'):
            return cls('sentences') 
        elif s.startswith('T'):
            return cls('exercises') 
        elif s.startswith('N'):
            return cls('title') 

for path in lesson_files:

    # extract information from mp3-tag
    audiofile = eyed3.load(path)
    album = audiofile.tag.album.replace(' ', '-')
    sentence = audiofile.tag.title[4:]
    artist = audiofile.tag.artist
    lesson_nr = 'NA'
    m = re.search('(L\d{3})', audiofile.tag.album)
    if m is not None:
        lesson_nr = m.group(0)
    else:
        pass
        # TODO Error

    if lesson_nr not in metadata:
        metadata[lesson_nr] = {'sentences': {}, 'lesson_number': '', 'lesson_name': '', 'exercises': {}}

    if not media_folder_created:
        media_folder = Path(artist.replace(' ', '-') + '_anki_media')
        media_folder.mkdir(exist_ok=True)
        media_folder_created = True

    type = Type.from_string(path.stem)

    if type == Type.TITLE:

        metadata[lesson_nr]['lesson_number'] = audiofile.tag.title.split('-')[1].capitalize()

    elif type == Type.SENTENCE or type == Type.EXERCISE:

        # some files have typos
        t = path.stem.upper()
        if 'TITLE' in t or 'TTTLE' in t or 'TITLLE' in t:
            metadata[lesson_nr]['lesson_name'] = audiofile.tag.title.split('-')[-1]
        elif 'TRANSLATE' in t:
            metadata[lesson_nr]['translate_name'] = audiofile.tag.title.split('-')[-1].capitalize()
        else:
            i = int(t[1:])
            new_filename = Path(album + '-' + path.name)

            if i not in metadata[lesson_nr][type]:
                metadata[lesson_nr][type][i] = {}
            metadata[lesson_nr][type][i]['text'] = sentence
            metadata[lesson_nr][type][i]['filename'] = new_filename

            # copy file with new filename
            shutil.copyfile(path, media_folder / new_filename)

for lesson, content in metadata.items():

    for i, sentence in content['sentences'].items():
        question = f"{lesson} - {content['lesson_name']} ({i})<br><br>[sound:{sentence['filename']}]"
        answer = f"{sentence['text']}"
        rows.append([question, answer, f"{artist}::{lesson[1:]} - {content['lesson_number']}"])

    for i, sentence in content['exercises'].items():
        question = f"{lesson} - {content['lesson_name']} ({content['translate_name']} {i})<br><br>[sound:{sentence['filename']}]"
        answer = f"{sentence['text']}"
        rows.append([question, answer, f"{artist}::{lesson[1:]} - {content['lesson_number']}"])

# write csv
# documentation: https://docs.ankiweb.net/importing/text-files.html#file-headers
with open(f"{artist.replace(' ', '-')}.csv", 'w') as f:
    f.write('#separator:Tab\n')
    f.write('#html:true\n')
    f.write('#notetype:Basic\n')
    f.write('#deck column:3\n')

    for row in rows:
        f.write('\t'.join(row) + '\n')

# copy files from media_folder into collection
# see https://docs.ankiweb.net/files.html
