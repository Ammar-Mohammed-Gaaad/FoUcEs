import requests, random
base='http://127.0.0.1:8000'
print('health', requests.get(base+'/health').status_code)
email = f'multi{random.randint(10000,99999)}@example.com'
res = requests.post(base+'/api/auth/signup', json={'email':email, 'full_name':'Multi Test', 'password':'TestPass123!'})
print('signup', res.status_code, res.json())
if res.status_code != 200:
    raise SystemExit('signup failed')
token=res.json()['access_token']
headers={'Authorization':f'Bearer {token}'}
res2=requests.post(base+'/api/learning/save-style', json={'learning_styles':['visual','kinesthetic']}, headers=headers)
print('save-style', res2.status_code, res2.json())
res3=requests.put(base+'/api/learning/my-profile', json={'learning_style':['visual','kinesthetic'], 'learning_pace':4, 'goals':'test goals', 'motivation_type':'mastery'}, headers=headers)
print('upd profile', res3.status_code, res3.json())
res4=requests.get(base+'/api/learning/my-profile', headers=headers)
print('get profile', res4.status_code, res4.json())
res5=requests.post(base+'/api/tasks', json={'title':'API task multi','description':'desc','priority':2}, headers=headers)
print('create task', res5.status_code, res5.json())
res6=requests.get(base+'/api/tasks', headers=headers)
print('list tasks', res6.status_code, res6.json())