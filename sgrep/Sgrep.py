"""
MIT License

Copyright (c) 2023 Mathieu Comeau

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from sgrep.StackedBuffers import *

import re


class StreamParser:
    LEADING_BUFFER = 0
    SEARCH_BUFFER = 1
    TRAILING_BUFFER = 2

    def __init__(self, stream, leading_ctx_size, search_ctx_size, trailing_ctx_size):
        if leading_ctx_size < 0 or search_ctx_size <= 0 or trailing_ctx_size < 0:
            raise Exception(f"Invalid buffer size parameters: "
                            f"'{leading_ctx_size} < 0 or {search_ctx_size} <= 0 or {trailing_ctx_size} < 0'")
        self._stream = stream

        self._stacked_buffers = StackedBuffers([leading_ctx_size,
                                                search_ctx_size,
                                                trailing_ctx_size])

        # Assume stream is not empty so first tick succeeds
        self._last_read = '\n'

    @property
    def eof(self) -> bool:
        return self._last_read == ''

    def prime_buffers(self) -> None:
        """
        Attempt to populate leading buffer until the search one is full
        :return:
        """
        while True:
            self.tick()

            # Is the search buffer primed?
            if self._stacked_buffers.get_buffer(StreamParser.SEARCH_BUFFER).is_full:
                break

            # If the trailing buffer is empty and the stream is eof, this is as much
            # data as we're going to get
            if self.eof and self._stacked_buffers.get_buffer(StreamParser.TRAILING_BUFFER).is_empty:
                break

    def tick(self) -> bool:
        """
        Read a new entry if available, pushing it onto the stacked buffer,
        cycling entries through all internal buffers in the process
        :return: True if there is more data in the buffers
        """
        if not self.eof:
            self._last_read = self._stream.readline()

        self._stacked_buffers.push(self._last_read)

        return not self._stacked_buffers.is_empty

    @property
    def leading_buffer(self):
        return self._stacked_buffers.get_buffer(StreamParser.LEADING_BUFFER)

    @property
    def search_buffer(self):
        return self._stacked_buffers.get_buffer(StreamParser.SEARCH_BUFFER)

    @property
    def trailing_buffer(self):
        return self._stacked_buffers.get_buffer(StreamParser.TRAILING_BUFFER)


class Sgrep:
    DEFAULT_CONTEXT_LEADING_LINES = 0
    DEFAULT_CONTEXT_TRAILING_LINES = 0

    def __init__(self, stream, leading_ctx_size, search_ctx_size, trailing_ctx_size):
        self._parser = StreamParser(stream, leading_ctx_size, search_ctx_size, trailing_ctx_size)

        self._leading_ctx = self._parser.leading_buffer
        self._search_ctx = self._parser.search_buffer
        self._trailing_ctx = self._parser.trailing_buffer

        self._grep_str = None
        self._regex = None
        self._multiline = search_ctx_size > 1
        self._show_captured_regex_only = False

        self._grepper = None
        self._search_buf = None
        self._process_match = None
        self._saved_matches = []

        self._show_markers = True
        self._save_match_flag = False
        self.set_matches_saving(self._save_match_flag)

    def set_show_markers(self, flag: bool) -> None:
        """
        Show markers to delimit the different context when outputting to stdout
        :param flag: bool
        :return:
        """
        self._show_markers = flag

    def set_matches_saving(self, flag) -> None:
        """
        Save matches instead of printing them on stdout
        :param flag: bool
        :return:
        """
        self._save_match_flag = flag
        if self._save_match_flag:
            self._process_match = self._save_match
        else:
            self._process_match = self._print_match

    def iter_matches(self) -> str:
        """
        Iterate through the saved matches
        :return: str
        """
        for m in self._saved_matches:
            yield m

    def setup(self, grep_str: str, regex_flag: bool, show_captured_only: bool) -> None:
        """
        Configure the grepping.
        :param grep_str: string to use for grepping, can be a NON compiled regex
        :param regex_flag: if 'grep_str' is meant to be compiled as a regex
        :param show_captured_only: If True, only shows captured regex match (regex only)
                                   Regex needs to use capturing groups.
        :return:
        """
        if grep_str == "":
            raise Exception("Empty grep string given to 'setup'!")

        if regex_flag:
            flags = re.DOTALL
            if self._multiline:
                flags |= re.MULTILINE
            self._regex = re.compile(grep_str, flags=flags)
            self._show_captured_regex_only = show_captured_only
        else:
            self._grep_str = grep_str

        self._parser.prime_buffers()
        self._attach_grepper()

    def _attach_grepper(self) -> None:
        if self._grep_str:
            if self._multiline:
                self._grepper = self._grep_search_multiline
            else:
                self._grepper = self._grep_search
        elif self._regex:
            if self._multiline:
                self._grepper = self._regex_search_multiline
            else:
                self._grepper = self._regex_search
        else:
            raise Exception("You must call 'setup' first!")

    def _save_match(self, match_str: str) -> None:
        self._saved_matches.append([self._leading_ctx.buffer_str,
                                    match_str,
                                    self._trailing_ctx.buffer_str])

    def _print_match(self, match_str: str) -> None:
        if not self._leading_ctx.is_empty:
            if self._show_markers:
                print("<lead ctx>")
            print(self._leading_ctx.buffer_str.rstrip("\n"))
        if self._show_markers:
            print("<search ctx>")
        print(match_str.rstrip("\n"))
        if not self._trailing_ctx.is_empty:
            if self._show_markers:
                print("<trailing ctx>")
            print(self._trailing_ctx.buffer_str.rstrip("\n"))
        if self._show_markers:
            print("<end grep>")
        print()

    def _grep_search(self) -> None:
        if self._grep_str in self._search_buf:
            self._process_match(self._search_buf)

    def _grep_search_multiline(self) -> None:
        # Make sure we match starting on first line of multi line string
        first_newline = self._search_buf.find('\n')
        match_loc = self._search_buf.find(self._grep_str)
        if match_loc != -1 and match_loc < first_newline:
            self._process_match(self._search_buf)

    def _regex_search(self) -> None:
        m = self._regex.search(self._search_buf)
        if m:
            if self._show_captured_regex_only:
                if self._show_markers:
                    self._process_match("\n".join([f"{i}: {m.group(i)}" for i in range(1, len(m.groups())+1)]))
                else:
                    self._process_match(" ".join(m.groups()))
            else:
                self._process_match(self._search_buf)

    def _regex_search_multiline(self) -> None:
        m = self._regex.search(self._search_buf)
        if m:
            # Make sure we match starting on first line of multi line string
            first_newline = self._search_buf.find('\n')
            if m and m.start() < first_newline:
                if self._show_captured_regex_only:
                    if self._show_markers:
                        self._process_match("\n".join([f"{i}: {m.group(i)}" for i in range(1, len(m.groups())+1)]))
                    else:
                        self._process_match(" ".join(m.groups()))
                else:
                    self._process_match(self._search_buf)

    def run(self) -> None:
        while True:
            self._search_buf = self._search_ctx.buffer_str
            self._grepper()
            self._parser.tick()
            if self._search_ctx.is_empty:
                break
