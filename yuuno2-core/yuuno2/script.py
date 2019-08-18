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
from contextlib import contextmanager
from typing import Mapping, Any, Optional, Union, NoReturn, Sequence
from abc import ABC, abstractmethod

from yuuno2.resource_manager import Resource
from yuuno2.clip import Clip
from yuuno2.typings import ConfigTypes


NOT_GIVEN = object()


class Script(Resource, ABC):

    @abstractmethod
    def activate(self) -> NoReturn:
        """
        :return:
        """
        pass

    @abstractmethod
    def deactivate(self) -> NoReturn:
        pass

    @contextmanager
    def inside(self):
        self.activate()
        try:
            yield
        finally:
            self.deactivate()

    @abstractmethod
    async def set_config(self, key: str, value: ConfigTypes) -> NoReturn:
        pass

    @abstractmethod
    async def get_config(self, key: str, default: Union[object, ConfigTypes]=NOT_GIVEN) -> ConfigTypes:
        return None

    @abstractmethod
    async def list_config(self) -> Sequence[str]:
        return []

    @abstractmethod
    async def run(self, code: Union[bytes, str]) -> Any:
        pass

    @abstractmethod
    async def retrieve_clips(self) -> Mapping[str, Clip]:
        return {}


class ScriptProvider(Resource, ABC):

    @abstractmethod
    async def get(self, **params: Any) -> Optional[Script]:
        pass