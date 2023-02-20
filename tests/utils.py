"""
Author: mcomeau
Date: 2023/02/12
"""

EMPTY_CONTENT = ""

SAMPLE_CONTENT = """ctx1
ctx2
ctx3
line 2 [
line 3
line 2 + 2 ]
line 6 - 1
line 6
line 3 * 2 + 1
one
two
three"""


def confirm_stack_empty(stacked_buffers):
    error_msg = ""
    if not stacked_buffers.is_empty:
        error_msg += "StackedBuffer not empty!"

    for i in range(0, stacked_buffers.size):
        buffer = stacked_buffers.get_buffer(i)
        if not buffer.is_empty:
            error_msg += f"Buffer[{i}] is not empty!"

        if buffer.is_full:
            error_msg += f"Buffer[{i}] reported as full!"

        content = buffer.buffer_str
        if content:
            error_msg += f"Buffer[{i}] contains {content}!"

    return error_msg


def confirm_buffer_content(stacked_buffers, stacked_size, expected_buffer_sizes: [], expected_content: []):
    error_msg = ""
    if stacked_buffers.is_empty:
        error_msg += "StackedBuffer empty!"

    if stacked_buffers.size != stacked_size:
        error_msg += f"Expected stack size: {stacked_size} Got: {stacked_buffers.size}"

    for i in range(0, stacked_buffers.size):
        buffer = stacked_buffers.get_buffer(i)

        if buffer.is_empty and expected_buffer_sizes[i] != 0:
            error_msg += f"Buffer[{i}] is empty!"

        is_full = buffer.size == expected_buffer_sizes[i]

        if stacked_buffers.get_buffer(i).is_full != is_full:
            if is_full:
                error_msg += f"Buffer[{i}] should have reported it is full!"
            else:
                error_msg += f"Buffer[{i}] should have reported it is NOT full!"

        content = stacked_buffers.get_buffer(i).buffer_str
        if content != expected_content[i]:
            error_msg += f"Expected: {repr(expected_content[i])} Got: {repr(content)}!"

    return error_msg


def push_1_to_x_numbers(stacked_buffer, x_numbers):
    expected_content_format = "line: {:d}\n"
    for i in range(1, x_numbers+1):
        stacked_buffer.push(expected_content_format.format(i))
    return expected_content_format
