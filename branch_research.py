#coding=utf-8
import requests
import json
import re
import hmac
import time
import hashlib
import datetime
import math
import pandas as pd

# user_cookie
cookie = ''

info_table = pd.DataFrame(columns=['KeyNo', 'Name', 'OperName', 'OperKeyNo', 'StartDate', 'Status', 'PhoneNumber', 'Address', 'CreditCode', 'TaxNo', 'No', 'OrgNo', 'EconKind', 'Industry', 'Province', 'City', 'CountyDesc'])

def get_pid_tid():
    url = 'https://www.qcc.com/web/project/batchSearch'

    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
        ,'accept-encoding': 'gzip, deflate, br'
        ,'accept-language': 'zh-CN,zh;q=0.9'
        ,'cache-control': 'max-age=0'
        ,'cookie': cookie
        ,'referer': 'https://www.qcc.com/web/project/batchSearch'
        ,'sec-fetch-dest': 'document'
        ,'sec-fetch-mode': 'navigate'
        ,'sec-fetch-site': 'same-origin'
        ,'sec-fetch-user': '?1'
        ,'upgrade-insecure-requests': '1'
        ,'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
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

# 批量搜索的结果
def get_righterr_list(res):
    json_data = json.loads(res)
    slurErrList = []
    rightList = []

    if len(json_data['slurErrList']) > 0 :
        for i in json_data['slurErrList']:
            slurErrList.append(i['FWord'])
    if len(json_data['rightList']) > 0:
        for i in json_data['rightList']:
            rightList.append(i['FWord'])

    return rightList, slurErrList

def make_textResolverCompanyList(data, pid, tid):
    url = 'https://www.qcc.com/api/batch/textResolverCompanyList'

    headers = {
        'accept': 'application/json, text/plain, */*'
        ,'accept-encoding': 'gzip, deflate, br'
        ,'accept-language': 'zh-CN,zh;q=0.9'
        ,'content-length': '3870'
        ,'content-type': 'application/json'
        ,'cookie': cookie
        ,'origin': 'https://www.qcc.com'
        ,'referer': 'https://www.qcc.com/web/project/batchSearch'
        ,'sec-fetch-dest': 'empty'
        ,'sec-fetch-mode': 'cors'
        ,'sec-fetch-site': 'same-origin'
        ,'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        ,'x-requested-with': 'XMLHttpRequest'
    }

    headers['x-pid'] = pid

    req_url = '/api/batch/textResolverCompanyList'

    key = a_default(req_url, data)
    val = r_default(req_url, data, tid)
    headers[key] = val

    res = requests.post(url=url, headers=headers, json=data).text

    return res

def make_get_res(url, pid, tid):
    url = f'https://www.qcc.com/api/batch/{url}'

    headers = {
        'accept': 'application/json, text/plain, */*'
        , 'accept-encoding': 'gzip, deflate, br'
        , 'accept-language': 'zh-CN,zh;q=0.9'
        , 'cookie': cookie
        , 'referer': 'https://www.qcc.com/web/project/batchList?batchType=1'
        , 'sec-fetch-dest': 'empty'
        , 'sec-fetch-mode': 'cors'
        , 'sec-fetch-site': 'same-origin'
        ,
        'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        , 'x-requested-with': 'XMLHttpRequest'
    }

    headers['x-pid'] = pid

    req_url = f'/api/batch/{url}'

    key = a_default(req_url)
    val = r_default(req_url, tid=tid)
    headers[key] = val

    res = requests.get(url=url, headers=headers).text

    return res

def make_getBatchRedis(data, pid, tid):
    url = 'https://www.qcc.com/api/batch/getBatchRedis?batchType=0'

    headers = {
        'accept': 'application/json, text/plain, */*'
        ,'accept-encoding': 'gzip, deflate, br'
        ,'accept-language': 'zh-CN,zh;q=0.9'
        ,'cookie': cookie
        ,'referer': 'https://www.qcc.com/web/project/batchList?batchType=1'
        ,'sec-fetch-dest': 'empty'
        ,'sec-fetch-mode': 'cors'
        ,'sec-fetch-site': 'same-origin'
        ,'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        ,'x-requested-with': 'XMLHttpRequest'
    }

    headers['x-pid'] = pid

    req_url = '/api/batch/getBatchRedis?batchType=0'

    key = a_default(req_url)
    val = r_default(req_url, tid=tid)
    headers[key] = val

    res = requests.get(url=url, headers=headers).text

    return res

