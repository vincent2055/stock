# -*- coding: utf-8 -*-
import urllib.request, json, time

def fetch(pn):
    url = ('http://push2.eastmoney.com/api/qt/clist/get?pn=%d&pz=100&po=1&np=1'
           '&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3'
           '&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23&fields=f2,f3,f12,f14,f100' % pn)
    req = urllib.request.Request(url, headers={'Referer': 'https://www.eastmoney.com', 'User-Agent': 'Mozilla/5.0'})
    raw = urllib.request.urlopen(req, timeout=20).read().decode('utf-8')
    return json.loads(raw).get('data', {}).get('diff', [])

allrows = []
for pn in range(49, 54):  # 第4801-5300名，跌幅最大
    try:
        rows = fetch(pn)
        allrows.extend(rows)
        time.sleep(0.3)
    except Exception as e:
        print('pn=%d 失败: %s' % (pn, e))

print('共获取', len(allrows), '只（跌幅最大区间）')

# 跌幅榜10个板块（申万二级名，需匹配 f100）
targets = ['元件','通信设备','玻璃玻纤','医疗服务','电子化学品','自动化设备','消费电子','工业金属','半导体','通用设备']

# 按行业归类，取每板块跌幅最大的个股
sector_lead = {}
for r in allrows:
    hy = r.get('f100', '')
    for t in targets:
        if hy and (hy == t or hy.startswith(t) or t.startswith(hy)):
            key = t
            f3 = r.get('f3', 0)
            if key not in sector_lead or f3 < sector_lead[key]['f3']:
                sector_lead[key] = {'code': r.get('f12'), 'name': r.get('f14'), 'chg': f3, 'hy': hy}

print('\n=== 各跌幅榜板块的领跌股(当天跌幅最大) ===')
for t in targets:
    if t in sector_lead:
        s = sector_lead[t]
        print('%-8s 领跌: %s(%s) %.2f%%' % (t, s['name'], s['code'], s['chg']))
    else:
        print('%-8s 未匹配到' % t)
