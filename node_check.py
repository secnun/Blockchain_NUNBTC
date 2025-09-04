import requests
import json
import pandas as pd
import hashlib
import random


#트랜잭션 입력 -> 채굴 -> 블록생성(블록넘버+1) -> 블록 확인 -> 트랜잭션 입력 -> ...
#1. 노드 블록정보 확인
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5000/chain", headers=headers)
print(json.loads(res.content))
'''

#2. 트랜잭션 입력 확인 (블록생성X, current block list에만 추가 상태)
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
data = {
        "sender": "test_from",
        "recipient": "test_to4",
        "amount": 3,
        "smart_contract": {"contract_address":"myaddress"}
}
response=requests.post("http://localhost:5000/transactions/new", headers=headers, data=json.dumps(data))
print(response.status_code)  #테스트용 출력
print(response.json()) #테스트용 출력
'''


#3. 채굴
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5000/mine")
print(res)
'''


#4. pandas 활용 거래내역 확인
'''
headers = {'Content-Type' : 'application/json; charset=utf-8'}
res = requests.get("http://localhost:5000/chain", headers=headers)

res.text

status_json = json.loads(res.text)
status_json['chain']    
tx_amount_l = []
tx_sender_l = []
tx_reciv_l  = []
tx_time_l   = []

for chain_index in range(len(status_json['chain'])):
    chain_tx = status_json['chain'][chain_index]['transactions']
    for each_tx in range(len(chain_tx)):
        tx_amount_l.append(chain_tx[each_tx]['amount'])
        tx_sender_l.append(chain_tx[each_tx]['sender'])
        tx_reciv_l.append(chain_tx[each_tx]['recipient'])
        tx_time_l.append(chain_tx[each_tx]['timestamp'])

df_tx = pd.DataFrame()
df_tx['timestamp'] = tx_time_l  
df_tx['sender'] = tx_sender_l 
df_tx['recipient'] = tx_reciv_l
df_tx['amount'] = tx_amount_l   
print(df_tx)

#5. 추가 - 잔고 조회(계정별)
print("=============잔액조회=============")
df_sended = pd.DataFrame(df_tx.groupby('sender')['amount'].sum()).reset_index()
df_sended.columns = ['user','sended_amount']
df_received= pd.DataFrame(df_tx.groupby('recipient')['amount'].sum()).reset_index()
df_received.columns = ['user','received_amount']
print(df_received)

df_status = pd.merge(df_received,df_sended, on ='user', how=  'outer').fillna(0)
df_status['balance'] = df_status['received_amount']  - df_status['sended_amount']  
print(df_status)
'''