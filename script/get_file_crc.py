import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import utils as utl


def main():
    """Compute CRC32 for a file with optional length limit."""
    parser = argparse.ArgumentParser(description="Compute CRC32 for a file")
    parser.add_argument("file", type=str, help="input file path")
    parser.add_argument(
        "-l",
        "--len",
        dest="data_len",
        type=int,
        default=None,
        help="optional length (bytes) to limit CRC computation",
    )

    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"Error: file not found: {args.file}")
        return 1

    with open(args.file, "rb") as f:
        data = f.read()

    data_len = args.data_len
    if data_len is not None:
        data_len = max(int(data_len), 0)
        if data_len > len(data):
            data_len = len(data)

    crc_src = utl.calc_crc32(data, data_len)
    print(f"crc of file '{args.file}': {crc_src:08X}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
