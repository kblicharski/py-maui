from functools import reduce
from pprint import pprint
from typing import Sequence, Tuple

import requests

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
    pprint('{} => {}'.format(pair[0], pair[1]))
    for prereq in modify_string(pair[1], replacements).split(','):
        courses.add(prereq)

pprint(courses)
print(len(courses))
