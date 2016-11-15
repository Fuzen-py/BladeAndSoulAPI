# Unofficial BladeAndSoul API
[![Build Status](https://travis-ci.org/Fuzen-py/BladeAndSoulAPI.svg?branch=Development)](https://travis-ci.org/Fuzen-py/BladeAndSoulAPI)

---
### Usage:
```python
from BladeAndSoul import character
async def ex(user):
    c = await character(user) # Character Object
    c.pretty_profile() # Returns the prettied profile as a string
    c.pretty_stats() # Returns the prettied stats as a string
    c.pretty_gear() # Returns the prettied gear as a string
    c.pretty_outfit() # returns the prettied outfit as a string
    c['Stats'] # Dictionary Value of stats
    await c() # Same as await c.reload()
    # If you really want.. you can change char via c.name = {char} and await c()
```
better documentation to come (for now just read the doc strings in ``BladeAndSoul/bns.py``)
