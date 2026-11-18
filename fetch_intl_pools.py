# -*- coding: utf-8 -*-
"""采集国际指数(东财ulist) + 涨停/跌停/炸板池(东财push2ex)，保存 JSON"""
import urllib.request, json, time

UA = {'Referer': 'https://quote.eastmoney.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get_json(url, retries=3):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=25).read().decode('utf-8'))
        except Exception as e:
            if i == retries - 1:
                print('FAIL', url[:60], repr(e))
                return None
            time.sleep(1.0 + i)

result = {}

# 1. 国际指数
intl_url = ('http://push2.eastmoney.com/api/qt/ulist.np/get?secids=100.DJIA,100.SPX,100.NDX,100.HSI,124.HSTECH,100.HSCEI,100.N225,100.KS11'
            '&fields=f2,f3,f4,f12,f13,f14&fltt=2&invt=2&ut=fa5fd1943c7b386f172d6893dbfba10b')
d = get_json(intl_url)
intl = []
if d and 'data' in d and d['data']:
    for r in d['data']['diff']:
        intl.append({'name': r['f14'], 'price': r['f2'], 'chg': r['f3']})
result['intl'] = intl
print('国际指数:', intl)

# 2. 涨停/跌停/炸板池
def pool(url):
    d = get_json(url)
    if not d or 'data' not in d or not d['data']:
        return {'count': 0, 'list': []}
    dd = d['data']
    lst = []
    for x in (dd.get('pool') or []):
        hybk = x.get('hybk') or ''
        lst.append({'name': x.get('n'), 'code': x.get('c'), 'hybk': hybk})
    return {'count': dd.get('tc', 0), 'list': lst}

base = 'http://push2ex.eastmoney.com/getTopic'
result['zt'] = pool(base + 'ZTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=300&sort=fund:asc&date=20261116')
time.sleep(0.4)
result['dt'] = pool(base + 'DTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=300&sort=fund:asc&date=20261116')
time.sleep(0.4)
result['zb'] = pool(base + 'ZBPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=300&sort=zttj:asc&date=20261116')
print('涨停池', result['zt']['count'], '跌停池', result['dt']['count'], '炸板池', result['zb']['count'])

json.dump(result, open('intl_pools.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('已保存 intl_pools.json')
