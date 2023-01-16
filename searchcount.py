# author：墨雨微晴
# date：2023/01/16
# note：企查查数量查询接口，可以查询在特定的查询条件下的结果数
# note：需要填写自己的账号cookie

import requests
import json
import re
import hmac
import hashlib

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

def make_request(data, pid, tid):
    url = 'https://www.qcc.com/api/search/searchCount'
    # url = 'https://www.qcc.com/api/search/searchMulti'
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

    req_url = '/api/search/searchcount'

    print(pid)
    key = a_default(req_url, data)
    val = r_default(req_url, data, tid)
    headers[key] = val
    print(key, val)

    res = requests.post(url=url, headers=headers, json=data).text
    print(res)

if __name__ == '__main__':
    # 由于查询接口参数种类和枚举较为复杂，故不对查询接口参数作统一化处理，需要查询时通过F12进行复制调用
    data = {"count": True,
     "filter": "{\"i\":[\"F\"],\"r\":[{\"pr\":\"GD\",\"cc\":[440106]}],\"s\":[\"20\",\"10\",\"50\",\"60\",\"117\"],\"rc\":[{\"min\":\"0\",\"max\":\"500\"}],\"ct\":[\"10\",\"70\"],\"d\":[{\"start\":\"20180116\",\"end\":\"20200116\"}],\"c\":[\"CNY\"],\"f\":[\"VMN\"]}"}

    pid, tid = get_pid_tid()
    make_request(data, pid, tid)