import json

ar = []

with open('banwolrd.txt', encoding='utf-8') as r:
    for i in r:
        n = i.lower().split('\n')[0]
        if n != '':
            ar.append(n)

with open('banwolrd.json', 'w' ,encoding='utf-8') as r:
    json.dump(ar, r)


