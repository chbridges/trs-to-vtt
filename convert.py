"""Convert a Transcriber TRS subtitle file into the WebVTT format."""

import argparse
import datetime
import re
import sys
from typing import Optional
from xml.etree import ElementTree


def format_timecode(timecode: str):
    """Convert ssss[.sss] into hh:mm:ss.sss format."""
    time = "0" + str(datetime.timedelta(seconds=float(timecode)))[:11]
    if "." in time:
        # Add 1 or 2 zeros so the ms suffix has a length of 3
        return time + "0" * (12 - len(time))
    return time + ".000"


def generate_timestamp(start_time: str, end_time: str) -> str:
    """Generate a WebTTV-format timestamp 'hh:mm:ss.sss --> hh:mm:ss.sss'."""
    return "{0} --> {1}".format(format_timecode(start_time), format_timecode(end_time))


def convert(
    input_path: str,
    language: Optional[str] = None,
    add_speakers: bool = False,
    preserve_noise: bool = False,
) -> str:
    """Read TRS input file and return it in WebVVT format."""
    noise = {
        "breath": " <i>(breaths)</i> ",
        "click": " <i>(clicks tongue)</i> ",
        "cough": " <i>(coughs)</i> ",
        "ee-hesitation": " <i>(hesitates)</i> ",
        "inhale": " <i>(inhales)</i> ",
        "laugh": " <i>(laughs)</i> ",
        "laughter": " <i>(laughs)</i> ",
        "lip_smack": " <i>(smacks lips)</i> ",
        "loud_breath": " <i>(breaths loudly)</i> ",
        "mouth": " <i>(opens mouth)</i> ",
        "noise": " <i>(noise)</i> ",
        "silence": " <i>(silence)</i> ",
        "uh": " <i>(uh)</i> ",
        "uh-huh": " <i>(uh-huh)</i> ",
        "um": " <i>(um)</i> ",
        "unintelligible": " <i>(unintelligible)</i> ",
    }

    with open(input_path, "r", encoding="CP1250") as file:
        xml_parser = ElementTree.XMLParser(encoding="CP1250")
        tree = ElementTree.parse(file, xml_parser)
        root = tree.getroot()

    speaker_dict = {
        speaker.attrib["id"]: speaker.attrib["name"]
        for speaker in root.find("Speakers").iter("Speaker")
    }

    # Add file header
    vtt_lines = ["WEBVTT"]
    if language:
        vtt_lines.append("Language: {}".format(language))
    vtt_lines.append("")

    # Iterate the speaker turns
    for section in root.find("Episode").iter("Section"):
        for turn in section.iter("Turn"):
            speakers = [
                speaker_dict.get(speaker, "")
                for speaker in turn.attrib.get("speaker", "").split()
            ]
            if speakers:
                speaker_prefix = "<v {}>".format(speakers[0])
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
                    speaker_prefix = "<v {}>".format(
                        speakers[int(annotation.attrib["nb"]) - 1]
                    )
                # Events themselves are added only if preserve_noise == True
                elif annotation.tag == "Event":
                    if (
                        preserve_noise
                        and annotation.attrib["extent"] == "instantaneous"
                    ):
                        text = text + noise[annotation.attrib["desc"].lower()]
                # Comments are dropped; discover unhandled nodes
                elif annotation.tag != "Comment":
                    raise ValueError(
                        "Unknown annotation node: {}".format(annotation.tag)
                    )
                # Finally, add the tailing text (if existing)
                text = text + annotation.tail.strip()
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

    vtt = convert(args.input, args.language, args.speakers, args.noise)

    if args.output:
        with open(args.output[0], "w", encoding="CP1250") as handle:
            handle.write(vtt)
    else:
        sys.stdout.write(vtt)
