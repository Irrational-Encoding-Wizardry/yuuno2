from aiounittest import AsyncTestCase
from yuuno2 import resource_manager
from yuuno2.tests.mocks import MockResource


class TestResource(AsyncTestCase):
    async def test_acquired(self):
        resource = MockResource("test_acquired")
        self.assertFalse(resource.acquired)
        await resource.acquire()
        self.assertTrue(resource.acquired)
        await resource.release()
        self.assertFalse(resource.acquired)

    async def test_resource_state(self):
        resource = MockResource("test_resource_state")
        await resource.acquire()
        self.assertIsNotNone(resource.resource_state)
        self.assertTrue(resource.resource_state.acquired)
        self.assertFalse(resource.resource_state.released)
        await resource.release()
        self.assertIsNotNone(resource.resource_state)
        self.assertFalse(resource.resource_state.acquired)
        self.assertTrue(resource.resource_state.released)

    async def test_async_context_manager(self):
        resource = MockResource("test_resource_state")

        async with resource:
            self.assertIsNotNone(resource.resource_state)
            self.assertTrue(resource.resource_state.acquired)
            self.assertFalse(resource.resource_state.released)

        self.assertIsNotNone(resource.resource_state)
        self.assertFalse(resource.resource_state.acquired)
        self.assertTrue(resource.resource_state.released)

    async def test__acquire__release(self):
        resource = MockResource("test_acquire_release")
        self.assertFalse(resource.has_acquired)
        self.assertFalse(resource.has_released)
        await resource.acquire()
        self.assertTrue(resource.has_acquired)
        self.assertFalse(resource.has_released)
        await resource.release()
        self.assertTrue(resource.has_acquired)
        self.assertTrue(resource.has_released)

    async def test_acquire(self):
        resource = MockResource("test_acquire")
        self.assertNotIn(resource, resource_manager._resources)
        await resource.acquire()
        self.assertIn(resource, resource_manager._resources)
        await resource.release()

    async def test_release(self):
        resource = MockResource("test_release")
        await resource.acquire()
        await resource.release()

    async def test_resource_not_reentrant(self):
        resource = MockResource("test_not_reentrant")
        await resource.acquire()
        await resource.release()
        with self.assertRaises(EnvironmentError):
            await resource.acquire()

    async def test__release_deferred(self):
        r1 = MockResource("test_release_deferred_parent")
        r2 = MockResource("test_release_deferred_child")
        await r1.acquire()
        await r2.acquire()
        resource_manager.register(r1, r2)

        with self.assertWarns(ResourceWarning):
            del r1

        self.assertTrue(await r2._release_deferred())
        self.assertFalse(r2.acquired)

    async def test_reentrant_resource(self):
        r1 = MockResource("test_reentrant_resource")
        await r1.acquire()
        self.assertTrue(r1.acquired)
        await r1.acquire()
        self.assertTrue(r1.acquired)
        await r1.release(force=False)
        self.assertTrue(r1.acquired)
        await r1.release(force=False)
        self.assertFalse(r1.acquired)

    async def test_non_reentrant_release(self):
        r1 = MockResource("test_reentrant_resource")
        await r1.acquire()
        self.assertTrue(r1.acquired)
        await r1.acquire()
        self.assertTrue(r1.acquired)
        await r1.release()
        self.assertFalse(r1.acquired)


class TestResourceManager(AsyncTestCase):

    async def test_register(self):
        r1 = MockResource("test_register_parent")
        r2 = MockResource("test_register_child")
        resource_manager.register(r1, r2)

        self.assertIn(r2, r1.resource_state.children)

    async def test_release_children(self):
        r1 = MockResource("test_release_children")
        r2 = MockResource("test_release_child")
        resource_manager.register(r1, r2)
        await r1.acquire()
        await r2.acquire()

        self.assertTrue(r1.acquired)
        self.assertTrue(r2.acquired)

        self.assertFalse(r1.has_released)

        await r1.release()
        self.assertFalse(r1.acquired)
        self.assertTrue(r1.has_released)
        self.assertFalse(r2.acquired)
        self.assertTrue(r2.has_released)

    async def test_non_acquired_parent(self):
        r1 = MockResource("test_non_acquired_parent")
        r2 = MockResource("test_non_acquired_parent_child")
        resource_manager.register(r1, r2)

        with self.assertRaises(EnvironmentError):
            await r2.acquire()


    async def test_remove_child_binding(self):
        r1 = MockResource("test_drop_child_parent")
        r2 = MockResource("test_drop_child_child")
        resource_manager.register(r1, r2)
        self.assertIn(r2, r1.resource_state.children)
        self.assertIn(r1, r2.resource_state.parents)

        async with r1:
            await r2.acquire()
            await r2.release()

            self.assertNotIn(r2, r1.resource_state.children)
