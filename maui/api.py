from functools import reduce
from pprint import pprint
from typing import Sequence, Tuple

import requests

from graph import Graph

spring_id = 71
spring_id_legacy = 20178


def modify_string(p: str, repl: Sequence[Tuple[str, str]]) -> str:
    return reduce(lambda a, kv: a.replace(*kv), repl, p)


url = 'https://api.maui.uiowa.edu/maui/api/pub/registrar/sections'
subject = 'ece'
payload = "json={{sessionId: {}, courseSubject: '{}'}}".format(str(spring_id), subject)
response = requests.get(url=url, params=payload)

if response.status_code != 200:
    print('Error: HTTP {}'.format(response.status_code))

data = response.json()
raw_courses = data['payload']

courses_with_prereqs = list(filter(lambda x: x['prerequisite'] is not None, raw_courses))

replacements = (' ', ''), ('and', '+'), ('or', '?')
for d in courses_with_prereqs:
    d.update((k, modify_string(v, replacements)) for k, v in d.items() if k ==
             'prerequisite')

prereqs = {map(lambda x: x['prerequisite'], courses_with_prereqs)}

pairings = {(x['subjectCourse'], x['prerequisite']) for x in courses_with_prereqs}

courses = set()
replacements = ('(', ''), (')', ''), ('+', ','), ('?', ',')
for pair in pairings:
    courses.add(pair[0])
    for prereq in modify_string(pair[1], replacements).split(','):
        courses.add(prereq)

pprint(courses)
print(len(courses))

connections = []
for pair in pairings:
    pprint('{} => {}'.format(pair[0], pair[1]))

# g = Graph(directed=True)


# 'ECE:5220 => (BIOS:4120?STAT:3510)+BME:5320+(CS:5110?ENGR:1300)'
# ('BIOS:4120?', 'ECE:5220',