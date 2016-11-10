import asyncio
import aiohttp
from bs4 import BeautifulSoup

# Todo: Create Custom Exceptions

try:
    import lxml
    parser = 'lxml'

except ImportError:
    parser = 'html.parser'

# Todo: Blade and soul Class remodel
# types of weapons in game
VALID_WEAPONS = ['dagger', 'sword', 'staff', 'razor', 'axe', 'bangle', 'gauntlet', 'lynblade', 'bracer']
# types of accessories in game
VALID_ACCESSORIES = ['necklace', 'earring', 'bracelet', 'ring', 'belt', 'energy', 'soul']
PROFILE_URL = 'http://na-bns.ncsoft.com/ingame/bs/character/profile'  # ?c=Char
SEARCH_URL = 'http://na-bns.ncsoft.com/ingame/bs/character/search/info'  # ?c=Char
SUGGEST_URL = 'http://na-search.ncsoft.com/openapi/suggest.jsp'  # ?site=bns&display=10&collection=bnsusersuggest&query=char

def _float(var):
    if var in [None, False]:
        return 0
    if var is True:
        return 1
    if isinstance(var, float):
        return var
    if isinstance(var, int):
        return float(int)
    assert isinstance(var, str)
    assert any(x.isnumeric() for x in var)
    var = var.split()[-1]
    while len(var) > 0 and not var[-1].isnumeric():
        var = var[:-1]
    while len(var) > 0 and not var[0].isnumeric():
        var = var[1:]
    return float(var)

def _math(var1, var2, string=True, percent=False):
    if string:
        if percent:
            return '{}% - {}% = {}%'.format(var1, var2, var1-var2)
        return '{} - {} = {}'.format(var1, var2, var1-var2)
    if percent:
        return str(var1) + '%', str(var2) + '%', str(var1-var2) + '%'
    return var1, var2, var1-var2



async def search_user(user, suggest=True, max_count=3) -> list:
    soup = await fetch_url(SEARCH_URL, params={'c': user})
    search = soup.find('div', class_='searchList')
    if suggest:
        return [(x.dl.dt.a.text, [b.text for b in x.dl.find('dd', class_='other').dd.find_all('li')]) for x in
                search.find_all('li') if x.dt is not None][:max_count]
    return (search.li.dl.dt.a.text,
            [x.text for x in search.li.dl.find('dd', class_='other').dd.find_all('li') if x is not None])


def get_name(gear_item):
    try:
        gear_item = gear_item.find('div', class_='name')
        if not gear_item:
            return None
        if gear_item.find('span', class_='empty') is not None:
            return None
        return gear_item.span.text
    except AttributeError:
        return None


def set_bonus(set_) -> tuple:
    return (':\n'.join(('\n'.join((t.strip() for t in z.text.strip().split('\n') if t.strip() != '')) for z in x)) for x
            in dict(zip(set_.find_all('p', class_='discription'), set_.find_all('p', class_='setEffect'))).items())


async def fetch_url(url, params={}) -> BeautifulSoup:
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=params) as re:
            return BeautifulSoup(await re.text(), parser)


