# TRS-to-VTT
This Python script converts TRS subtitle files to the simpler and more common [WebVTT](https://en.wikipedia.org/wiki/WebVTT) format.
TRS subtitles files are XML files produced by the old transcription software [Transcriber](https://trans.sourceforge.net/en/presentation.php) and [TranscriberAG](https://transag.sourceforge.net/). 

The only other script I found to convert TRS files is [geomedialab/convert-trs-srt](https://github.com/geomedialab/convert-trs-srt).
However, next to an easily fixable bug when encountering specific timecodes, it loses most temporal information when processing long segments by a single speaker.
I thus found it easier to write my own script and skip the intermediate conversion from [SubRip](https://en.wikipedia.org/wiki/SubRip) to WebVTT, which can be done, e.g., using [nwoltman/srt-to-vtt-converter](https://github.com/nwoltman/srt-to-vtt-converter).

## Requirements
Python 3.6+

There are no other dependencies unless you want to replace the vulnerable standard XML library with [defusedxml](https://pypi.org/project/defusedxml/).

## Usage

`python convert.py [-h] [-o PATH] [-l LANG] [-s] [-n] INPUTFILE`

Unless an output path is specified using `-o` or `--output`, the result will be written to stdout.

The `-l` or `--language` argument adds a language header to the file.

When using `-s` or `--speakers`, each spoken line is prefixed with `<v SPEAKER>`, if this information is annotated.

When using `-n` or `--noise`, noise events such as *(laughter)*, *(silence)*, or *(unintelligible)* are preserved.

## Limitations

The script does not handle the named entity annotations described in the [TranscriberAG manual](https://transag.sourceforge.net/index.php?content=manual#annotation_menu).
