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
"""
This class manages asynchronous resource management.
"""

from _weakref import ref
from _weakrefset import WeakSet
from typing import Set, MutableMapping, None, Optional, Callable, List, Union
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from weakref import WeakKeyDictionary


class Resource(ABC):

    @property
    def acquired(self) -> bool:
        """
        The state of the resource.
        If it has been acquired, this flag will be true.

        :return: True or False depending on whether it has been acquired.
        """
        if self not in _resources:
            return False
        return _resources[self].acquired > 0

    @property
    def resource_state(self) -> Optional['ResourceState']:
        return _get_state(self)

    @abstractmethod
    async def _acquire(self) -> None:
        """
        Acquires the resource.
        Only after you acquired it, you can use the resource (e.g. get metadata, render a frame, ...)
        """

    @abstractmethod
    async def _release(self) -> None:
        """
        Releases the frame and the associated resources.

        Please consider that this method might also be called if the parent has been
        disposed incorrectly.
        """

    async def acquire(self) -> None:
        """
        Acquires the resource.

        DO NOT OVERRIDE.
        """
        # Control the order the resource-dict is
        # released by manually holding a reference to the dict
        # that will otherwise not be used.
        #
        # This is important because if the module is collected
        # before an instance of this module, _resources is set to None.
        # Which causes an error in the __del__ method.
        #
        # This is a very rare edge-case that only happened to me exactly once.

        # noinspection PyAttributeOutsideInit
        self.__resource_dict_ref = _resources

        _flag_acquired(self)
        if self.resource_state.acquired != 1:
            return

        try:
            await self._acquire()
        except Exception as e:
            try:
                await self.release()
            except Exception as e_sub:
                e_sub.__context__ = e
                raise e_sub
            else:
                raise

    async def release(self, *, force=True) -> None:
        """
        Releases the resource.

        :param force: If force is false, the resource will only be released if no other
                      resource has acquired it.
        """
        if (force and self.acquired > 0) or self.resource_state.acquired == 1:
            await _release_children(self)
            await self._release()

        if self.resource_state.acquired > 0:
            self.resource_state.acquired -= 1

    async def _release_deferred(self) -> bool:
        """
        :return True: This object has been released by an incorrect removal of the object.
        """
        if not self.acquired:
            return False

        state = self.resource_state
        if state.parent_dead:
            state.acquired = False
            await self.release()
            return True

        return False

    async def __aenter__(self) -> 'Resource':
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.acquired:
            await self.release(force=False)

    async def check_acquired(self) -> bool:
        if not self.acquired:
            return False

        if await self._release_deferred():
            return False

        return True

    async def ensure_acquired(self) -> None:
        if not self.acquired:
            raise AssertionError("Resource not acquired.")

        if await self._release_deferred():
            raise AssertionError("Parent resource incorrectly released.")

    def __del__(self):
        if self.acquired:
            try:
                import warnings
                warnings.warn(
                    f"Resource {self!r} was never released. Did you do this by mistake?",
                    ResourceWarning,
                    stacklevel=2
                )

            except ImportError:
                # Fix for bug during python shutdown:
                # > During python shutdown, you cannot correctly import modules anymore.
                #
                # We can safely assume that warnings is imported, so we skip the warning.
                pass

            _mark_incorrectly_released(self)
            _call_release_cbs(self)


@dataclass
class ResourceState:
    released: bool = False
    acquired: int = 0
    parent_dead: bool = False
    parents: Set[Resource] = field(default_factory=WeakSet)
    children: Set[Resource] = field(default_factory=set)
    callbacks: List[Callable[[Resource], None]] = field(default_factory=list)


class ResourceProxy(Resource):

    def __init__(self, target: 'NonAbcResource'):
        self.target = ref(target)

    async def _release(self) -> None:
        target = self.target()
        if target is None:
            return
        await target._release()

    async def _acquire(self) -> None:
        target = self.target()
        if target is None:
            return
        await target._acquire()

    def __repr__(self):
        return f"<ResourceProxy for {self.target()!r}>"


class NonAbcResource:

    @property
    def resource(self) -> 'Resource':
        resource = _light_resources.setdefault(self, ResourceProxy(self))
        return resource

    @property
    def resource_state(self) -> 'ResourceState':
        return self.resource.resource_state

    @property
    def acquired(self) -> bool:
        return self.resource.acquired

    async def acquire(self):
        await self.resource.acquire()

    async def release(self, *, force=True):
        await self.resource.release(force=force)

    async def __aenter__(self):
        await self.resource.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.resource.__aexit__(exc_type, exc_val, exc_tb)

    async def _acquire(self):
        pass

    async def _release(self):
        pass

    async def ensure_acquired(self):
        return self.resource.ensure_acquired()


ResourceTarget = Union[Resource, NonAbcResource]


_light_resources: MutableMapping[NonAbcResource, Resource] = WeakKeyDictionary()
_resources: MutableMapping[Resource, ResourceState] = WeakKeyDictionary()


def _flag_acquired(resource: Resource) -> None:
    state = _get_state(resource)

    if state.released:
        raise EnvironmentError(f"Resource cannot be reacquired. (resource: {resource!r}")

    for par in state.parents:
        if not par.acquired:
            raise EnvironmentError(f"Parent not acquired: {par!r} (resource: {resource!r})")
    state.acquired += 1


def _mark_incorrectly_released(resource: Resource) -> None:
    resource_state = _get_state(resource)
    resource_state.parent_dead = True

    for child in resource_state.children:
        _mark_incorrectly_released(child)

    resource_state.children = frozenset()


def _get_state(resource: ResourceTarget) -> ResourceState:
    if not isinstance(resource, Resource):
        resource = resource.resource

    return _resources.setdefault(resource, ResourceState())


def register(parent: ResourceTarget, child: ResourceTarget):
    """
    Register the child-resource to the parent resource.

    If the parent resource is released, the child is automatically released.

    :param parent:  The parent resource.
    :param child:   The child resource.
    """
    if isinstance(parent, NonAbcResource): parent = parent.resource
    if isinstance(child,  NonAbcResource): child  = child.resource

    _get_state(child).parents.add(parent)
    _get_state(parent).children.add(child)


def _call_release_cbs(resource: Resource):
    state = resource.resource_state
    if state is None:
        return

    for cb in state.callbacks:
        cb(resource)


def on_release(resource: ResourceTarget, callback: Callable[[Resource], None]) -> None:
    """
    Adds a callback that is called when the resource is about to be released.

    If the object is incorrectly released

    :param resource: The resource to attach to.
    :param callback: The callback to run.
    """
    _get_state(resource).callbacks.append(callback)


def remove_callback(resource: ResourceTarget, callback: Callable[[Resource], None]) -> None:
    """
    Removes the callback from the callback list.

    :param resource: The resource that is attached.
    :param callback: The callback to remove.
    """
    cbs = _get_state(resource).callbacks
    if callback in cbs:
        cbs.remove(callback)


async def _release_children(resource: Resource):
    if isinstance(resource, NonAbcResource): resource = resource.resource
    state = _get_state(resource)
    state.released = True
    state.acquired = 0

    _call_release_cbs(resource)

    for parent in resource.resource_state.parents:
        siblings = parent.resource_state.children
        siblings.remove(resource)

    for child in list(state.children):
        await child.release()