async def fetch_profile(user) -> dict:
    CharacterName, other_chars = await search_user(user, suggest=False)
    soup = await fetch_url(PROFILE_URL, params={'c': CharacterName})
    # INFORMATION
    Name = soup.find('a', href='#').text
    CharacterName = soup.find('dt').span.text[1:-1]
    Class, Level, Server, *Faction = [x.text.strip().replace('\xa0', ' ') for x in
                                      soup.find('dd', class_='desc').find_all('li')]
    if len(Faction) == 0:
        Clan = Rank = Faction = None
    elif len(Faction) == 1:
        Faction = Faction[0].split()
        Rank = ' '.join(Faction[2:])
        Faction = ' '.join(Faction[:2])
        Clan = None
    else:
        Clan = Faction[1]
        Faction = Faction[0].split()
        Rank = ' '.join(Faction[2:])
        Faction = ' '.join(Faction[:2])
    Level = Level.split()
    if len(Level) > 2:
        HM = int(Level[-1])
    else:
        HM = 0
    Level = int(Level[1])

    # ATTACK
    ATK = soup.find('div', class_='attack').dl
    sub = [z for z in (dict(zip((z.text for z in x.find_all('span', class_='title')),
                                (z.text for z in x.find_all('span', class_='stat-point')))) for x in ATK.find_all('dd')) if len(z)][:-2]
    temp = ATK.find_all('dt')[:-2]
    ATK = dict(
        zip([t.find('span', class_='title').text for t in temp], [t.find('span', 'stat-point').text for t in temp]))
    del ATK['Mastery']
    [ATK.update({x: {'Total': ATK.get(x)}}) for x in ATK.keys()]
    ATK['Attack Power'].update(sub[0])
    ATK['Piercing'].update(sub[2])
    ATK['Accuracy'].update(sub[3])
    ATK['Critical Hit'].update(sub[5])
    ATK['Critical Damage'].update(sub[6])

    # DEFENSE
    Defense = soup.find('div', class_='defense')
    temp = Defense.dl.find_all('dt')
    sub = [z for z in (dict(zip((z.text for z in x.find_all('span', class_='title')),
                                (z.text for z in x.find_all('span', class_='stat-point')))) for x in Defense.find_all('dd')) if len(z)]
    Defense = dict(
        zip([t.find('span', class_='title').text for t in temp], [t.find('span', 'stat-point').text for t in temp]))
    [Defense.update({x: {'Total': Defense.get(x)}}) for x in Defense.keys()]
    del Defense['Debuff Defense']
    Defense['Defense'].update(sub[1])
    Defense['Evolved Defense'].update(sub[2])
    Defense['Evasion'].update(sub[3])
    Defense['Block'].update(sub[4])
    Defense['Critical Defense'].update(sub[5])
    Defense['Health Regen'].update(sub[7])
    Defense['Recovery'].update(sub[8])

    # GEAR
    Weapon = get_name(soup.find('div', class_='wrapWeapon'))
    Necklace = get_name(soup.find('div', class_='wrapAccessory necklace'))
    Earring = get_name(soup.find('div', class_='wrapAccessory earring'))
    Ring = get_name(soup.find('div', class_='wrapAccessory ring'))
    Bracelet = get_name(soup.find('div', class_='wrapAccessory bracelet'))
    Belt = get_name(soup.find('div', class_='wrapAccessory belt'))
    Soul = get_name(soup.find('div', class_='wrapAccessory soul'))

    # SoulSheild
    SS = soup.find('div', class_='wrapGem')
    BONUS = ()
    Stats = ()
    if any(x.img is not None for x in SS.find_all('span')):
        BONUS = set_bonus(SS.find('div', class_='lyCharmEffect'))
        Stats = ([': '.join([tr.th.text, tr.td.text]) for tr in SS.table.find_all('tr')])
    # OUTFIT
    Clothes = get_name(soup.find('div', class_='wrapAccessory clothes'))
    Head = get_name(soup.find('div', class_='wrapAccessory tire'))
    Face = get_name(soup.find('div', class_='wrapAccessory faceDecoration'))
    Adornment = get_name(soup.find('div', class_='wrapAccessory clothesDecoration'))

    # PROFILEPICTURE
    Picture = soup.find('section').div.div.img.get('src')
    del soup, temp, sub
    r = {'Account Name': Name,
            'Character Name': CharacterName,
            'Class': Class,
            'Level': Level,
            'HM Level': HM,
            'Server': Server,
            'Faction': Faction,
            'Clan': Clan,
            'Faction Rank': Rank,
            'Picture': Picture,
            'Stats': {},
            'Gear': {
                'Weapon': Weapon,
                'Necklace': Necklace,
                'Earring': Earring,
                'Ring': Ring,
                'Bracelet': Bracelet,
                'Belt': Belt,
                'Soul': Soul},
            'SoulSheild': Stats,
            'Set Bonus': '\n\n'.join(BONUS),
            'Outfit': {'Clothes': Clothes,
                       'Head': Head,
                       'Face': Face,
                       'Adornment': Adornment},
            'Other Characters': other_chars}
    r['Stats'].update(ATK)
    r['Stats'].update(Defense)
    return r


def suggest_chars(search: BeautifulSoup) -> list:
    x = [x.dt.a.text for x in search.ul.find_all('li') if x is not None or x.dt is not None]


