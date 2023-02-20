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
from abc import ABC


class BufferABC(ABC):
    """
    Buffer interface
    """
    def __init__(self, buffer: [], buffer_size):
        self._buffer = buffer
        self._size = buffer_size

    @property
    def size(self) -> int:
        """
        Return maximum size of buffer
        :return:
        """
        return self._size

    @property
    def is_full(self) -> bool:
        return len(self._buffer) == self._size

    @property
    def is_empty(self) -> bool:
        return not bool(self._buffer)

    @property
    def buffer_str(self) -> str:
        return "".join(self._buffer)


class Buffer(BufferABC):
    """
    Buffer implementation for internal use by StackedBuffers. Allows
    pushing data onto the buffer.
    """
    def __init__(self, buffer_size):
        self.buffer = []
        super(Buffer, self).__init__(self.buffer, buffer_size)

    def push(self, entry: str) -> (None, str):
        """
        Push a new entry onto the buffer, popping the oldest item if it went beyond its maximum size.
        Pushing 'None' or '' simply pops the oldest entry in the buffer
        :param entry: data string to push onto the buffer
        :return: None or the oldest discarded entry when buffer was full.
        """
        if entry:
            self.buffer.append(entry)
        if (len(self.buffer) > self._size) or not self.is_empty and (entry is None or entry == ''):
            return self.buffer.pop(0)
        return None


class PublicBuffer(BufferABC):
    """
    Buffer implementation for client use by. No methods for changing the internal data.
    """
    def __init__(self, buffer: Buffer):
        super(PublicBuffer, self).__init__(buffer.buffer, buffer.size)


def buffer_index_checker(f):
    """
    Requirements to use this decorator:
    - must decorate class member method with signature 'method(self, index)'
    - class must have the 'size' property
    """
    def f_wrapper(self, *args, **kwargs):
        index = args[0]
        if index >= self.size:
            raise Exception(f"Index out of range: {index}, buffer size: {self.size}")
        return f(self, *args, **kwargs)
    return f_wrapper


class StackedBuffers:
    """
    The stacked buffer implementation pushes data from leading buffers onto the following
    ones when they're full
    """
    def __init__(self, buffers_size: []):
        self._buffers = []
        self._public_buffers = []
        self._nb_buffers = len(buffers_size)
        for i in range(0, self._nb_buffers):
            self._buffers.append(Buffer(buffers_size[i]))
            self._public_buffers.append(PublicBuffer(self._buffers[-1]))

    def push(self, entry) -> None:
        push_next = entry
        for i in range(self._nb_buffers-1, 0-1, -1):
            push_next = self._buffers[i].push(push_next)

    @property
    def size(self) -> int:
        """
        Return number of stacked buffers in this object
        :return: int
        """
        return self._nb_buffers

    @property
    def is_empty(self) -> bool:
        for i in range(0, self._nb_buffers):
            if not self._buffers[i].is_empty:
                return False
        return True

    @buffer_index_checker
    def get_buffer(self, index) -> PublicBuffer:
        """
        Return a public instance of a stacked buffer
        :param index: index of desired buffer
        :return: PublicBuffer
        """
        return self._public_buffers[index]
