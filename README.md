# assimil2anki

This script creates an Anki deck from the Assimil audio lessons - each lesson is converted into a subdeck, while each sentence is placed on a separate card.
The transcripts of the sentences, along with the chapter metadata, are extracted from the mp3-files and put on the cards along with the audio.
The resulting deck is saved as a CSV file, ready for Anki to import.
All relevant sentence audio files are copied into a separate folder (ends in _anki_media) and should be copied into the Anki collection as well, in order for Anki to play the audio while reviewing the cards.

## Dependencies

- eyed3 (pip install eyed3)

## Usage

First, create a venv and install eyed3 (you can run the install.sh-script).

Then, run the script from the command line and pass the Assimil audio folder as an argument:
```
$ sh install.sh
$ .venv/bin/python assimil2anki.py <Folder with ASSIMIL audio files>
```

## Tested with

- [Dutch](https://www.assimil.com/en/with-ease/1775-het-nieuwe-nederlands-zonder-moeite-dutch-mp3-download-3135414907601.html)
- [Finnish](https://www.assimil.com/en/with-ease/1788-suomea-vaivatta-finnish-mp3-download-3135414907717.html)
- [Turkish](https://www.assimil.com/en/with-ease/1499-turkce-3135414907243.html)
