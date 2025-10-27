from pathlib import Path
import re
import shutil
import sys

import eyed3


try:
    assimil_audiofiles = Path(sys.argv[1])
    if not assimil_audiofiles.exists():
        print(f"ERROR: Folder {assimil_audiofiles} does not exist!")
        sys.exit(1)
except IndexError:
    print(f"USAGE: {Path(__file__).name} <Folder with ASSIMIL audio files>")
    sys.exit(1)

metadata = {}
rows = []
media_folder_created = False
media_folder = ""

lesson_files = sorted(assimil_audiofiles.glob("L*/*.[mM][pP]3"))
total_mp3_files = len(lesson_files)
lesson_mp3_files = 0
translate_title_mp3_files = 0
skip_translate_files = False
used_mp3_files = 0

for path in lesson_files:
    if path.stem.upper().startswith("L"):
        # complete lesson files
        lesson_mp3_files += 1
        continue

    # extract information from mp3-tag
    audiofile = eyed3.load(path)
    album = audiofile.tag.album.replace(" ", "-")
    track, text = audiofile.tag.title.split("-", maxsplit=1)
    if track == "S00TITLE":
        track = "S00"
        text = "TITLE-" + text
    artist = audiofile.tag.artist
    lesson = re.search(r"(L\d{3})", album).group(0)
    # print(album, track, text, artist, lesson)

    if lesson not in metadata:
        metadata[lesson] = {
            "sentences": {},
            "translations": {},
            "conversations": {},
            "lesson_name": {},
        }

    if not media_folder_created:
        media_folder = Path(artist.replace(" ", "-") + "_anki_media")
        media_folder.mkdir(exist_ok=True)
        media_folder_created = True

    new_filename = Path(album + "-" + path.name)
    track_type = track[0].upper()

    if track_type == "N":
        metadata[lesson]["lesson_number"] = text.strip().title()
    elif re.search("(TITLE|TTTLE|TITLLE)", text):
        title, text = text.split("-", maxsplit=1)
        text = text.strip().title()
        metadata[lesson]["lesson_title"] = text
    elif re.search("^TRANSLATE", text):
        title, text = text.split("-", maxsplit=1)
        text = text.strip().title()
        metadata[lesson]["translate_title"] = text
        if skip_translate_files:
            translate_title_mp3_files += 1
            continue
        # keep the first translate file to hear the audio
        skip_translate_files = True
    elif re.search("^CONVERSATION", text):
        # TODO strip CONVERSATION from the text
        metadata[lesson]["conversation_title"] = text

    text = text.strip()
    if track_type == "N":
        text = text.title()

    labels = {
        "N": "lesson_name",
        "S": "sentences",
        "T": "translations",
        "X": "conversations",
    }
    label = labels[track_type]
    track_number = int(track[1:])

    if track_number not in metadata[lesson][label]:
        metadata[lesson][label][track_number] = {}
    metadata[lesson][label][track_number]["text"] = text
    metadata[lesson][label][track_number]["filename"] = new_filename

    # copy file with new filename
    shutil.copyfile(path, media_folder / new_filename)
    used_mp3_files += 1


for lesson, content in metadata.items():
    if "lesson_title" not in content:
        # turkish lesson 71 does not have a lesson title in the mp3 tags
        content["lesson_title"] = content["lesson_number"]

    deck = artist
    l = [deck, lesson, content["lesson_number"], content["lesson_title"]]

    for _, sentence in content["lesson_name"].items():
        audio: str = f"[sound:{sentence['filename']}]"
        sentence: str = sentence["text"]
        rows.append([*l, sentence, audio, "", ""])

    for i, sentence in content["sentences"].items():
        audio: str = f"[sound:{sentence['filename']}]"
        sentence: str = sentence["text"]
        rows.append([*l, sentence, audio, str(i), ""])

    for i, sentence in content["translations"].items():
        audio: str = f"[sound:{sentence['filename']}]"
        sentence: str = sentence["text"]
        rows.append([*l, sentence, audio, str(i), content["translate_title"]])

    for i, sentence in content["conversations"].items():
        audio: str = f"[sound:{sentence['filename']}]"
        sentence_title: str = content.get("conversation_title", "")
        sentence: str = sentence["text"]
        rows.append([*l, sentence, audio, str(i), sentence_title])

# write csv
# documentation: https://docs.ankiweb.net/importing/text-files.html#file-headers
csv_filename = f"{artist.replace(' ', '-')}.csv"
with open(csv_filename, "w") as f:
    f.write("#separator:Tab\n")
    f.write("#notetype:Assimil\n")
    f.write("#deck column:1\n")
    f.write("#tags column:2\n")

    for row in rows:
        f.write("\t".join(row) + "\n")

print(
    f"copied {used_mp3_files}, ignored {lesson_mp3_files} lesson files and {translate_title_mp3_files} translation title files (total: {used_mp3_files + lesson_mp3_files + translate_title_mp3_files}). All mp3 files in folder: {total_mp3_files}"
)
print(f"You can now import {csv_filename} into Anki.")
print(
    f"You need to copy the files from {media_folder} into your Anki collection as well."
)
print("Please visit https://docs.ankiweb.net/files.html for more information.")
