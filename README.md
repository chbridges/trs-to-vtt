# TRS-to-WebVTT
This Python script converts TRS subtitle files to the simpler and more common [WebVTT](https://en.wikipedia.org/wiki/WebVTT) format.
TRS subtitles files are XML files produced by the old transcription software [Transcriber](https://trans.sourceforge.net/en/presentation.php) and [TranscriberAG](https://transag.sourceforge.net/). 

The only other script I found to convert TRS files is [geomedialab/convert-trs-srt](https://github.com/geomedialab/convert-trs-srt).
However, next to an easily fixable bug when encountering specific timecodes, it loses most temporal information when processing long segments by a single speaker.
I thus found it easier to write my own script and skip the intermediate conversion from [SubRip](https://en.wikipedia.org/wiki/SubRip) to WebVTT, which can be done, e.g., using [nwoltman/srt-to-vtt-converter](https://github.com/nwoltman/srt-to-vtt-converter).

The script does not handle the named entity annotations described in the [TranscriberAG manual](https://transag.sourceforge.net/index.php?content=manual#annotation_menu).

## Requirements
Python 3.6+

There are no other dependencies unless you want to replace the vulnerable standard XML library with [defusedxml](https://pypi.org/project/defusedxml/).

## Usage

`python convert.py [-h] [-o PATH] [-l LANG] [-s] [-n] INPUTFILE`

Unless an output path is specified using `-o` or `--output`, the result will be written to stdout.

The `-l` or `--language` argument adds a language header to the file.

When using `-s` or `--speakers`, each spoken line is prefixed with `<v SPEAKER>`, if this information is annotated.

When using `-n` or `--noise`, noise events such as *(laughter)*, *(silence)*, or *(unintelligible)* are preserved.

## Example

Input TRS file `example.trs` created with [Transcriber](https://trans.sourceforge.net/en/presentation.php):

```
<?xml version="1.0" encoding="ISO-8859-1"?>
<!DOCTYPE Trans SYSTEM "trans-14.dtd">
<Trans scribe="(unknown)" audio_filename="18061-006" version="1" version_date="020301">
<Speakers>
<Speaker id="spk1" name="interviewer" check="no" dialect="native" accent="" scope="local"/>
<Speaker id="spk2" name="interviewee" check="no" dialect="native" accent="" scope="local"/>
</Speakers>
<Episode>
<Section type="report" startTime="0" endTime="902.624">
<Turn speaker="spk1" startTime="0" endTime="15.665">
<Sync time="0"/>

<Sync time="9.037"/>
survivor is Abraham [Bommer] the date is August fourteenth nineteen ninety six
</Turn>
<Turn speaker="spk2" startTime="15.665" endTime="34.685">
<Sync time="15.665"/>
you know something I forgot to mention is about
<Sync time="20.3"/>
a man by the name of Captain [Jello]
<Sync time="23.99"/>
he was almost the head man from the
<Event desc="EE-HESITATION" type="noise" extent="instantaneous"/>
 Czechoslovakia army
<Sync time="28.385"/>
he came over there according my knowledge is
<Sync time="32.56"/>
with his wife because his wife was Jewish
</Turn>

[...]
```

Simple WebVTT output: `python convert.py example.trs`

```
WEBVTT

00:00:09.037 --> 00:00:15.665
survivor is Abraham [Bommer] the date is August fourteenth nineteen ninety six

00:00:15.665 --> 00:00:20.300
you know something I forgot to mention is about

00:00:20.300 --> 00:00:23.990
a man by the name of Captain [Jello]

00:00:23.990 --> 00:00:28.385
he was almost the head man from the Czechoslovakia army

00:00:28.385 --> 00:00:32.560
he came over there according my knowledge is

00:00:32.560 --> 00:00:34.685
with his wife because his wife was Jewish

[...]
```

WebVTT output with language, speaker, and noise info: `python convert.py example.trs --language en --speaker --noise`
```
WEBVTT
Language: en

00:00:09.037 --> 00:00:15.665
<v interviewer>survivor is Abraham [Bommer] the date is August fourteenth nineteen ninety six

00:00:15.665 --> 00:00:20.300
<v interviewee>you know something I forgot to mention is about

00:00:20.300 --> 00:00:23.990
<v interviewee>a man by the name of Captain [Jello]

00:00:23.990 --> 00:00:28.385
<v interviewee>he was almost the head man from the <i>(ee-hesitation)</i> Czechoslovakia army

00:00:28.385 --> 00:00:32.560
<v interviewee>he came over there according my knowledge is

00:00:32.560 --> 00:00:34.685
<v interviewee>with his wife because his wife was Jewish

[...]
```
