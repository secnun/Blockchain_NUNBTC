import hashlib # hash 함수용 sha256 사용할 라이브러리
import json
from time import time
import random
import requests
#from flask import Flask, request, jsonify
import datetime


class Blockchain(object):

    def __init__(self):
        self.chain = [] #블록 연결 체인
        self.current_transaction = [] #블록 내 거래 내역(transaction)
        

    #새로운 거래, transaction 
    def new_transaction(self, sender, recipient, amount):
        # 거래내역 추가
        ## 현재 transaction 리스트에 송신자, 수신자 등의 거래내역을 입력
        self.current_transaction.append(
            {
                'sender' : sender, # 송신자
                'recipient' : recipient, # 수신자
                'amount' : amount, # 금액
                'timestamp': datetime.datetime.now().timestamp() # 시간
            }
        )
        return self.last_block['index'] + 1 #현재 거래내역이 들어갈 블록의 인덱스 inform 용도

    #블록생성 함수
    def new_block(self, proof, previous_hash=None):
        # 현재 블록에 이어질 새로운 블록 생성
        block = {
            'index' : len(self.chain)+1, ## 지금까지의 체인의 숫자 +1 = 새로운 블록의 인덱스
            'timestamp' : datetime . datetime .now().timestamp(), # 지금 시간 넣기(현재 block 생성 시간)
            'transactions' : self.current_transaction, ## 지금까지의 transaction을 넣기
        }

        self.current_transaction = [] # 새로 블록이 생겼으니 이제 transaction 은 다시 초기화
        self.chain.append(block)      # 기존 체인에 블록 연결 
        return block

    @property
    def last_block(self): #체인 마지막(최신) block 접근
        return self.chain[-1]


# 제네시스 블록 생성 -> 거래발생 -> 블록 생성 메커니즘
## Blcokchain Object
sample_blockchain = Blockchain()

## New Block
sample_blockchain.new_block(proof = "1") #index1 block, genesis block
#sample_blockchain.new_block(proof = "1") #index2 block
sample_blockchain.new_transaction(sender="Aliece", recipient="Bob", amount=10) #new transcation 1
sample_blockchain.new_transaction(sender="Tom", recipient="Jerry", amount=10) #new transcation 2
sample_blockchain.new_block(proof = "1") #index3 block

print(sample_blockchain.chain)
#print(sample_blockchain.current_transaction)