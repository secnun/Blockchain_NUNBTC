import hashlib
import json
from time import time
import random
import requests
from flask import Flask, request, jsonify
import datetime
from urllib.parse import urlparse

class Blockchain(object):

    def __init__(self):
        self.chain = [] # chain에 여러 block들 들어옴
        self.current_transaction = [] # 임시 transaction
        self.nodes = set() # Node 목록을 보관, 여러 노드 존재시 필요
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
    
    ## node 연결
    ## node_{number} 각 노드별 연결 위함.
    def register_node(self, address): # url 주소를 넣게 됨
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc) # set 자료형태 안에 목록을 저장
        
        
    # resolve_conflicts 함수 : 여러 노드 존재시, 노드간 데이터 상이한 경우 어떤 노드를 기준으로 체인을 유지할지 결정하기 위한 함수
    #다른노드와 블록길이를 비교,더 긴 블록을 인정
    def resolve_conflicts(self):
        neighbours = self.nodes # 구동되는 노드들을 저장
        new_block = None

        max_length = len(self.chain) # 내 블록의 길이 저장
        for node in neighbours:
            node_url = "http://" + str(node.replace("0.0.0.0","localhost")) + '/chain' # url을 받아서 request 통해 체인 정보 저장
            response = requests.get(node_url)
            if response.status_code == 200: # 정상적으로 웹페이지와 교류가 되면 그 정보 저장
                length = response.json()['length'] #다른 노드 길이
                chain = response.json()['chain'] #다른 노드 블록 내역
                ## 다른노드의 길이(length)가 내 노드의 길이(max_length) 보다 길고 and 내 채인이 유효한 경우
                ## 길이가 더 긴 노드를 유효한 노드로 인정
                if length > max_length and self.valid_chain(chain): # 긴 체인을 비교 >> 제일 긴 블록이 인정
                    max_length = length
                    ##  기존 노드의 정보보다 받은 정보가 최신이다. 전송 받은 블록 정보를 new_block 넣는다
                    new_block = chain
                ## 다른노드의 길이(length)가 내 노드의 길이(max_length) 보다 짧거나 or 내 체인이 유효하지 않은경우 
                else:
                    1==1  # 별도 작업 불필요
            if new_block != None:
                self.chain = new_block  # 기존 블록 정보가 잘못된 것을 인정하고 검증된 블록정보로 변경
                return True

            return False


blockchain = Blockchain()
my_ip = '0.0.0.0'
my_port = '5002' #Node 3번
node_identifier = 'node_'+my_port
mine_owner = 'master' #지갑 개념
mine_profit = 0.1 #채굴 보상


app = Flask(__name__)

@app.route('/chain', methods=['GET'])
def full_chain():
    print("chain info requested!!")
    response = {
        'chain' : blockchain.chain, 
        'length' : len(blockchain.chain), 
    }
    return jsonify(response), 200

