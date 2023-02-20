#!/usr/bin/env python3

import importlib
import io
import os
import sys

import utils

append_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(append_path)
sgrep = importlib.import_module("sgrep")
from sgrep.Sgrep import *


SAMPLE_TEXT = "sample.txt"
failure = 0


def capture_output(method, *args):
    bak_stdout = sys.stdout
    bak_stderr = sys.stderr
    try:
        with io.StringIO() as buf:
            sys.stdout = buf
            sys.stderr = buf
            method(*args)
            return buf.getvalue()
    finally:
        sys.stdout = bak_stdout
        sys.stderr = bak_stderr


def test_markers():
    global failure
    print("----------------------------")
    print("test_markers")
    expected_output = '<lead ctx>\nctx1\n<search ctx>\nctx2\n<trailing ctx>\nctx3\n<end grep>\n\n'

    def _test():
        with open(SAMPLE_TEXT, "w") as fd:
            fd.write(utils.SAMPLE_CONTENT)

        with open(SAMPLE_TEXT, "r") as fd:
            parser = Sgrep(fd, 1, 1, 1)
            parser.set_show_markers(True)
            parser.setup("ctx2", regex_flag=False, show_captured_only=False)
            parser.run()

    test_out = capture_output(_test)
    if repr(test_out) == repr(expected_output):
        print(f"RESULTS: {repr(test_out)}")
        print("PASS")
    else:
        failure = 1
        print("FAIL")
        print("   Expected: '%s'" % repr(expected_output))
        print("   Got:      '%s'" % repr(test_out))


def test_no_markers():
    global failure
    print("----------------------------")
    print("test_no_markers")
    expected_output = 'ctx1\nctx2\nctx3\n\n'

    def _test():
        with open(SAMPLE_TEXT, "w") as fd:
            fd.write(utils.SAMPLE_CONTENT)

        with open(SAMPLE_TEXT, "r") as fd:
            parser = Sgrep(fd, 1, 1, 1)
            parser.set_show_markers(False)
            parser.setup("ctx2", regex_flag=False, show_captured_only=False)
            parser.run()

    test_out = capture_output(_test)
    if repr(test_out) == repr(expected_output):
        print(f"RESULTS: {repr(test_out)}")
        print("PASS")
    else:
        failure = 1
        print("FAIL")
        print("   Expected: '%s'" % repr(expected_output))
        print("   Got:      '%s'" % repr(test_out))


def _captured_regex_cases(expected_outputs: dict, show_markers: bool, multiline: int):
    global failure

    def _test(regex):
        with open(SAMPLE_TEXT, "w") as fd:
            fd.write(utils.SAMPLE_CONTENT)

        with open(SAMPLE_TEXT, "r") as fd:
            parser = Sgrep(fd, 1, multiline, 1)
            parser.set_show_markers(show_markers)
            parser.setup(regex, regex_flag=True, show_captured_only=True)
            parser.run()

    for case in expected_outputs.keys():
        test_out = capture_output(_test, case)
        if repr(test_out) == repr(expected_outputs[case]):
            print(f"RESULTS: {repr(test_out)}")
            print("PASS")
        else:
            failure = 1
            print("FAIL")
            print("   Expected: '%s'" % repr(expected_outputs[case]))
            print("   Got:      '%s'" % repr(test_out))


def test_marked_captured_regex():
    print("----------------------------")
    print("test_marked_captured_regex")
    expected_outputs = {
        'ctx2': '<lead ctx>\nctx1\n<search ctx>\n\n<trailing ctx>\nctx3\n<end grep>\n\n',
        '(ctx2)': '<lead ctx>\nctx1\n<search ctx>\n1: ctx2\n<trailing ctx>\nctx3\n<end grep>\n\n'
    }
    _captured_regex_cases(expected_outputs, True, 1)


def test_unmarked_captured_regex():
    print("----------------------------")
    print("test_unmarked_captured_regex")
    expected_outputs = {
        'ctx2': 'ctx1\n\nctx3\n\n',
        '(ctx2)': 'ctx1\nctx2\nctx3\n\n'
    }

    _captured_regex_cases(expected_outputs, False, 1)


def test_captured_regex_multiline():
    print("----------------------------")
    print("test_unmarked_captured_regex_multiline")

    expected_outputs = {
        r'(ctx\d\n)(ctx\d\n)': 'ctx1\n ctx2\nctx3\n\nctx1\nctx2\n ctx3\nline 2 [\n\n'
    }
    _captured_regex_cases(expected_outputs, False, 2)

    expected_outputs = {
        r'(ctx2\n)': '<lead ctx>\nctx1\n<search ctx>\n1: ctx2\n<trailing ctx>\nline 2 [\n<end grep>\n\n'
    }
    _captured_regex_cases(expected_outputs, True, 2)


if __name__ == "__main__":
    test_markers()
    test_no_markers()
    test_marked_captured_regex()
    test_unmarked_captured_regex()
    test_captured_regex_multiline()
    os.remove(SAMPLE_TEXT)

    sys.exit(failure)
