#!/usr/bin/env python
# coding: utf-8

from datetime import datetime, date, timedelta
import time
import random
import requests
import urllib.parse
import json
import base64
import hmac
import hashlib
import jsonpickle
import pandas as pd
import numpy as np
from itertools import chain
import progressbar


pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 500)

print("연관키워드 추출 프로그램")

# Naver Signature
class Signature:
    @staticmethod
    def generate(timestamp, method, uri, secret_key):
        message = "{}.{}.{}".format(timestamp, method, uri)
        hash = hmac.new(bytes(secret_key, "utf-8"), bytes(message, "utf-8"), hashlib.sha256)

        hash.hexdigest()
        return base64.b64encode(hash.digest())


def get_header(method, uri, api_key, secret_key, customer_id):
    timestamp = str(round(time.time() * 1000))
    signature = Signature.generate(timestamp, method, uri, secret_key)
    return {'Content-Type': 'application/json; charset=UTF-8', 'X-Timestamp': timestamp, 'X-API-KEY': api_key,
            'X-Customer': str(CUSTOMER_ID), 'X-Signature': signature}

BASE_URL = 'https://api.naver.com'
API_KEY = '<API_KEY>'
SECRET_KEY = '<SECRET_KEY>'
CUSTOMER_ID = '<CUSTOMER_ID>'

uri = '/keywordstool'
method = 'GET'
para = []

for word in all_keyword:
    word = word.replace(" ", "")
    para.append({'hintKeywords': word, 'showDetail': 1})

df = pd.DataFrame()
i = 0
wait = 0.1

print("연관키워드 추출 시작하겠습니다.")
print("등록된 키워드들이 많을 수록 소요 시간이 길다는 점을 참고하시길 바랍니다.")

bar = progressbar.ProgressBar(maxval=len(para),
                              widgets=[' [', progressbar.Timer(), '] ', progressbar.Bar(), ' (', progressbar.ETA(),
                                       ') ', ]).start()

for param in para:
    r = requests.get(BASE_URL + uri, params=param,
                     headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))

    while r.status_code != 200:
        time.sleep(wait)
        r = requests.get(BASE_URL + uri, params=param,
                         headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))
        wait += 0.1

    data = json.loads(r.text)
    data = list(data.values())
    data = data[0]
    result = pd.read_json(json.dumps(data))
    df = pd.concat([df, result])
    i += 1
    bar.update(i)

print("연관키워드 추출 완료했습니다.")

df = df.drop_duplicates()
print("중복 키워드 제거중.........")
print("중복 키워드 제거 완료!")

print("연관키워드 등록 여부 확인 중......")
df['Registered'] = np.where((df.relKeyword.isin(all_keyword)), 'true', 'false')
print("연관키워드 등록 여부 확인 완료!")

df.columns = ['연관키워드', '월간검색수PC', '월간검색수MO', '월평균클릭수PC', '월평균클릭수MO', '월평균클릭률PC', '월평균클릭률MO',
              '월평균광고노출수', '경쟁정도', '계정등록여부']
df['월간검색수PC'] = df['월간검색수PC'].replace('< 10', '1')
df['월간검색수MO'] = df['월간검색수MO'].replace('< 10', '1')

today = (datetime.today() - timedelta(days=1)).strftime("%Y%m%d")
file_name = "Relative_Keyword_" + str(today) + ".csv"
df.to_csv(file_name, encoding='utf-8-sig', index=None)

print('연관키워드 추출 성공적으로 마무리 했습니다.')
time.sleep(1)
print('3초 후에 프로그램이 종료됩니다.')
time.sleep(3)
exit(1)




print("광고그룹 데이터 수집 시작하겠습니다.")
uri = '/ncc/adgroups'
method = 'GET'
r = requests.get(BASE_URL + uri, headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))
data = r.json()
adgroup_result = pd.read_json(json.dumps(data))
print("광고그룹 데이터 수집 완료했습니다.")



print("등록된 키워드 데이터 수집 시작하겠습니다.")
uri = '/ncc/keywords'
method = 'GET'
keywords = []
for ids in adgroup_result['nccAdgroupId']:
    r = requests.get(BASE_URL + uri, params={'nccAdgroupId': ids},
                     headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))
    data = r.json()
    if len(data) > 0:
        keywords.append(pd.read_json(json.dumps(data))['keyword'].tolist())
print("등록된 키워드 데이터 수집 완료했습니다.")


all_keyword = list(chain.from_iterable(i if isinstance(i, list) else [i] for i in keywords))

print("총 {}개의 키워드가 발견되었습니다.".format(str(len(all_keyword))))

uri = '/keywordstool'
method = 'GET'
para = []

for word in all_keyword:
    para.append({'hintKeywords': word, 'showDetail': 1})


df = pd.DataFrame()
i = 0
wait = 0.1



print("연관키워드 추출 시작하겠습니다.")
print("등록된 키워드들이 많을 수록 소요 시간이 길다는 점을 참고하시길 바랍니다.")

bar = progressbar.ProgressBar(maxval = len(para),
                              widgets=[' [', progressbar.Timer(), '] ', progressbar.Bar(), ' (', progressbar.ETA(), ') ',]).start()

for param in para:
    r = requests.get(BASE_URL + uri, params=param, headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))

    while r.status_code != 200:
        time.sleep(wait)
        r = requests.get(BASE_URL + uri, params=param,
                         headers=get_header(method, uri, API_KEY, SECRET_KEY, CUSTOMER_ID))
        wait += 0.1

    data = json.loads(r.text)
    data = list(data.values())
    data = data[0]
    result = pd.read_json(json.dumps(data))
    df = pd.concat([df, result])
    i += 1
    bar.update(i)

print("연관키워드 추출 완료했습니다.")

df = df.drop_duplicates()
print("중복 키워드 제거중.........")
print("중복 키워드 제거 완료!")

print("연관키워드 등록 여부 확인 중......")
df['Registered'] = np.where((df.relKeyword.isin(all_keyword)), 'true', 'false')
print("연관키워드 등록 여부 확인 완료!")

df.columns = ['연관키워드', '월간검색수PC', '월간검색수MO', '월평균클릭수PC', '월평균클릭수MO', '월평균클릭률PC', '월평균클릭률MO',
              '월평균광고노출수', '경쟁정도', '계정등록여부']
df['월간검색수PC'] = df['월간검색수PC'].replace('< 10', '1')
df['월간검색수MO'] = df['월간검색수MO'].replace('< 10', '1')


today = (datetime.today() - timedelta(days = 1)).strftime("%Y%m%d")
file_name = "Relative_Keyword_" + str(today) + ".csv"
df.to_csv(file_name, encoding='euc-kr', index=None)

print('연관키워드 추출 성공적으로 마무리 했습니다.')
time.sleep(1)
print('3초 후에 프로그램이 종료됩니다.')
time.sleep(3)
