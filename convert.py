import argparse
import sys
import xml.etree.ElementTree as ET


def convert(
    input_path: str,
    language: str = "",
    add_speakers: bool = False,
    preserve_noise: bool = False,
) -> str:
    """Read and parse input file.

    :param input_file: Path to the input TRS file.
    :type input_file: str
    :param language: Language code to add as a prefix
    :type language: str
    :param add_speakers: Prepend speaker names to lines
    :type add_speakers: bool
    :param noise: Preserve noise such as laughter or hesitation
    :type noise: bool
    :returns: Input file in WEBVTT format.
    :rtype: str"""
    with open(input_path, "r", encoding="utf-8") as file:
        tree = ET.parse(file)
        root = tree.getroot()

    if add_speakers:
        speakers = {
            speaker["id"]: speaker["name"]
            for speaker in root.find("Speakers").getchildren()
        }

    # Add file prefix
    vtt = ["WEBVTT"]
    if language:
        vtt.append("Language: {}".format(language))
    vtt.append("")

    return "\n".join(vtt)


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Convert a TRS subtitle file to the WebVTT format."
    )
    parser.add_argument("input", help="Path to the input file")
    parser.add_argument(
        "-o",
        "--output",
        required=False,
        nargs=1,
        metavar="PATH",
        help="Write output to PATH instead of STDOUT",
    )
    parser.add_argument(
        "-l",
        "--language",
        required=False,
        nargs="?",
        metavar="LANG",
        help="Add 'Language: LANG' prefix to output",
    )
    parser.add_argument(
        "-s",
        "--speakers",
        required=False,
        action="store_true",
        help="Add speaker metadata to each line",
    )
    parser.add_argument(
        "-n",
        "--noise",
        required=False,
        action="store_true",
        help="Preserve noise such as laughter",
    )
    args = parser.parse_args()

    vtt = convert(args.input, args.language, args.speakers, args.noise)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(vtt)
    else:
        sys.stdout.write(vtt)
