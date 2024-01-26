"""Convert a Transcriber TRS subtitle file into the WebVTT format."""

import argparse
import datetime
import re
import sys
from collections import OrderedDict
from typing import Optional
from xml.etree import ElementTree


def get_encoding(input_path: str) -> str:
    """Extract the file encoding from the XML header."""
    with open(input_path, "r", encoding="ISO-8859-1") as file:
        header = file.readline()
    return header.split('"')[-2]


def format_timecode(timecode: str):
    """Convert ssss[.sss] into hh:mm:ss.sss format."""
    time = "0" + str(datetime.timedelta(seconds=float(timecode)))[:11]
    if "." in time:
        # Add 1 or 2 zeros so the ms suffix has a length of 3
        return time + "0" * (12 - len(time))
    return time + ".000"


def generate_timestamp(start_time: str, end_time: str) -> str:
    """Generate a WebTTV-format timestamp 'hh:mm:ss.sss --> hh:mm:ss.sss'."""
    return f"{format_timecode(start_time)} --> {format_timecode(end_time)}"


def convert(
    input_path: str,
    encoding: str,
    language: Optional[str] = None,
    add_speakers: bool = False,
    preserve_noise: bool = False,
) -> str:
    """Read TRS input file and return it in WebVVT format."""
    with open(input_path, "r", encoding=encoding) as file:
        xml_parser = ElementTree.XMLParser(encoding=encoding)
        tree = ElementTree.parse(file, xml_parser)
        root = tree.getroot()

    # OrderedDict as a fallback for erroneous speaker annotations
    speaker_dict = OrderedDict()
    for speaker in root.find("Speakers").iter("Speaker"):
        speaker_dict[speaker.attrib["id"]] = speaker.attrib["name"]

    # Add file header
    vtt_lines = ["WEBVTT"]
    if language:
        vtt_lines.append(f"Language: {language}")
    vtt_lines.append("")

    # Iterate the speaker turns
    for section in root.find("Episode").iter("Section"):
        for turn in section.iter("Turn"):
            speakers = [
                speaker_dict.get(speaker, "")
                for speaker in turn.attrib.get("speaker", "").split()
            ]
            speaker_prefix = f"<v {speakers[0]}>" if speakers else ""
            start_time = turn.attrib["startTime"]
            end_time = ""
            text = ""
            for annotation in turn.iter():
                # Parent node
                if annotation.tag == "Turn":
                    continue
                # New lines are added at synchronization points
                if annotation.tag == "Sync":
                    end_time = annotation.attrib["time"]
                    if text:
                        vtt_lines.append(generate_timestamp(start_time, end_time))
                        vtt_lines.append(add_speakers * speaker_prefix + text.strip())
                        vtt_lines.append("")
                        text = ""
                    start_time = end_time
                # Update the active speaker if the turn has multiple speakers
                elif annotation.tag == "Who":
                    speaker_idx = int(annotation.attrib["nb"]) - 1
                    if speaker_idx < len(speakers):
                        speaker = speakers[speaker_idx]
                    else:
                        # Fallback to speaker metadata if ill-defined header
                        speaker = list(speaker_dict.values())[speaker_idx]
                    speaker_prefix = f"<v {speaker}>"
                # Events themselves are added only if preserve_noise == True
                elif annotation.tag == "Event":
                    if (
                        preserve_noise
                        and annotation.attrib["extent"] == "instantaneous"
                        and "/" not in annotation.attrib["desc"]
                    ):
                        desc = annotation.attrib["desc"].strip().lower()
                        text = text + f" <i>({desc})</i> "
                # Comments are dropped; discover unhandled nodes
                elif annotation.tag != "Comment":
                    raise ValueError(f"Unknown annotation node: {annotation.tag}")
                # Finally, add the tailing text (if existing)
                text = text + " " + annotation.tail.strip()
            # Handle text line at the end of turn
            if text:
                vtt_lines.append(generate_timestamp(start_time, turn.attrib["endTime"]))
                vtt_lines.append(add_speakers * speaker_prefix + text.strip())
                vtt_lines.append("")

    vtt = "\n".join(vtt_lines)

    # If --noise, patterns such as <i>(laughs)</i>  <i>(inhales)</i> are possible
    if preserve_noise:
        vtt = re.sub("  ", " ", vtt)

    return vtt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a TRS subtitle file to the WebVTT format."
    )
    parser.add_argument("input", metavar="INPUTFILE", help="Path to the input file")
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        metavar="PATH",
        help="Write output to PATH instead of STDOUT",
    )
    parser.add_argument(
        "-l",
        "--language",
        required=False,
        metavar="LANG",
        help="Add 'Language: LANG' header to output",
    )
    parser.add_argument(
        "-s",
        "--speakers",
        required=False,
        action="store_true",
        help="Add speaker metadata to applicable lines",
    )
    parser.add_argument(
        "-n",
        "--noise",
        required=False,
        action="store_true",
        help="Preserve noise such as laughter or silence",
    )
    args = parser.parse_args()

    # Conversion
    encoding = get_encoding(args.input)
    vtt = convert(args.input, encoding, args.language, args.speakers, args.noise)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(vtt)
    else:
        sys.stdout.write(vtt)
