from flask import Flask
from datetime import datetime
from flask import render_template
import requests
import os
import json
import pandas as pd
import random

app = Flask(__name__, template_folder=os.getcwd())

node_port_list = ['5000','5001','5002']

@app.route('/')
def index():
    headers = {'Content-Type' : 'application/json; charset=utf-8'}
        # 블록 체인 내 블록 정보를 제공하는 url(http://localhost:5000/chain)에 request 방식으로 데이터를 요청
    node_id = random.choice(node_port_list)
    res = requests.get("http://localhost:" + node_id + "/chain", headers=headers)
    print("Selected Node : ", node_id)
    # 요청 결과 데이터(res.text)를 json 으로 로드
    status_json = json.loads(res.text)
    # 결과 데이터를 pandas의 dataframe(df_scan)으로  정리
    df_scan = pd.DataFrame(status_json['chain'] )
     # Front 구성내용이 담길 html(one_node_scan.html)파일에 Dataframe 정보(df_scan)과 블록의 길이(block_len)을 제공
    return render_template('/scan_page.html', df_scan = df_scan, block_len = len(df_scan))

app.run(port=8080)