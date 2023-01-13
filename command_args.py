import argparse
from sys import exit
from datetime import datetime

"""
Commands:
    -h  --help          Print manual/help

    -l  --live          Open program with connection to sensor live via serial port
                        Parameters:
    -p                  Serial port e.g. 'COM3' or '/dev/TTY*' [String] (MANDATORY)
    -o                  Output file path [String]                       (OPTIONAL)

    -rp --replay        Open program and and get input from file.
                        Parameters:
    -i                  Input file path [String]                        (MANDATORY)
    -f                  Playback frequency [Int, Hz]                    (OPTIONAL)
"""

def run_arg_parse():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--live", action="store_true")
    group.add_argument("--replay", action="store_true")
    parser.add_argument("-p", type=str, help="COM port")
    parser.add_argument("-b", type=int, help="Baudrate (e.g. 115200)")
    parser.add_argument("-o", type=str, help="Path to output file")
    parser.add_argument("-i", type=str, help="Input file")
    parser.add_argument("-f", type=int, help="Playback frequency")

    args = parser.parse_args()

    if args.live:
        if not args.p:
            print("Serial/COM-port MUST be specified with the option -p <port>")
            exit()
        if not args.b:
            print("Baudrate MUST be specified with the option -b <baudrate>")
            exit()
        if not args.o:
            print("Output will be saved to file in the format log_<date>_<time>.json")
            print("Output MAY be specified with the option -o <path/filename>")
    elif args.replay:
        if not args.i:
            print("Input file not provided. MUST be specified with -i <path/filename>")
            exit()
        if not args.f:
            # args['f'] = 5
            print("Playback frequency defaulted to 5Hz. MAY be specified with the option -f <Hz>")
    else:
        print("No valid arguments given. See --help")
        exit()

    return args