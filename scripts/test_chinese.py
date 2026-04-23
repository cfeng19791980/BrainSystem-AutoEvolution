import requests

r = requests.post('http://127.0.0.1:5002/entry', json={'content': 'brain hook 如何工作'})
d = r.json()
print('Success:', d['success'])
print('Intent:', d['brain_context']['intent']['type'])
print('Trigger:', d['brain_context']['trigger_detected'])
print('Results:')
for x in d['brain_context']['results']:
    print(f"  - {x['source']}: score={x['score']:.3f}")