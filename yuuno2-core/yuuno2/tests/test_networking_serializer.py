#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Yuuno - IPython + VapourSynth
# Copyright (C) 2019 StuxCrystal (Roland Netzsch <stuxcrystal@encode.moe>)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from unittest import TestCase

from yuuno2.networking.base import Message
from yuuno2.networking.serializer import bytes_protocol, ByteOutputStream


class TestProtocolParser(TestCase):

    def test_read_text_only(self):
        parser = bytes_protocol()
        self.assertEqual(list(parser.feed(b"\x00\x00\x00\x01\x00\x00\x00\x02{}")), [Message({}, [])])
        self.assertEqual(list(parser.feed(b'\x00\x00\x00\x01\x00\x00\x00\x0a{"test":1}')), [Message({"test": 1}, [])])

    def test_read_with_buffer(self):
        parser = bytes_protocol()
        self.assertEqual(
            list(parser.feed(b'\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x02{}ab')),
            [Message({}, [b"ab"])]
        )
        self.assertEqual(
            list(parser.feed(b'\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x02{}abcd')),
            [Message({}, [b"ab", b"cd"])]
        )

    def test_read_both(self):
        parser = bytes_protocol()
        self.assertEqual(
            list(parser.feed(b'\x00\x00\x00\x03\x00\x00\x00\x0a\x00\x00\x00\x02\x00\x00\x00\x02{"test":1}abcd')),
            [Message({"test": 1}, [b"ab", b"cd"])]
        )


class TestProtocolWriter(TestCase):

    def test_write_message_text_only(self):
        self.assertEqual(
            ByteOutputStream.write_message(Message({}, [])),
            b"\x00\x00\x00\x01\x00\x00\x00\x02{}"
        )
        self.assertEqual(
            ByteOutputStream.write_message(Message({"test":1}, [])),
            b'\x00\x00\x00\x01\x00\x00\x00\x0a{"test":1}'
        )

    def test_write_message_buffer(self):
        self.assertEqual(
            ByteOutputStream.write_message(Message({}, [b"ab"])),
            b'\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x02{}ab'
        )
        self.assertEqual(
            ByteOutputStream.write_message(Message({}, [b"ab", b"cd"])),
            b'\x00\x00\x00\x03\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x02{}abcd'
        )

    def test_write_both(self):
        self.assertEqual(
            ByteOutputStream.write_message(Message({"test": 1}, [b"ab", b"cd"])),
            b'\x00\x00\x00\x03\x00\x00\x00\x0a\x00\x00\x00\x02\x00\x00\x00\x02{"test":1}abcd'
        )
