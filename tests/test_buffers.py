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


class BufferTest(unittest.TestCase):
    def _confirm_stack_empty(self, stacked_buffers):
        error_msg = utils.confirm_stack_empty(stacked_buffers)
        if error_msg:
            self.fail(error_msg)

    def _confirm_buffer_content(self, stacked_buffers, stacked_size, expected_buffer_sizes: [], expected_content: []):
        error_msg = utils.confirm_buffer_content(stacked_buffers,
                                                 stacked_size,
                                                 expected_buffer_sizes,
                                                 expected_content)
        if error_msg:
            self.fail(error_msg)


class TestSingleStackBuffer(BufferTest):
    def test_one_liner_buffer(self):
        single_buffer_stack = StackedBuffers([1])

        # Empty buffer tests
        self._confirm_stack_empty(single_buffer_stack)

        # Shouldn't be able to push content on public buffers
        with self.assertRaises(Exception, msg="Shouldn't be able to append data to internal buffers!"):
            single_buffer_stack.get_buffer(0).append("Error!")

        # Should be able to push content to stacked buffer
        token = "Bonjour!\n"
        single_buffer_stack.push(token)

        self._confirm_buffer_content(single_buffer_stack, 1, [1], [token])

    def test_3_liner_buffer(self):
        push_nb_items = 5
        buffer_size = 3

        single_buffer_stack = StackedBuffers([buffer_size])

        # Empty buffer tests
        self._confirm_stack_empty(single_buffer_stack)

        # Shouldn't be able to push content on public buffers
        with self.assertRaises(Exception, msg="Shouldn't be able to append data to internal buffers!"):
            single_buffer_stack.get_buffer(0).append("Error!")

        # Should be able to push content to stacked buffer
        expected_content_format = utils.push_1_to_x_numbers(single_buffer_stack, push_nb_items)

        expected_content = []
        for i in range(buffer_size-1, 0-1, -1):
            expected_content.append(expected_content_format.format(push_nb_items-i))

        self._confirm_buffer_content(single_buffer_stack, 1, [buffer_size], ["".join(expected_content)])


class TestMultiStackBuffer(BufferTest):

    def test_triple_stacked_2_liner_buffer(self):
        push_nb_items = 10
        buffer_sizes = [2, 2, 2]

        stacked_buffer = StackedBuffers(buffer_sizes)

        # Empty buffer tests
        self._confirm_stack_empty(stacked_buffer)

        # Shouldn't be able to push content on public buffers
        for b in range(0, stacked_buffer.size):
            with self.assertRaises(Exception, msg=f"Shouldn't be able to append data to internal buffer[{b}]!"):
                stacked_buffer.get_buffer(b).append("Error!")

        # Should be able to push content to stacked buffer
        expected_content_format = utils.push_1_to_x_numbers(stacked_buffer, push_nb_items)

        expected_content = [
            "".join([expected_content_format.format(5), expected_content_format.format(6)]),
            "".join([expected_content_format.format(7), expected_content_format.format(8)]),
            "".join([expected_content_format.format(9), expected_content_format.format(10)])
        ]
        self._confirm_buffer_content(stacked_buffer, len(buffer_sizes), buffer_sizes, expected_content)

        # Empty last buffer
        stacked_buffer.push(None)
        stacked_buffer.push(None)
        buffer_sizes[2] = 0

        expected_content = [
            "".join([expected_content_format.format(7), expected_content_format.format(8)]),
            "".join([expected_content_format.format(9), expected_content_format.format(10)]),
            ''
        ]
        self._confirm_buffer_content(stacked_buffer, len(buffer_sizes), buffer_sizes, expected_content)

        # Pop one in middle buffer
        stacked_buffer.push(None)
        buffer_sizes[1] = 1

        expected_content = [
            "".join([expected_content_format.format(8), expected_content_format.format(9)]),
            "".join([expected_content_format.format(10)]),
            ''
        ]
        self._confirm_buffer_content(stacked_buffer, len(buffer_sizes), buffer_sizes, expected_content)

        # Empty the rest of the stack
        for i in range(0, 8):
            stacked_buffer.push(None)
        self._confirm_stack_empty(stacked_buffer)


if __name__ == "__main__":
    unittest.main()
