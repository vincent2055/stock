# -*- coding: utf-8 -*-
"""通过搜索建议接口获取申万二级板块 BK 代码，再用 K 线计算多周期涨幅（降级方案，绕过被反爬的 clist）"""
import urllib.request, json, time

def get(url, ref='https://quote.eastmoney.com', retries=3, timeout=25):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'Referer': ref, 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0'})
            return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8'))
        except Exception as e:
            if i == retries - 1:
                return None
            time.sleep(1.5 + i)

SEARCH_TOKEN = 'D43BF722C8E33BDC906FB84D85E326E8'

def search_board(name):
    """搜索板块，返回精确匹配的 BK 代码（Classify=BK）"""
    import urllib.parse
    q = urllib.parse.quote(name)
    url = f'https://searchapi.eastmoney.com/api/suggest/get?input={q}&type=14&token={SEARCH_TOKEN}'
    d = get(url)
    if not d:
        return None
    data = d.get('QuotationCodeTable', {}).get('Data') or []
    # 优先精确名称匹配的板块
    for item in data:
        if item.get('Classify') == 'BK' and item.get('Name') == name:
            return item.get('Code')
    # 兜底：任意 BK 板块
    for item in data:
        if item.get('Classify') == 'BK':
            return item.get('Code')
    return None

def get_board_closes(bk):
    secid = '90.' + bk
    url = (f'https://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&klt=101&fqt=1'
           f'&beg=20260501&end=20261113&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56')
    d = get(url)
    if not d or 'data' not in d or not d['data'] or not d['data']['klines']:
        return None
    k = d['data']['klines']
    return [(x.split(',')[0], float(x.split(',')[2])) for x in k]  # [(date, close)]

def calc(closes):
    last = closes[-1][1]
    n = len(closes)
    def pct(idx):
        if idx < 0 or -idx > n:
            return None
        return round((last / closes[idx][1] - 1) * 100, 2)
    return {
        'last_date': closes[-1][0],
        'first_date': closes[0][0],
        'today': pct(-2),
        'w1': pct(-6),
        'm1': pct(-21),
        'm3': pct(-61),
        'm6': round((last / closes[0][1] - 1) * 100, 2) if n > 1 else None,
        'days': n,
    }

def main():
    sw = json.load(open('sector_data.json', encoding='utf-8'))
    names = [s['name'] for s in sw]

    out = {}
    fail_code = []
    fail_kline = []
    for i, name in enumerate(names):
        bk = search_board(name)
        if not bk:
            fail_code.append(name)
            print(f'[{i+1}/{len(names)}] {name}: 未找到板块代码')
            time.sleep(0.3)
            continue
        closes = get_board_closes(bk)
        if not closes:
            fail_kline.append(name)
            print(f'[{i+1}/{len(names)}] {name} ({bk}): K线失败')
            time.sleep(0.2)
            continue
        p = calc(closes)
        out[name] = {'bk': bk, **p}
        print(f'[{i+1}/{len(names)}] {name} ({bk}): today={p["today"]} w1={p["w1"]} m1={p["m1"]} m3={p["m3"]} m6={p["m6"]}')
        time.sleep(0.15)

    json.dump({'boards': out, 'fail_code': fail_code, 'fail_kline': fail_kline},
              open('board_data.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n成功', len(out), ' 未找到代码', len(fail_code), ' K线失败', len(fail_kline))
    print('未找到代码:', fail_code)
    print('K线失败:', fail_kline)

if __name__ == '__main__':
    main()
