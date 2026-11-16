# -*- coding: utf-8 -*-
"""A股复盘看盘工作台 数据采集脚本（westock 降级为 东方财富/新浪）
一次性快照，2026-11-13 周五收盘数据
"""
import urllib.request, json, time, re

UA = {'Referer': 'https://quote.eastmoney.com', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

def get(url, retries=3, timeout=25):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8'))
        except Exception as e:
            if i == retries - 1:
                return None
            time.sleep(1.0 + i)

def get_text(url, retries=3, timeout=25):
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'Referer': 'https://finance.sina.com.cn', 'User-Agent': 'Mozilla/5.0'})
            return urllib.request.urlopen(req, timeout=timeout).read().decode('utf-8', errors='ignore')
        except Exception:
            if i == retries - 1:
                return None
            time.sleep(1.0)

UT = 'bd1d9ddb04089700cf9c27f6f7426281'
EM = 'http://push2.eastmoney.com'

# ============ 1. 涨跌家数 + 涨跌分布（分页全A股） ============
def collect_breadth():
    allrows = []
    pn = 1
    total = None
    while True:
        url = (f'{EM}/api/qt/clist/get?pn={pn}&pz=100&po=1&np=1&ut={UT}&fltt=2&invt=2&fid=f3'
               f'&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f3,f12,f14')
        d = get(url)
        if not d or 'data' not in d or not d['data']:
            break
        data = d['data']
        if total is None:
            total = data.get('total', 0)
        diff = data.get('diff') or []
        if not diff:
            break
        allrows.extend(diff)
        if len(allrows) >= total:
            break
        pn += 1
        time.sleep(0.2)
    up = down = flat = 0
    buckets = {'zt': 0, 'gt7': 0, 's5_7': 0, 's2_5': 0, 's0_2': 0, 'flat': 0,
               'd0_2': 0, 'd2_5': 0, 'd5_7': 0, 'lt7': 0, 'dt': 0}
    for r in allrows:
        f3 = r['f3']
        if f3 > 9.9: buckets['zt'] += 1; up += 1
        elif f3 > 7: buckets['gt7'] += 1; up += 1
        elif f3 > 5: buckets['s5_7'] += 1; up += 1
        elif f3 > 2: buckets['s2_5'] += 1; up += 1
        elif f3 > 0: buckets['s0_2'] += 1; up += 1
        elif f3 == 0: buckets['flat'] += 1; flat += 1
        elif f3 > -2: buckets['d0_2'] += 1; down += 1
        elif f3 > -5: buckets['d2_5'] += 1; down += 1
        elif f3 > -7: buckets['d5_7'] += 1; down += 1
        elif f3 > -9.9: buckets['lt7'] += 1; down += 1
        else: buckets['dt'] += 1; down += 1
    return {'total': total, 'fetched': len(allrows), 'up': up, 'flat': flat, 'down': down, 'buckets': buckets}

# ============ 2. 涨停/跌停/炸板池 ============
def collect_pools():
    def pool(url):
        d = get(url)
        if not d or 'data' not in d or not d['data']:
            return {'count': 0, 'list': []}
        dd = d['data']
        lst = [(x['n'], x['c']) for x in (dd.get('pool') or [])]
        return {'count': dd.get('tc', 0), 'list': lst}
    base = 'http://push2ex.eastmoney.com/getTopic'
    zt = pool(f'{base}ZTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=300&sort=fund:asc&date=20261113')
    time.sleep(0.3)
    dt = pool(f'{base}DTPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=300&sort=fund:asc&date=20261113')
    time.sleep(0.3)
    zb = pool(f'{base}ZBPool?ut=7eea3edcaed734bea9cbfc24409ed989&dpt=wz.ztzt&Pageindex=0&pagesize=300&sort=zttj:asc&date=20261113')
    return {'zt': zt, 'dt': dt, 'zb': zb}

# ============ 3. 国际指数 ============
def collect_intl():
    url = (f'{EM}/api/qt/ulist.np/get?secids=100.DJIA,100.SPX,100.NDX,100.HSI,124.HSTECH,100.HSCEI,100.N225,100.KS11'
           f'&fields=f2,f3,f4,f12,f13,f14&fltt=2&invt=2&ut=fa5fd1943c7b386f172d6893dbfba10b')
    d = get(url)
    items = []
    if d and 'data' in d and d['data']:
        for r in d['data']['diff']:
            items.append({'name': r['f14'], 'price': r['f2'], 'chg': r['f3']})
    return items

# ============ 4. 板块（东财496 → 匹配申万二级124名） ============
def collect_boards(sw_names):
    boards = []
    for pn in range(1, 6):
        url = (f'{EM}/api/qt/clist/get?pn={pn}&pz=100&po=1&np=1&ut={UT}&fltt=2&invt=2&fid=f3'
               f'&fs=m:90+t:2+f:!50&fields=f2,f3,f12,f14,f109,f110,f128,f136,f140')
        d = get(url)
        if d and 'data' in d and d['data']:
            boards.extend(d['data'].get('diff') or [])
        time.sleep(0.2)
    # 名称匹配
    bmap = {}
    for b in boards:
        nm = b['f14']
        bmap.setdefault(nm, b)  # 同名取第一个（当天涨幅靠前，无所谓）
    matched = {}
    for sw in sw_names:
        b = bmap.get(sw)
        if b is None:
            # 尝试去掉Ⅱ后缀匹配
            b = bmap.get(sw.replace('Ⅱ', ''))
        if b is not None:
            matched[sw] = b
    return boards, matched

