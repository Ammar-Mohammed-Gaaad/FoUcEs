import requests
BASE_URL='http://127.0.0.1:8000'
print('health', requests.get(f'{BASE_URL}/health').status_code)

u='apitest@example.com'
res=requests.post(f'{BASE_URL}/api/auth/signup', json={'email':u,'full_name':'API Test','password':'TestPass123!'})
print('signup', res.status_code, res.text)

res=requests.post(f'{BASE_URL}/api/auth/login?email={u}&password=TestPass123!')
print('login', res.status_code, res.text)

if res.status_code!=200:
    raise SystemExit('login failed')

token=res.json()['access_token']
hdr={'Authorization':f'Bearer {token}'}

a=requests.post(f'{BASE_URL}/api/learning/save-style', params={'learning_style':'kinesthetic'}, headers=hdr)
print('save-style', a.status_code, a.text)

b=requests.get(f'{BASE_URL}/api/tasks', headers=hdr)
print('get-tasks', b.status_code, b.text)

c=requests.post(f'{BASE_URL}/api/tasks', json={'title':'test task','description':'desc','priority':2}, headers=hdr)
print('create-task', c.status_code, c.text)
