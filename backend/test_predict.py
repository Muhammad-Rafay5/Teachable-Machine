import requests, os, json

path = None
for dirpath, dirnames, filenames in os.walk('dataset'):
    for fn in filenames:
        if fn.lower().endswith(('.jpg','.jpeg','.png','.bmp','.webp')) and 'cat' in dirpath.lower():
            path = os.path.join(dirpath, fn)
            break
    if path:
        break

if not path:
    print('No cat image found in dataset')
    raise SystemExit(1)

print('using', path)
with open(path, 'rb') as f:
    files = {'file': (os.path.basename(path), f, 'image/jpeg')}
    r = requests.post('http://127.0.0.1:8000/predict', files=files, timeout=60)
    print('status', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print(r.text)