class Character:
    def __init__(self, data: dict):
        data = data.copy()
        self.__name__ = data['Character Name']
        self.__data = data
        self.stats
        self.name = __name__
        self.account = data['Account Name']

    async def refresh(self):
        self.__data = await fetch_profile(self.__name__)

    def __getattr__(self, item):
        return self[str(item)]

    def __getitem__(self, item):
        item = str(item).replace('_', ' ')
        k = list(self.__data.keys())
        k = dict(zip([z.lower() for z in k], k))
        return self.__data[k.get(item.lower())]

    def pretty_profile(self):
        if self['HM Level']:
            temp = 'Level {} Hongmoon Level {}'.format(self['Level'], self['HM Level'])
        else:
            temp = 'Level {}'.format(self['Level'])
        text = ['**Display Name:** {}'.format(self['Account Name']),
                '**Character**: {} {}'.format(self['Character Name'], temp),
                '**Weapon**: {}'.format(self['Gear']['Weapon']),
                '**Server:** {}'.format(self['Server'])]
        if self['Faction']:
            if self['Faction'] == 'Cerulean Order':
                text.append('**Faction:** Cerulean Order :blue_heart:')
            else:
                text.append('**Faction"** Crimson Legion :heart:')
            text.append('**Faction Rank:** {}'.format(self['Faction Rank']))
            if self['Clan']:
                text.append('**Clan:** {}'.format(self['Clan']))
        if len(self['Other Characters']):
            temp = ['[', ']']
            temp.insert(1, ', '.join(self['Other Characters']))
            text.append('**Other Characters:**\n {}'.format(''.join(temp)))
        text.append(self['Picture'])
        return '\n'.join(text).strip()

    def pretty_gear(self):
        temp = [self['Character Name'], '[' + self['Class'],'Level', str(self['Level'])]
        if self['HM Level']:
            temp += ['Hongmoon Level', str(self['HM Level'])]
        temp = ' '.join(temp) + ']'
        divider = '─'*len(temp)
        stats = self['Stats']
        send_this = ['```', temp, divider, 'Total HP {}    Attack Power {}'.format(stats['HP']['Total'], stats['Attack Power']['Total']),
                     divider, 'Soul Shield Attributes (Base + Fused + Set)', '\n'.join(self['SoulSheild']),
                     ''.join(self['Set Bonus']), '']
        gear = self['Gear']
        temp = list(gear.keys())
        temp.sort()
        for k in temp:
            send_this.append('{}: {}'.format(k, gear[k]))
        send_this.append(divider)
        send_this.append('```')
        return '\n'.join(send_this).strip()

    def pretty_stats(self):

        temp = [self['Character Name'], '[' + self['Class'] + ',','Level', str(self['Level'])]
        if self['HM Level']:
            temp += ['Hongmoon Level', str(self['HM Level'])]
        temp = ' '.join(temp) + ']'
        divider = '─'*len(temp)
        stats = self['Stats']
        send_this = ['```ruby', temp, divider, 'HP: {}'.format(stats['HP']['Total']),
                     'Attack Power: {}'.format(stats['Attack Power']['Total']),
                     'Piercing: {}'.format(stats['Piercing']['Total']),
                     '+Defense Piercing: {}'.format(stats['Piercing']['Defense Piercing']),
                     '+Block Piercing: {}'.format(stats['Piercing']['Block Piercing']),
                     'Accuracy: {0[Total]} ({0[Hit Rate]})'.format(stats['Accuracy']),
                     'Critical Hit: {0[Total]} ({0[Critical Rate]})'.format(stats['Critical Hit']),
                     'Critical Damage: {0[Total]} ({0[Increase Damage]})'.format(stats['Critical Damage']), divider,
                     'Defense: {0[Total]} ({0[Damage Reduction]})'.format(stats['Defense']),
                     'Evasion: {}'.format(stats['Evasion']['Total']),
                     '+Evasion Rate: {}'.format(stats['Evasion']['Evasion Rate']),
                     '+Counter Bonus: {}'.format(stats['Evasion']['Counter Bonus']),
                     ('Block: {0[Total]}\n'
                      '+Damage Reduction: {0[Damage Reduction]}\n'
                      '+Block Bonus: {0[Block Bonus]}\n'
                      '+Block Rate: {0[Block Rate]}').format(stats['Block']),
                     'Health Regen (IN/OUT): {0[In Combat]}/{0[Out of Combat]}'.format(stats['Health Regen']),
                     'Recovery Rate: {}'.format(stats['Recovery']['Total']),
                     '```']
        return '\n'.join(send_this)

    def pretty_outfit(self):
        outfit = self['Outfit']
        o = list(outfit.keys())
        o.sort()
        return '\n'.join(['```'] + ['{}\'s Outfit:'.format(self['Character Name'])] +
                         ['{}: {}'.format(k, outfit[k]) for k in o] + ['```'])

async def get_character(user: str) -> Character:
    return Character(await fetch_profile(user))

async def compare(user1: Character, user2: Character, update=False):
    assert isinstance(user1, Character) and isinstance(user2, Character)
    if update:
        await user1.refresh()
        await user2.refresh()
    temp = '{}  -  {}'.format(user1['Character Name'], user2['Character Name'])
    divider = '─'*len(temp)
    user1 = user1['Stats']
    user2 = user2['Stats']

    for k,v in user1.items():
        for k2,v2 in v.items():
            v[k2] = _float(v2)
        user1[k] = v
    for k,v in user2.items():
        for k2,v2 in v.items():
            v[k2] = _float(v2)
        user2[k] = v

    send_this = [temp, divider, 'HP: {}'.format(_math(user1['HP']['Total'], user2['HP']['Total'])),
                 'Attack Power: {}'.format(_math(user1['Attack Power']['Total'],
                                                 user2['Attack Power']['Total'])),
                 'Piercing: {}'.format(_math(user1['Piercing']['Total'], user2['Piercing']['Total'])),
                 '+Defense Piercing: {}'.format(_math(user1['Piercing']['Defense Piercing'],
                                                      user2['Piercing']['Defense Piercing'],
                                                      percent=True)),
                 '+Block Piercing: {}'.format(_math(user1['Piercing']['Block Piercing'],
                                                    user2['Piercing']['Block Piercing'],
                                                    percent=True)),
                 'Accuracy: {}'.format(_math(user1['Accuracy']['Total'],
                                             user2['Accuracy']['Total'])),
                 '+']
    return '\n'.join(send_this)
