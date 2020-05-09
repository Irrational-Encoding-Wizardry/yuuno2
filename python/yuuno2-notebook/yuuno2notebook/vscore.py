import vapoursynth as vs
from typing import Optional, Set
from weakref import WeakSet, ref

from yuuno2.script import NOT_GIVEN
from yuuno2.resource_manager import Resource, NonAbcResource, register, on_release


######
# Vapoursynth <=R50
if not hasattr(vs, "has_policy"):
    ATOMS = {}
    GET_ENVIRONMENT_CODE = "(lambda marshal, globals_: eval(marshal.loads(b'%(source)s', globals_, globals_)))(__import__('marshal'), {'cid': %(cid)d})"

    import marshal

    from yuuno2.vapoursynth.vsscript.script import VSScript, VSScriptProvider
    from yuuno2.providers.wrapper import WrappedScript

    from yuuno2notebook.utils import run_in_main_thread

    class GlobalScript(Resource):

        def __init__(self, script, provider):
            super().__init__(script)
            self.provider = provider

        async def list_config(self):
            return ["yuuno2.notebook.default_env"] + super().list_config()

        async def get_config(self, key, default=NOT_GIVEN):
            if key == "yuuno2.notebook.default_env":
                return self.provider._is_current(self)
            return super().get_config(key, default=default)

        async def set_config(self, key, value):
            target = bool(value)

            if key == "yuuno2.notebook.default_env":
                if self.provider._is_current(self) and not target:
                    await self.provider._swap(None)
                elif not self.provider._is_current(self) and target:
                    await self.provider._swap(self)

            return super().set_config(key, value)


        async def _acquire(self):
            await self.provider.acquire()
            register(self.provider, self)

            await super()._acquire()

            self.provider._swap(self)

        async def _release(self):
            await run_in_main_thread(self.deactivate)
            await super()._release()

            self.provider._swap(None)
            await self.provider.release(force=False)


    class YuunoScriptProvider(VSScriptProvider):

        def __init__(self):
            super().__init__()
            self._current_core: Optional[GlobalScript] = None
            self._cores = []

        async def get_environment(self, core):
            def _get_env(cid):
                import vapoursynth
                from yuuno2notebook.vscore import ATOMS as atoms
                atoms[cid][0] = vapoursynth.vpy_current_environment()
            atom = [None]
            ATOMS[id(core)] = []
            code = GET_ENVIRONMENT_CODE % {
                "source": marshal.dumps(_get_env.__code__).encode("unicode_escape"),
                "cid": id(core)
            }
            await core.run(code)
            ATOMS.pop(id(core))

        async def _swap(self, core):
            if self._current_core is not None:
                env = await self.get_environment(self._current_core)
                await run_in_main_thread(lambda: self.env.__exit__(None, None, None))
                env.__exit__(None, None, None)

                await self._current_core.release(force=False)
                self._current_core = None
            
            if core is not None:
                await core.acquire()
                env = await self.get_environment(core)
                await run_in_main_thread(lambda: self.env.__enter__())
                self.env.__enter__()
                self._current_core = core

        def _is_current(self, core):
            return self._current_core is core

        async def get(self, default=False, **params):
            script = GlobalScript(super().get(**params), self)

            self._cores.append(script)
            on_release(script, lambda _: self._cores.pop(script))

            if default:
                await self._swap(script)

            return script


######
# Vapoursynth >=R51
else:
    from contextvars import ContextVar

    from yuuno2.script import ScriptProvider
    from yuuno2.vapoursynth.script import VapourSynthScript

    ctx = ContextVar("@yuuno2/notebook:vs:ctx")

    class YuunoEnvironmentPolicy(vs.EnvironmentPolicy, NonAbcResource):

        def __init__(self, *args, **kwargs):
            self.global_environment: Optional[ExplicitVapourSynthScript] = None
            self.api: Optional[vs.EnvironmentPolicyAPI] = None

            self.dead: Set[vs.EnvironmentData] = WeakSet()

        ###
        # Resource Management
        async def _acquire(self):
            vs.register_policy(self)
        
        async def _release(self):
            if self.api is not None:
                self.api.unregister_policy()

        ###
        # VapourSynth API
        def on_policy_registered(self, special_api: vs.EnvironmentPolicyAPI):
            self.api = special_api

        def on_policy_cleared(self):
            ctx.set(None)

        def is_alive(self, environment):
            return environment not in self.dead

        def set_environment(self, environment):
            global ctx

            if environment in self.dead:
                raise EnvironmentError("Environment is dead.")

            ctx.set([ref(self), environment])

        def get_current_environment(self):
            global ctx

            self.ensure_acquired_sync()

            env = ctx.get(None)
            if env is None or env[0]() is not self or env[1] in self.dead:
                return self.global_environment._env
            return env[1]

        ###
        # Yuuno-Specific API
        async def _make_env(self) -> vs.EnvironmentData:
            await self.ensure_acquired()
            return self.api.create_environment()

        async def _wrap(self, env: vs.EnvironmentData) -> vs.Environment:
            await self.ensure_acquired()
            return self.api.wrap_environment(env)


        async def _kill(self, env: vs.EnvironmentData):
            await self.ensure_acquired()
            self.dead.add(env)

        async def make_global(self, script: 'ExplicitVapourSynthScript'):
            if script is not None and script.policy is not self:
                raise ValueError("Script provider mismatch")

            if self.global_environment is not None:
                await self.global_environment.release(force=False)

            self.global_environment = script
            if script is not None:
                await self.global_environment.acquire()

        def is_global(self, script: 'ExplicitVapourSynthScript'):
            return self.global_environment is script


    class ExplicitVapourSynthScript(VapourSynthScript):

        def __init__(self, policy: YuunoEnvironmentPolicy):
            self._env: Optional[vs.EnvironmentData] = None
            self.policy = policy
            super().__init__(None)

        # Allow to overwrite the default environment
        async def list_config(self):
            return ["yuuno2.notebook.default_env"] + await super().list_config()

        async def get_config(self, key, default=NOT_GIVEN):
            if key == "yuuno2.notebook.default_env":
                return self.policy.is_global(self)
            return await super().get_config(key, default=default)

        async def set_config(self, key, value):
            target = bool(value)

            if key == "yuuno2.notebook.default_env":
                if self.policy.is_global(self) and not target:
                    await self.policy.make_global(None)
                elif not self.policy.is_global(self) and target:
                    await self.policy.make_global(self)

            return await super().set_config(key, value)

        async def _acquire(self):
            await self.policy.acquire()

            self._env = await self.policy._make_env()
            register(self.policy, self)

            self.environment = await self.policy._wrap(self._env)

            await super()._acquire()

        async def _release(self):
            await self.policy._kill(self._env)
            self._env = None

            if self.policy.is_global(self):
                await self.policy.make_global(None)

            await super()._release()

            await self.policy.release(force=False)


    class YuunoScriptProvider(ScriptProvider):

        def __init__(self):
            self.policy = YuunoEnvironmentPolicy()
            self._envs = []

        async def list(self):
            for env in tuple(self._envs):
                yield env

        async def get(self, default=False, **params):
            env = ExplicitVapourSynthScript(self.policy)

            register(self, env)
            self._envs.append(env)
            on_release(env, lambda _: self._envs.remove(env))

            if default:
                await self.policy.make_global(env)

            return env

        async def _acquire(self):
            await self.policy.acquire()
            register(self, self.policy)

        async def _release(self):
            await self.policy.release()