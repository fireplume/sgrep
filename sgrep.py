#!/usr/bin/env python3
"""
Smart parser which allows to output context around a pattern
to be matched in a text file.

Note that grep/egrep may offer similar functionalities, but the
regex support is experimental at the time this tool was written.
"""
from sgrep.Sgrep import Sgrep

import argparse
import os
import sys


def parse_cmdline():
    parser = argparse.ArgumentParser(description='Smart log grepper')

    parser.add_argument("--log",
                        dest="logfile",
                        default=None,
                        help="Filename to read data from, if not used, reads data from stdin")

    parser.add_argument("--ctx-tags",
                        dest="context_tags",
                        default=False,
                        action="store_true",
                        help="Display match context tags in the output")

    parser.add_argument("--regex", "-r",
                        dest="regex",
                        default=False,
                        action="store_true",
                        help="Pattern given is a regular expression")

    parser.add_argument("--leading-lines", "-l",
                        dest="leading_lines",
                        default=Sgrep.DEFAULT_CONTEXT_LEADING_LINES,
                        type=int,
                        help="Number of lines of context to keep BEFORE the grep pattern, defaults to %u" %
                             Sgrep.DEFAULT_CONTEXT_LEADING_LINES)

    parser.add_argument("--trailing-lines", "-t",
                        dest="trailing_lines",
                        default=Sgrep.DEFAULT_CONTEXT_TRAILING_LINES,
                        type=int,
                        help="Number of lines of context to keep AFTER the grep pattern, defaults to %u" %
                             Sgrep.DEFAULT_CONTEXT_TRAILING_LINES)

    parser.add_argument("--captured-only", "-c",
                        dest="captured_only",
                        default=False,
                        action="store_true",
                        help="If specified, will only output regex captured matches with context instead of complete "
                             "matched line")

    parser.add_argument("--multiline", "-m",
                        dest="multiline",
                        default=0,
                        type=int,
                        help="If specified, overrides the matching buffer number of lines set based on the pattern number of '\n'")

    parser.add_argument("grep_pattern",
                        default=None,
                        help="Grepping pattern, no need to double escape characters (be wary of shell expansion though!)")

    parser.epilog = """NOTES

TODO...
"""
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()

    # error checking
    if args.captured_only and not args.regex:
        print("ERROR: You need to use '-r' with '-c' and/or '-m x', where 'x > 1'")
        sys.exit(1)

    if args.leading_lines < 0 or args.trailing_lines < 0:
        print("ERROR: Leading/trailing lines of context must be >0")
        sys.exit(1)

    if args.logfile is not None and not os.path.exists(args.logfile):
        print(f"ERROR: {args.logfile} does not exist!")
        sys.exit(1)

    return args


def main():
    args = parse_cmdline()

    try:
        if args.logfile:
            stream = open(args.logfile, "r")
        else:
            stream = sys.stdin

        if args.multiline:
            search_ctx_size = args.multiline
        elif '\n' in args.grep_pattern:
            search_ctx_size = args.grep_pattern.count('\n')
        else:
            search_ctx_size = 1

        grepper = Sgrep(stream, args.leading_lines, search_ctx_size, args.trailing_lines)
        grepper.set_show_markers(args.context_tags)
        grepper.setup(args.grep_pattern, args.regex, args.captured_only)
        grepper.run()
    except Exception as e:
        print(f"Tool failed with:\n{str(e)}")
        return 1

    print("Done!")


if __name__ == "__main__":
    sys.exit(main())
