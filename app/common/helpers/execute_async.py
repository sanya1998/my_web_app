import asyncio
from typing import Coroutine


# TODO: попробовать asyncio.run()
def execute_async(func: Coroutine):
    """
    Использовать следующим образом:
    ```
    async def func(*args, **kwargs):
        pass

    execute_async(func(*args, **kwargs))
    ```
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func)
    loop.close()
