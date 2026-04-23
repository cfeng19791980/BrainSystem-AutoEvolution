import requests

r = requests.post('http://127.0.0.1:5002/entry', json={'content': 'vector search config'})
d = r.json()
print('Success:', d['success'])
print('Intent:', d['brain_context']['intent'])
print('Results:')
for x in d['brain_context']['results']:
    print(f"  - {x['source']}: score={x['score']:.3f}")