################### 노드 연결을 위해 추가되는 함수 : 다른 Node 등록 위함.
### 노드간 연결(추가) 위함이며, 정상 노드인지 확인 및 본 노드와 기 연결된 노드에게 전파까지 수행
@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json() # json 형태로 보내면 노드가 저장이 됨
    print("register nodes !!! : ", values)
    registering_node =  values.get('nodes')
    if registering_node == None: # 요청된 node 값이 없다면! 
        return "Error: Please supply a valid list of nodes", 400
     
    ## 요청받은 노드드이 이미 등록된 노드와 중복인지 검사
    ## 중복인인 경우
    if registering_node.split("//")[1] in blockchain.nodes:
        print("Node already registered")  # 이미 등록된 노드입니다.
        response = {
            'message' : 'Already Registered Node',
            'total_nodes' : list(blockchain.nodes),
        }

    ## 중복  안되었다면
    else:  
        # 내 노드리스트에 추가
        blockchain.register_node(registering_node) 
        
        ## 이 후 해당 노드에 내정보를  등록하기
        headers = {'Content-Type' : 'application/json; charset=utf-8'}
        data = {
            "nodes": 'http://' + my_ip + ":" + my_port
        }
        print("MY NODE INFO " , 'http://' + my_ip + ":" + my_port)
        requests.post( registering_node + "/nodes/register", headers=headers, data=json.dumps(data))
        
        # 이후 주변 노드들에도 새로운 노드가 등장함을 전파
        for add_node in blockchain.nodes:
            if add_node != registering_node.split("//")[1]:
                print('add_node : ', add_node)
                ## 노드 등록하기
                headers = {'Content-Type' : 'application/json; charset=utf-8'}
                data = {
                    "nodes": registering_node
                }
                requests.post('http://' + add_node   + "/nodes/register", headers=headers, data=json.dumps(data))

        response = {
            'message' : 'New nodes have been added',
            'total_nodes' : list(blockchain.nodes),
        }
    return jsonify(response), 201


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json() 
    print("transactions_new!!! : ", values)
    required = ['sender', 'recipient', 'amount'] 

    if not all(k in values for k in required):
        return 'missing values', 400

    index = blockchain.new_transaction(values['sender'],values['recipient'],
values['amount'])
        
    response = {'message' : f'Transaction will be added to Block {index}'}

    ################### 노드 연결
    ## 본 노드에 받은 거래내역 정보를 다른 노드들에 다같이 업데이트 수행
    # type을 통해 신규 거래내역과 다른 노드 전파용 거래내역을 구분
    if "type" not in values:  ## 신규로 추가된 경우 type 이라는 정보가 포함되어 있지 않음. 해당 내용은 전파 필요
        for node in blockchain.nodes:  # nodes에 저장된 모든 노드에 정보를 전달한다.
            headers = {'Content-Type' : 'application/json; charset=utf-8'}
            data = {
                "sender": values['sender'],
                "recipient": values['recipient'],
                "amount": values['amount'],
                "type" : "sharing"   # 전파이기에 sharing이라는 type 이 꼭 필요
            }
            requests.post("http://" + node  + "/transactions/new", headers=headers, data=json.dumps(data))
            print("share transaction to >>   ","http://" + node )

    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
    print("MINING STARTED")    
    last_block = blockchain.last_block
    last_proof = last_block['nonce']
    proof = blockchain.pow(last_proof)  

    blockchain.new_transaction(
        sender=mine_owner, 
        recipient=node_identifier, 
        amount=mine_profit # coinbase transaction 
    )
 
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)
    print("MINING FINISHED")

    ################### 노드 연결을 위해 추가되는 부분
    for node in blockchain.nodes: # nodes에 연결된 모든 노드에 작업증명(PoW)가 완료되었음을 전파
        headers = {'Content-Type' : 'application/json; charset=utf-8'}
        data = {
            "miner_node":  'http://' + my_ip + ":" + my_port,
            'new_nonce' : blockchain.last_block['nonce']
        }
            
        alarm_res = requests.get("http://" + node  + "/nodes/resolve", headers=headers, data =json.dumps(data) ) 
        
        if "ERROR" not in alarm_res.text : # 전파 받은 노드의 응답에 ERROR라는 이야기가 없으면 (나의 PoW가 인정 받으면)
            ## 정상 response
            response = {
                'message' : 'new block completed',
                'index' : block['index'],
                'transactions' : block['transactions'],
                'nonce' : block['nonce'],
                'previous_hash' : block['previous_hash']
            }
            
        else : # 전파 받은 노드의 응답에 이상이 있음을 알린다면?
            ## 내 PoW가 이상이 있을수 있기에 다시 PoW 진행!
            block = blockchain.new_block(proof, previous_hash)
          
    return jsonify(response), 200

##### 타 노드에서 블록 생성내용을 전파하였을떄 검증작업 수행
## 채굴 전파 내용을 그대로 받아들이는 것이 아닌 알맞은 작업인지, 조작이 없었는지 검증
@app.route('/nodes/resolve', methods=['GET'])
def resolve():
    requester_node_info =  request.get_json()
    required = ['miner_node'] # 해당 데이터가 존재해야함
    # 데이터가 없으면 에러를 띄움
    if not all(k in requester_node_info for k in required):
        return 'missing values', 400   
    
    
    ## 그전에 우선 previous 에서 바뀐것이 있는지 점검하자!!
    my_previous_hash =  blockchain.last_block['previous_hash']
    print(my_previous_hash)
    
    last_proof = blockchain.last_block['nonce']
    
    headers = {'Content-Type' : 'application/json; charset=utf-8'}
    miner_chain_info = requests.get(requester_node_info['miner_node']  + "/chain", headers=headers)
    ##초기 블록은 과거 이력 변조내역 확인 할 필요가 없다
        
    print("다른노드에서 요청이 온 블록, 검증 시작")
    new_block_previous_hash = json.loads(miner_chain_info.text)['chain'][-2]['previous_hash']
    # 내 노드의 전(previous)해시랑 새로만든 노드의 전(previous)해시가 같을때 정상
    if my_previous_hash == new_block_previous_hash  and  \
                hashlib.sha256(str(last_proof + int(requester_node_info['new_nonce'])).encode()).hexdigest()[:4] == "0000" : 
                # 정말 PoW의 조건을 만족시켰을까? 검증하기
        print("다른노드에서 요청이 온 블록, 검증결과 정상!!!!!!")

        replaced = blockchain.resolve_conflicts() # 결과값 : True Flase  / True 면 내 블록에 길이가 짧아 대체되어야 한다.

        # 체인 변경 알림 메시지
        if replaced == True:
            ## 내 체인이 짧아서 대체되어야 함
            print("REPLACED length :",len(blockchain.chain))
            response = {
                'message' : 'Our chain was replaced >> ' +  my_ip + ":"+ my_port,
                'new_chain' : blockchain.chain
            }
        else:
            ## 내 체인이 제일 길어서 권위가 있음
            response = {
                'message' : 'Our chain is authoritative',
                'chain' : blockchain.chain
            }
    #아니면 무엇인가 과거데이터가 바뀐것이다!!
    else:
        print("다른노드에서 요청이 온 블록, 검증결과 이상발생!!!!!!!!")
        response = {
            'message' : 'Our chain is authoritative>> ' +  my_ip + ":"+ my_port,
            'chain' : blockchain.chain
        }            


    return jsonify(response), 200

if __name__ == '__main__':
    app.run(host=my_ip, port=my_port)
