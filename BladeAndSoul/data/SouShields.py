import yaml
from os import path
p = path.split(path.abspath(__file__))[0]
with open(path.join(p, 'SS.yml')) as f:
    SS = yaml.safe_load(f)
for k,v in SS.items():
    for k2, v2 in v.items():
        text = ['{}: {}'.format(k3, v3) for k3, v3 in v2.items()]
        text.sort()
        v[k2] = '\n'.join(text)
    SS[k] = v