# 明细请求
def make_getDetailsByIds(data, pid, tid):
    url = 'https://www.qcc.com/api/batch/getDetailsByIds'

    headers = {
        'accept': 'application/json, text/plain, */*'
        ,'accept-encoding': 'gzip, deflate, br'
        ,'accept-language': 'zh-CN,zh;q=0.9'
        ,'cookie': cookie
        ,'referer': 'https://www.qcc.com/web/project/batchList?batchType=1'
        ,'sec-fetch-dest': 'empty'
        ,'sec-fetch-mode': 'cors'
        ,'sec-fetch-site': 'same-origin'
        ,'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        ,'x-requested-with': 'XMLHttpRequest'
    }

    headers['x-pid'] = pid

    req_url = '/api/batch/getDetailsByIds'

    key = a_default(req_url, data)
    val = r_default(req_url, data, tid)
    headers[key] = val

    res = requests.post(url=url, headers=headers, json=data).text

    return res

def parse(json_data):
    global info_table

    if json_data['Status'] == 200:
        print('请求成功')

    if len(json_data['Result']) > 0:
        for i in json_data['Result']:
            alist = []
            for j in info_table.columns:
                try:
                    alist.append(i[j])
                except:
                    alist.append('')
            info_table.loc[len(info_table)] = alist

# 数据规整
def comform_data(data):
    json_data = json.loads(data)
    dic_list = []
    for i in json_data['normalErrList']:
        dic = {"Name": i['Word'], "KeyNo": ""}
        dic_list.append(dic)
    for i in json_data['slurErrList']:
        dic = {"Name": i['Word'], "KeyNo": ""}
        dic_list.append(dic)
    for i in json_data['rupRightList']:
        dic = {"KeyNo": i['LinkCompany'][0]['KeyNo'], "Name": i['LinkCompany'][0]['Name'],
               "ActualName": i['LinkCompany'][0]['ActualName'], "OriginalName":i['LinkCompany'][0]['OriginalName']}
        dic_list.append(dic)
    for i in json_data['rightList']:
        dic = {"KeyNo": i['LinkCompany'][0]['KeyNo'], "Name": i['LinkCompany'][0]['Name'],
               "ActualName": i['LinkCompany'][0]['ActualName'], "OriginalName": i['LinkCompany'][0]['OriginalName']}
        dic_list.append(dic)
    dic = {"companyListStr": str(dic_list).replace("'", '"')}
    return dic

# 主请求函数
def make_request(data, pid, tid):
    url = 'https://www.qcc.com/api/batch/getCompaniesWithFreeText'

    headers = {
        'accept': 'application/json, text/plain, */*'
        ,'accept-encoding': 'gzip, deflate, br'
        ,'accept-language': 'zh-CN,zh;q=0.9'
        ,'content-length': '1016'
        ,'content-type': 'application/json'
        ,'cookie': cookie
        ,'origin': 'https://www.qcc.com'
        ,'referer': 'https://www.qcc.com/web/project/batchSearch'
        ,'sec-fetch-dest': 'empty'
        ,'sec-fetch-mode': 'cors'
        ,'sec-fetch-site': 'same-origin'
        ,'user-agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        ,'x-requested-with': 'XMLHttpRequest'
    }

    headers['x-pid'] = pid

    req_url = '/api/batch/getCompaniesWithFreeText'

    key = a_default(req_url, data)
    val = r_default(req_url, data, tid)
    headers[key] = val

    res = requests.post(url=url, headers=headers, json=data).text

    # 获取首次匹配结果
    rightList, slurErrList = get_righterr_list(res)     # 匹配正确列表和错误列表

    # 公司列表请求查询，返回状态码
    data = comform_data(res)
    res = make_textResolverCompanyList(data, pid, tid)

    # 前置请求
    res = make_get_res('getBatchYearConsumptionsData', pid, tid)
    res = make_get_res('getBatchWholeExportCountedData', pid, tid)
    res = make_get_res('getUsageCount?type=4', pid, tid)

    # 批次请求
    res = make_get_res('getBatchRedis?batchType=0', pid, tid)
    json_data = json.loads(res)

    # 明细请求，每页20条数据请求
    if len(json_data['data']) > 0:
        page = math.ceil(len(json_data['data']) / 20)
        for p in range(1, page + 1):
            data = {"batchModel":0,"batchType":"1", "page":p}
            try:
                res = make_getDetailsByIds(data, pid, tid)
                json_data = json.loads(res)
                parse(json_data)
            except Exception as e:
                print('请求错误', e)
                return 1

if __name__ == '__main__':
    filename = ''
    file = pd.read_csv(f'{filename}.csv', encoding='gb18030')

    data = {"text":''''''}
    for i in list(file['name']):
        data['text'] += str(i)
        data['text'] += '\n'

    # 获取请求headers密码参数
    pid, tid = get_pid_tid()
    print("pid:", pid, "tid:", tid)
    # 主请求
    make_request(data, pid, tid)
    info_table.to_csv(f'./{filename}_result.csv', index=False, encoding='gb18030')