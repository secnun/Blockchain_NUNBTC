import hashlib # hash 함수용 sha256 사용할 라이브러리
import json
from time import time
import random
import requests
from flask import Flask, request, jsonify
import datetime


class Blockchain(object):

    def __init__(self):
        self.chain = [] # chain에 여러 block들 들어옴
        self.current_transaction = [] # 임시 transaction
        self.nodes = set() # Node 목록을 보관
        self.new_block(previous_hash=1, proof=100) #genesis block 생성

    @staticmethod #new_block 에서 이전 블록 해싱 활용
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode() 
        return hashlib.sha256(block_string).hexdigest()

    @property #변수 취급 위함
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof, proof):
        guess = str(last_proof + proof).encode()          # 전(previous) proof와 구할 proof 문자열 연결 -> 전 블록과의 연관성 강화.
        guess_hash = hashlib.sha256(guess).hexdigest()    # 이 hash 값 저장
        return guess_hash[:4] == "0000" # 앞 4자리가 0000 이면 True (알맞은 nonce값을 찾음) -> 기존 BTC라면 10분에 1블록 생성 기준으로 블록내 "난이도"값을 참조하게 됨.

    def pow(self, last_proof):
        proof = random.randint(-1000000,1000000)
        while self.valid_proof(last_proof, proof) is False: # valid proof 함수 활용(아래 나옴), 맞을 때까지 반복적으로 검증
            proof = random.randint(-1000000,1000000)
        return proof

    def new_transaction(self, sender, recipient, amount):
        self.current_transaction.append(
            {
                'sender' : sender, # 송신자
                'recipient' : recipient, # 수신자
                'amount' : amount, # 금액
                'timestamp':time()
            }
        )
        return self.last_block['index'] + 1 #현 트랜잭션 해당 블록 반환(inform)용

    def new_block(self, proof, previous_hash=None):
        block = {
            'index' : len(self.chain)+1,
            'timestamp' : time(), 
            'transactions' : self.current_transaction,
            'nonce' : proof, #채굴과정에서 난수값이 proof
            'previous_hash' : previous_hash or self.hash(self.chain[-1]), #genesis block 고려
        }
        self.current_transaction = []
        self.chain.append(block)     
        return block

    def valid_chain(self, chain): #전 블록 변경사항 감지. 검증 과정.
        last_block = chain[0] 
        current_index = 1

        while current_index < len(chain): 
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n--------\n")
            if block['previous_hash'] != self.hash(last_block):
                return False
            last_block = block
            current_index += 1
        return True


# 1. 객체 생성
blockchain = Blockchain()

# 2. 트랜잭션 추가
blockchain.new_transaction("Alice", "Bob", 10)
blockchain.new_transaction("Bob", "Charlie", 5)

# 3. 마지막 블록의 proof 가져오기
last_proof = blockchain.last_block['nonce']

# 4. Proof of Work 수행
proof = blockchain.pow(last_proof)

# 5. 새 블록 생성
previous_hash = blockchain.hash(blockchain.last_block)
new_block = blockchain.new_block(proof, previous_hash)
chain = self.chain

print(new_block)