# ============ 5. 板块K线（60日/6月） ============
def collect_board_kline(bk_code):
    secid = '90.' + bk_code
    url = (f'http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&klt=101&fqt=1'
           f'&beg=20260501&end=20261113&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56')
    d = get(url)
    if not d or 'data' not in d or not d['data']:
        return None
    k = d['data']['klines'] or []
    closes = [float(x.split(',')[2]) for x in k]
    return closes

def calc_periods(closes):
    if not closes:
        return None
    n = len(closes)
    last = closes[-1]
    def pct(base_idx):
        if base_idx < 0 or base_idx >= n:
            return None
        return round((last / closes[base_idx] - 1) * 100, 2)
    w1 = pct(-6)
    m1 = pct(-21)
    m3 = pct(-61)
    m6 = round((last / closes[0] - 1) * 100, 2) if n > 0 else None
    return {'w1': w1, 'm1': m1, 'm3': m3, 'm6': m6, 'days': n, 'first_date': None}

# ============ 6. 自选股行情 + K线 ============
STOCKS = [
    ('sh513100', '纳指ETF国泰', True, 'ETF'),
    ('sh513180', '恒生科技ETF华夏', True, 'ETF'),
    ('sh600293', '三峡新材', False, '玻璃玻纤'),
    ('sz159227', '航空航天ETF华夏', True, 'ETF'),
    ('sh512070', '证券保险ETF易方达', True, 'ETF'),
    ('sz002415', '海康威视', False, '计算机设备'),
    ('sh603259', '药明康德', False, '医疗服务'),
    ('sh600276', '恒瑞医药', False, '化学制药'),
    ('sh601888', '中国中免', False, '一般零售'),
    ('sh600298', '安琪酵母', False, '调味发酵品'),
    ('sz300059', '东方财富', False, '证券'),
    ('sz002627', '三峡旅游', False, '旅游景区'),
    ('sz000001', '平安银行', False, '股份制银行'),
    ('sh688981', '中芯国际', False, '半导体'),
    ('sh600584', '长电科技', False, '半导体'),
]

def collect_stock(stock):
    code, name, is_etf, sector = stock
    secid = ('1.' if code.startswith('sh') else '0.') + code[2:]
    url = (f'{EM}/api/qt/stock/get?secid={secid}&fields=f43,f57,f58,f60,f169,f170,f50,f8,f168&invt=2&fltt=2')
    d = get(url)
    price = chg = vr = hs = None
    if d and 'data' in d and d['data']:
        dd = d['data']
        price = dd.get('f43'); chg = dd.get('f170'); vr = dd.get('f50'); hs = dd.get('f168')
    # K线30日
    url2 = (f'http://push2his.eastmoney.com/api/qt/stock/kline/get?secid={secid}&klt=101&fqt=1'
            f'&beg=20260920&end=20261113&fields1=f1,f2,f3&fields2=f51,f52,f53,f54,f55,f56')
    d2 = get(url2)
    closes = []
    if d2 and 'data' in d2 and d2['data'] and d2['data']['klines']:
        closes = [float(x.split(',')[2]) for x in d2['data']['klines']]
    return {'code': code, 'name': name, 'etf': is_etf, 'sector': sector,
            'price': price, 'chg': chg, 'vr': vr, 'hs': hs, 'closes': closes}

def main():
    result = {}

    # 申万二级名单
    sw = json.load(open('sector_data.json', encoding='utf-8'))
    sw_names = [s['name'] for s in sw]

    print('=== 采集涨跌家数 ===')
    result['breadth'] = collect_breadth()
    print('  涨', result['breadth']['up'], '平', result['breadth']['flat'], '跌', result['breadth']['down'])

    print('=== 采集涨停/跌停/炸板 ===')
    result['pools'] = collect_pools()
    print('  涨停', result['pools']['zt']['count'], '跌停', result['pools']['dt']['count'], '炸板', result['pools']['zb']['count'])

    print('=== 采集国际指数 ===')
    result['intl'] = collect_intl()
    print(' ', result['intl'])

    print('=== 采集板块 ===')
    boards, matched = collect_boards(sw_names)
    result['board_total'] = len(boards)
    result['board_matched'] = len(matched)
    print('  板块总数', len(boards), '匹配申万二级', len(matched), '/', len(sw_names))
    missing = [n for n in sw_names if n not in matched]
    print('  未匹配:', missing)

    # 板块K线（60日/6月）
    print('=== 采集板块K线(60日/6月) ===')
    board_period = {}
    for sw, b in matched.items():
        closes = collect_board_kline(b['f12'])
        if closes:
            board_period[sw] = calc_periods(closes)
        time.sleep(0.15)
    result['board_period'] = board_period

    # 保存板块合并结果
    boards_out = []
    for sw, b in matched.items():
        p = board_period.get(sw, {})
        boards_out.append({
            'name': sw, 'bk': b['f12'],
            'today': b.get('f3'), 'w1': b.get('f109'), 'm1': b.get('f110'),
            'm3': p.get('m3'), 'm6': p.get('m6'),
            'leader': b.get('f128'), 'leader_code': b.get('f140'), 'leader_chg': b.get('f136'),
        })
    result['boards'] = boards_out

    print('=== 采集自选股 ===')
    stocks = []
    for st in STOCKS:
        s = collect_stock(st)
        stocks.append(s)
        print(' ', s['name'], s['price'], s['chg'], '量比', s['vr'], 'close数', len(s['closes']))
        time.sleep(0.2)
    result['stocks'] = stocks

    json.dump(result, open('collected.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('\n已保存 collected.json')

if __name__ == '__main__':
    main()
