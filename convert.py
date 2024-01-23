import argparse
import sys


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Convert a TRS subtitle file to the WebVTT format."
    )
    parser.add_argument("input_file", help="Path to the input file")
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
        nargs=1,
        metavar="LANG",
        help="Add 'Language: LANG' prefix to output",
    )
    args = parser.parse_args()
