# author：墨雨微晴
# date：2023/01/16
# note：企查查批量查询接口，可以获取多条企业信息，且速度较快
# note：需要填写自己的账号cookie，且最大的单次爬取数量取决于自己的账号等级，如vip为5000条，svip为10000条

import requests
import json
import re
import os
import hmac
import time
import hashlib
import datetime
import logging
import pandas as pd

# user_cookie
# 用户cookie，填写自己的用户cookie
cookie = ''

def get_pid_tid():
    url = 'https://www.qcc.com/web/search/advance?hasState=true'

    headers = {
        'accept-encoding': 'gzip, deflate, br'
        ,'accept-language': 'zh-CN,zh;q=0.9'
        ,'cache-control': 'max-age=0'
        ,'cookie': cookie
        ,'referer': 'https://www.qcc.com/'
        ,'sec-fetch-dest': 'document'
        ,'sec-fetch-mode': 'navigate'
        ,'sec-fetch-site': 'same-origin'
        ,'sec-fetch-user': '?1'
        ,'upgrade-insecure-requests': '1'
        ,'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'''
    }

    res = requests.get(url, headers=headers).text
    try:
        pid = re.findall("pid='(.*?)'", res)[0]
        tid = re.findall("tid='(.*?)'", res)[0]
    except:
        pid = ''
        tid = ''

    return pid, tid

def seeds_generator(s):
    seeds = {
        "0": "W",
        "1": "l",
        "2": "k",
        "3": "B",
        "4": "Q",
        "5": "g",
        "6": "f",
        "7": "i",
        "8": "i",
        "9": "r",
        "10": "v",
        "11": "6",
        "12": "A",
        "13": "K",
        "14": "N",
        "15": "k",
        "16": "4",
        "17": "L",
        "18": "1",
        "19": "8"
    }
    seeds_n = 20

    if not s:
        s = "/"
    s = s.lower()
    s = s + s

    res = ''
    for i in s:
        res += seeds[str(ord(i) % seeds_n)]
    return res

def a_default(url: str = '/', data: object = {}):
    url = url.lower()
    dataJson = json.dumps(data, ensure_ascii=False, separators=(',', ':')).lower()

    hash = hmac.new(
        bytes(seeds_generator(url), encoding='utf-8'),
        bytes(url + dataJson, encoding='utf-8'),
        hashlib.sha512
    ).hexdigest()
    return hash.lower()[8:28]

def r_default(url: str = '/', data: object = {}, tid: str = ''):
    url = url.lower()
    dataJson = json.dumps(data, ensure_ascii=False, separators=(',', ':')).lower()

    payload = url + 'pathString' + dataJson + tid
    key = seeds_generator(url)

    hash = hmac.new(
        bytes(key, encoding='utf-8'),
        bytes(payload, encoding='utf-8'),
        hashlib.sha512
    ).hexdigest()
    return hash.lower()

def parse(text):
    datas = json.loads(text)['Result']
    for data in datas:
        try:
            print(data)
            data_dic = {}
            data_dic['KeyNo'] = data['KeyNo']                                   # keyno
            data_dic['Name'] = data['Name']                                     # 名称
            data_dic['CreditCode'] = data['CreditCode']                         # 统一社会信用代码
            data_dic['OperName'] = data['OperName']                             # 法定代表人
            data_dic['Status'] = data['Status']                                 # 经营状况
            data_dic['StartDate'] = datetime.datetime.fromtimestamp((int(data['StartDate'])/1000)).strftime('%Y-%m-%d')     # 成立日期
            data_dic['Address'] = data['Address']                               # 地址
            data_dic['RegistCapi'] = data['RegistCapi']                         # 注册资本
            data_dic['ContactNumber'] = data['ContactNumber']                   # 联系电话
            data_dic['Email'] = data['Email']                                   # email
            try:
                data_dic['tel'] = re.findall('"t":"(.*?)"', data['TelList'])[0] # 手机号码
            except:
                data_dic['tel'] = ''
            data_dic['CityCode'] = data['Area']['CityCode']                     # 城市代码
            data_dic['City'] = data['Area']['City']                             # 城市
            data_dic['CountyCode'] = data['Area']['CountyCode']                 # 区域代码
            data_dic['County'] = data['Area']['County']                         # 区域名
            data_dic['lat'] = data['X']                                         # 纬度
            data_dic['lng'] = data['Y']                                         # 经度

            datas = pd.DataFrame(data_dic, index=[0])
            logging.info(data_dic)

            if os.path.exists('qcc.csv'):
                datas.to_csv('qcc.csv', mode='a+', index=False, header=False, encoding='gb18030')
            else:
                datas.to_csv('qcc.csv', mode='a+', index=False, header=True, encoding='gb18030')
        except Exception as e:
            print(e)
            continue

def make_request(data, pid, tid):
    url = 'https://www.qcc.com/api/search/searchMulti'
    headers = {
        'accept': 'application/json, text/plain, */*'
        ,'accept-encoding': 'gzip, deflate, br'
        ,'accept-language': 'zh-CN,zh;q=0.9'
        ,'content-length': '141'
        ,'content-type': 'application/json'
        ,'cookie': cookie
        ,'origin': 'https://www.qcc.com'
        ,'referer': 'https://www.qcc.com/web/search/advance?hasState=true'
        ,'sec-fetch-dest': 'empty'
        ,'sec-fetch-mode': 'cors'
        ,'sec-fetch-site': 'same-origin'
        ,'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        ,'x-requested-with': 'XMLHttpRequest'
    }

    headers['x-pid'] = pid

    req_url = '/api/search/searchmulti'

    key = a_default(req_url, data)
    val = r_default(req_url, data, tid)
    headers[key] = val

    res = requests.post(url=url, headers=headers, json=data).text
    parse(res)

if __name__ == '__main__':
    # 由于查询接口种类参数较为复杂，故不对接口数据作统一化处理，需要查询时通过F12进行统一接口调用
    # data = {"filter":"{\"r\":[{\"pr\":\"GD\",\"cc\":[440105]}],\"i\":[\"F\"],\"s\":[\"20\",\"10\",\"50\",\"60\",\"117\"],\"rc\":[{\"min\":\"0\",\"max\":\"500\"}],\"ct\":[\"10\"],\"c\":[\"CNY\"],\"d\":[{\"start\":\"20180112\",\"end\":\"20200112\"}]}","pageSize":20,"isAgg":"false","pageIndex":1,"isLimit":False}
    data = {"filter":"{\"i\":[\"F\"],\"r\":[{\"pr\":\"GD\",\"cc\":[440106]}],\"s\":[\"20\",\"10\",\"50\",\"60\",\"117\"],\"rc\":[{\"min\":\"0\",\"max\":\"500\"}],\"ct\":[\"10\",\"70\"],\"d\":[{\"start\":\"20180116\",\"end\":\"20200116\"}],\"c\":[\"CNY\"],\"f\":[\"VMN\"]}","pageSize":20,"isAgg":"false","isLimit":False}

    pid, tid = get_pid_tid()
    for i in range(1, 251):
        try:
            data['pageIndex'] = i
            make_request(data, pid, tid)
            time.sleep(0.3)
        except:
            break