# Unofficial BladeAndSoul API
[![Build Status](https://travis-ci.org/Fuzen-py/BladeAndSoulAPI.svg?branch=Development)](https://travis-ci.org/Fuzen-py/BladeAndSoulAPI)

---
### Usage:
```python
from BladeAndSoul import character
async def ex(user):
    c = character(user) # Character Object
    c.pretty_profile() # Returns the profile as a string
    c.pretty_stats() # Returns the stats as a string
    c.pretty_gear() # Returns the gear as a string
    c.pretty_outfit() # returns the outfit as a string
    c['Stats'] # Dictionary Value of stats
```
better documentation to come...
