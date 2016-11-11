import asyncio; loop = asyncio.get_event_loop()
from time import sleep
from BladeAndSoul import character
async def func(name):
    c = await character(name)
    assert isinstance(c.Stats, dict)
    c.pretty_profile()
    c.pretty_gear()
    c.pretty_outfit()
    c.pretty_stats()

def test_mytest():
    loop.run_until_complete(func('Yui'))
