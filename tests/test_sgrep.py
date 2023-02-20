#!/usr/bin/env python3
"""
Author: mcomeau
Date: 2023/02/12
"""

import importlib
import os
import sys
import unittest

import utils

append_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(append_path)
sgrep = importlib.import_module("sgrep")
from sgrep.Sgrep import *


class TestParser(unittest.TestCase):
    TEXT_FILE = "sample.txt"

    @classmethod
    def setUpClass(cls):
        with open(cls.TEXT_FILE, "w") as fd:
            fd.write(utils.SAMPLE_CONTENT)

    @classmethod
    def tearDownClass(cls):
        os.remove(cls.TEXT_FILE)

    def test_bad_init(self):
        cases = [
            [-1, 1, 0],
            [0, 0, 0],
            [0, 1, -1]
        ]
        for c in cases:
            with self.assertRaises(Exception, msg="Faulty initialization should fail!"):
                with open(self.TEXT_FILE, "r") as fd:
                    Sgrep(fd, *c)

    def one_liner_buffer_search(self, nb_buffers: int, regex: bool):
        expected_match_cases = {
            1: [
                ['', "line 6 - 1\n", ''],
                ['', "line 6\n", '']
            ],
            3: [
                ['line 2 + 2 ]\n', "line 6 - 1\n", 'line 6\n'],
                ['line 6 - 1\n', "line 6\n", 'line 3 * 2 + 1\n']
            ]
        }
        nb_buffer_cases = {
            1: [0, 1, 0],
            3: [1, 1, 1]
        }

        expected_matches = expected_match_cases[nb_buffers]

        with open(self.TEXT_FILE, "r") as fd:
            grepper = Sgrep(fd, *nb_buffer_cases[nb_buffers])
            grepper.set_show_markers(False)
            grepper.set_matches_saving(True)
            grepper.setup("line 6", regex_flag=regex, show_captured_only=False)
            grepper.run()

            matched = []
            for m in grepper.iter_matches():
                matched.append(m)

            self.assertEqual(repr(matched), repr(expected_matches))

    def three_liner_buffer_search(self, nb_buffers: int, regex: bool):
        if regex:
            search = r"\[.*]"
            expected_match_cases = {
                1: [
                    ['',
                     'line 2 [\nline 3\nline 2 + 2 ]\n',
                     ''],
                ],
                3: [
                    ['ctx1\nctx2\nctx3\n',
                     'line 2 [\nline 3\nline 2 + 2 ]\n',
                     'line 6 - 1\nline 6\nline 3 * 2 + 1\n'],
                ]
            }
        else:
            search = 'one\ntwo\nthree'
            expected_match_cases = {
                1: [
                    ['', "one\ntwo\nthree", ''],
                ],
                3: [
                    ['line 6 - 1\nline 6\nline 3 * 2 + 1\n',
                     "one\ntwo\nthree",
                     ''],
                ]
            }

        nb_buffer_cases = {
            1: [0, 3, 0],
            3: [3, 3, 3]
        }

        expected_matches = expected_match_cases[nb_buffers]
        with open(self.TEXT_FILE, "r") as fd:
            grepper = Sgrep(fd, *nb_buffer_cases[nb_buffers])
            grepper.set_show_markers(False)
            grepper.set_matches_saving(True)
            grepper.setup(search, regex_flag=regex, show_captured_only=False)
            grepper.run()

            matched = []
            for m in grepper.iter_matches():
                matched.append(m)

            self.assertEqual(repr(matched), repr(expected_matches))

    def test_single_1_liner_buffer_grep(self):
        self.one_liner_buffer_search(nb_buffers=1, regex=False)

    def test_single_1_liner_buffer_regex(self):
        self.one_liner_buffer_search(nb_buffers=1, regex=True)

    def test_triple_1_liner_buffer_grep(self):
        self.one_liner_buffer_search(nb_buffers=3, regex=False)

    def test_triple_1_liner_buffer_regex(self):
        self.one_liner_buffer_search(nb_buffers=3, regex=True)

    def test_single_3_liner_buffer_grep(self):
        self.three_liner_buffer_search(nb_buffers=1, regex=False)

    def test_single_3_liner_buffer_regex(self):
        self.three_liner_buffer_search(nb_buffers=1, regex=True)

    def test_triple_3_liner_buffer_grep(self):
        self.three_liner_buffer_search(nb_buffers=3, regex=False)

    def test_triple_3_liner_buffer_regex(self):
        self.three_liner_buffer_search(nb_buffers=3, regex=True)


if __name__ == "__main__":
    unittest.main()
