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
from asyncio import wait_for

from aiounittest import AsyncTestCase

from yuuno2.networking.base import Message
from yuuno2.networking.multiplex import Multiplexer
from yuuno2.networking.pipe import pipe_bidi


class TestMultiplexer(AsyncTestCase):

    async def test_multiplexer_reject(self):
        c_faked_networking, c_multiplexed = pipe_bidi()
        muliplexer = Multiplexer(c_multiplexed)
        async with c_faked_networking, muliplexer:
            await c_faked_networking.write(Message({'target': 'non-existent', 'payload': {}}))
            msg: Message = await wait_for(c_faked_networking.read(), 5)

        self.assertIsInstance(msg.values, dict)
        self.assertIn('type', msg.values)
        self.assertEqual('close', msg.values['type'])

    async def test_multiplexer_delivered(self):
        value = {'v': 'test'}

        c_faked_networking, c_multiplexed = pipe_bidi()
        muliplexer = Multiplexer(c_multiplexed)
        async with c_faked_networking, muliplexer:
            async with muliplexer.connect('existing') as f:
                await c_faked_networking.write(Message({'target': 'existing', 'type': 'message', 'payload': value}))
                msg: Message = await wait_for(f.read(), 5)

        self.assertIs(value, msg.values)

    async def test_multiplexer_illegal(self):
        c_faked_networking, c_multiplexed = pipe_bidi()
        muliplexer = Multiplexer(c_multiplexed)
        async with c_faked_networking, muliplexer:
            async with muliplexer.connect('existing') as f:
                await c_faked_networking.write(Message({'target': 'existing', 'type': 'message'}))
                msg: Message = await wait_for(c_faked_networking.read(), 5)

        self.assertIsInstance(msg.values, dict)
        self.assertIn('type', msg.values)
        self.assertEqual('illegal', msg.values['type'])

    async def test_multiplexer_send(self):
        values = {}

        c_faked_networking, c_multiplexed = pipe_bidi()
        muliplexer = Multiplexer(c_multiplexed)
        async with c_faked_networking, muliplexer:
            async with muliplexer.connect('existing') as f:
                await f.write(Message(values, []))
                msg: Message = await wait_for(c_faked_networking.read(), 5)

        self.assertIsInstance(msg.values, dict)
        self.assertIn('target', msg.values)
        self.assertEqual('existing', msg.values['target'])
        self.assertIn('type', msg.values)
        self.assertEqual('message', msg.values['type'])
        self.assertIn('payload', msg.values)
        self.assertIs(values, msg.values['payload'])

    async def test_multiplexer_channel_death(self):
        c_faked_networking, c_multiplexed = pipe_bidi()
        muliplexer = Multiplexer(c_multiplexed)
        async with c_faked_networking, muliplexer:
            async with muliplexer.connect('temporary'):
                pass

            msg: Message = await wait_for(c_faked_networking.read(), 5)
            self.assertIsInstance(msg.values, dict)
            self.assertIn('type', msg.values)
            self.assertEqual('close', msg.values['type'])

            await c_faked_networking.write(Message({'target': 'temporary', 'payload': {}}))
            msg: Message = await wait_for(c_faked_networking.read(), 5)
            self.assertIsInstance(msg.values, dict)
            self.assertIn('type', msg.values)
            self.assertEqual('close', msg.values['type'])

    async def test_bidi_multiplexer_comm(self):
        c_m1, c_m2 = pipe_bidi()
        m1 = Multiplexer(c_m1)
        m2 = Multiplexer(c_m2)

        async with m1, m2:
            m1_ch = m1.connect('channel')
            m2_ch = m2.connect('channel')

            async with m1_ch, m2_ch:
                await m1_ch.write(Message({'someval': 123456}))
                msg: Message = await m2_ch.read()

                self.assertIsInstance(msg.values, dict)
                self.assertIn('someval', msg.values)
                self.assertEqual(123456, msg.values['someval'])

            self.assertTrue(m1_ch.closed)
            self.assertTrue(m2_ch.closed)

    async def test_multiplexer_forward_close(self):
        c_m1, c_m2 = pipe_bidi()
        m1 = Multiplexer(c_m1)
        m2 = Multiplexer(c_m2)

        async with m1, m2:
            m1_ch = m1.connect('channel')
            m2_ch = m2.connect('channel')

            async with m1_ch, m2_ch:
                await m1_ch.close()
                self.assertTrue(m1_ch.closed)

                await wait_for(m2_ch.read(), 5)
                self.assertTrue(m2_ch.closed)
