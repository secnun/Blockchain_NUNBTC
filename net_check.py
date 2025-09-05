import requests
import json
import pandas as pd
import hashlib 
import random



headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5000/chain", headers=headers)
print(json.loads(res.content))


'''
## 노드 등록하기
#아래는 노드1번에 노드2번을 등록하는 과정
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
    "nodes": 'http://localhost:5001'
}
requests.post("http://localhost:5000/nodes/register", headers=headers, data=json.dumps(data)).content
'''

'''
## 트랜잭션 발생(거래 생성)
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
        "sender": "test_from",
        "recipient": "test_to",
    "amount": 3,
}
requests.post("http://localhost:5000/transactions/new", headers=headers, data=json.dumps(data)).content
'''

'''
#위에서 발생시킨 트랜잭션 기록을 위해 채굴 실시
headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5002/mine")
print(res)
'''