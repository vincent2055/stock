# -*- coding: utf-8 -*-
import json, re

HTML = "trade-review.html"
h = open(HTML, encoding="utf-8").read()

# ---- 1. STOCKS（21只，从 compute 结果读） ----
stocks = json.load(open("stock_result_1117.json", encoding="utf-8"))
STOCKS = json.dumps(stocks, ensure_ascii=False, separators=(",", ": "))
h = re.sub(r'const STOCKS = \[.*?\];', 'const STOCKS = ' + STOCKS + ';', h, count=1, flags=re.S)

# ---- 2. ZB（炸板股，从 zbp.json 读） ----
zb = json.load(open("zbp.json", encoding="utf-8"))
zb_names = [s["n"] for s in zb["data"]["pool"]]
ZB = json.dumps(zb_names, ensure_ascii=False)
h = re.sub(r'const ZB = \[.*?\];', 'const ZB = ' + ZB + ';', h, count=1, flags=re.S)

# ---- 3. DIST（5段） ----
DIST = json.dumps([
    {"tag": "涨停", "n": 38, "c": "up"},
    {"tag": "上涨", "n": 1288, "c": "up"},
    {"tag": "平盘", "n": 135, "c": "flat"},
    {"tag": "下跌", "n": 4035, "c": "down"},
    {"tag": "跌停", "n": 84, "c": "down"},
], ensure_ascii=False)
h = re.sub(r'const DIST = \[.*?\];', 'const DIST = ' + DIST + ';', h, count=1, flags=re.S)

# ---- 4. INTL ----
INTL = json.dumps([
    {"market": "美股", "items": [{"name": "道琼斯", "price": "51,608.17", "chg": -1.41}, {"name": "标普500", "price": "7,416.59", "chg": -1.92}, {"name": "纳斯达克", "price": "24,509.76", "chg": -2.49}]},
    {"market": "港股", "items": [{"name": "恒生指数", "price": "23,508.17", "chg": -1.03}, {"name": "恒生科技", "price": "3,758.17", "chg": -1.14}, {"name": "国企指数", "price": "7,904.37", "chg": -0.97}]},
    {"market": "日股", "items": [{"name": "日经225", "price": "58,860.43", "chg": -1.34}]},
    {"market": "韩股", "items": [{"name": "KOSPI", "price": "4,968.48", "chg": -2.59}]},
], ensure_ascii=False)
h = re.sub(r'const INTL = \[.*?\];', 'const INTL = ' + INTL + ';', h, count=1, flags=re.S)

# ---- 5. LEADERS ----
LEADERS = {
  "w1": [{"name": "白色家电", "v": 4.84, "ld": "长虹美菱", "lc": 17.04}, {"name": "城商行Ⅱ", "v": 4.38, "ld": "齐鲁银行", "lc": 6.36}, {"name": "国有大型银行Ⅱ", "v": 4.13, "ld": "中国银行", "lc": 5.29}, {"name": "小家电", "v": 3.17, "ld": "北鼎股份", "lc": 39.00}, {"name": "渔业", "v": 2.40, "ld": "好当家", "lc": 24.43}, {"name": "农商行Ⅱ", "v": 2.40, "ld": "沪农商行", "lc": 6.83}],
  "m1": [{"name": "小家电", "v": 14.33, "ld": "九阳股份", "lc": 77.18}, {"name": "养殖业", "v": 9.91, "ld": "东瑞股份", "lc": 28.10}, {"name": "酒店餐饮", "v": 9.66, "ld": "首旅酒店", "lc": 21.72}, {"name": "饮料乳品", "v": 8.67, "ld": "新乳业", "lc": 20.55}, {"name": "白酒Ⅱ", "v": 8.37, "ld": "古井贡酒", "lc": 31.10}, {"name": "白色家电", "v": 8.23, "ld": "长虹美菱", "lc": 12.86}],
  "m3": [{"name": "国有大型银行Ⅱ", "v": 21.23, "ld": "交通银行", "lc": 26.52}, {"name": "小家电", "v": 13.83, "ld": "九阳股份", "lc": 239.29}, {"name": "养殖业", "v": 13.36, "ld": "东瑞股份", "lc": 52.10}, {"name": "股份制银行Ⅱ", "v": 12.51, "ld": "中信银行", "lc": 23.41}, {"name": "城商行Ⅱ", "v": 12.45, "ld": "北京银行", "lc": 27.47}, {"name": "数字媒体", "v": 12.19, "ld": "芒果超媒", "lc": 88.46}],
  "m6": [{"name": "国有大型银行Ⅱ", "v": 23.13, "ld": "交通银行", "lc": 34.50}, {"name": "医疗服务", "v": 17.87, "ld": "万邦医药", "lc": 74.54}, {"name": "股份制银行Ⅱ", "v": 13.31, "ld": "浦发银行", "lc": 25.25}, {"name": "城商行Ⅱ", "v": 13.21, "ld": "北京银行", "lc": 29.13}, {"name": "白色家电", "v": 9.86, "ld": "美的集团", "lc": 18.28}, {"name": "养殖业", "v": 7.20, "ld": "东瑞股份", "lc": 42.86}],
}
h = re.sub(r'const LEADERS = \{.*?\};', 'const LEADERS = ' + json.dumps(LEADERS, ensure_ascii=False) + ';', h, count=1, flags=re.S)

# ---- 6. TODAY_SECTORS ----
TODAY_SECTORS = [
  {"name": "小家电", "today": 3.94, "w1": 3.17, "m1": 14.33, "m3": 13.83, "m6": -2.90, "ld": "北鼎股份", "lc": 16.05},
  {"name": "贵金属", "today": 2.09, "w1": -10.03, "m1": -11.80, "m3": -21.12, "m6": -18.01, "ld": "山金国际", "lc": 3.40},
  {"name": "电子化学品Ⅱ", "today": 1.93, "w1": -6.30, "m1": -10.43, "m3": -36.02, "m6": -32.47, "ld": "西陇科学", "lc": 10.01},
  {"name": "黑色家电", "today": 1.51, "w1": -1.73, "m1": -5.97, "m3": -12.16, "m6": -28.14, "ld": "海信视像", "lc": 4.86},
  {"name": "酒店餐饮", "today": 1.38, "w1": -0.18, "m1": 9.66, "m3": 2.36, "m6": -8.15, "ld": "首旅酒店", "lc": 3.51},
  {"name": "渔业", "today": 1.14, "w1": 2.40, "m1": 0.80, "m3": -1.40, "m6": -7.03, "ld": "好当家", "lc": 10.00},
  {"name": "白色家电", "today": 1.08, "w1": 4.84, "m1": 8.23, "m3": 8.29, "m6": 9.86, "ld": "长虹美菱", "lc": 9.98},
  {"name": "非白酒", "today": 0.97, "w1": 0.46, "m1": -1.98, "m3": -3.31, "m6": -12.43, "ld": "重庆啤酒", "lc": 3.77},
  {"name": "调味发酵品Ⅱ", "today": 0.94, "w1": 0.58, "m1": 1.92, "m3": -5.34, "m6": -4.94, "ld": "宝立食品", "lc": 6.47},
  {"name": "农化制品", "today": 0.84, "w1": -2.89, "m1": -7.16, "m3": -18.03, "m6": -25.73, "ld": "国光股份", "lc": 9.24},
]
h = re.sub(r'const TODAY_SECTORS = \[.*?\];', 'const TODAY_SECTORS = ' + json.dumps(TODAY_SECTORS, ensure_ascii=False) + ';', h, count=1, flags=re.S)

# ---- 7. SECTOR_DOWN ----
SECTOR_DOWN = [
  {"name": "影视院线", "today": -8.59, "w1": -11.52, "m1": -0.48, "m3": 10.44, "m6": -8.74, "ld": "华策影视", "lc": -13.34},
  {"name": "电视广播Ⅱ", "today": -7.01, "w1": -5.73, "m1": -2.44, "m3": -2.86, "m6": -20.97, "ld": "流金科技", "lc": -11.78},
  {"name": "数字媒体", "today": -6.20, "w1": -14.05, "m1": -0.75, "m3": 12.19, "m6": -4.98, "ld": "凡拓数创", "lc": -13.88},
  {"name": "出版", "today": -5.12, "w1": -9.29, "m1": -4.11, "m3": 7.82, "m6": -6.35, "ld": "新华传媒", "lc": -10.00},
  {"name": "广告营销", "today": -4.99, "w1": -8.63, "m1": -1.69, "m3": -9.02, "m6": -23.36, "ld": "元隆雅图", "lc": -10.01},
  {"name": "电机Ⅱ", "today": -4.00, "w1": -11.64, "m1": -6.31, "m3": -21.51, "m6": -38.10, "ld": "华阳智能", "lc": -11.90},
  {"name": "焦炭Ⅱ", "today": -3.13, "w1": -7.86, "m1": -8.98, "m3": -8.95, "m6": -20.61, "ld": "云煤能源", "lc": -8.51},
  {"name": "航天装备Ⅱ", "today": -3.02, "w1": -15.15, "m1": -6.94, "m3": -26.95, "m6": -45.56, "ld": "航天环宇", "lc": -5.96},
  {"name": "自动化设备", "today": -2.98, "w1": -12.47, "m1": -13.04, "m3": -31.40, "m6": -40.63, "ld": "拓斯达", "lc": -12.33},
  {"name": "汽车服务", "today": -2.92, "w1": -3.83, "m1": -0.92, "m3": -2.06, "m6": -15.73, "ld": "阿尔特", "lc": -9.82},
]
h = re.sub(r'const SECTOR_DOWN = \[.*?\];', 'const SECTOR_DOWN = ' + json.dumps(SECTOR_DOWN, ensure_ascii=False) + ';', h, count=1, flags=re.S)

# ---- 8. 静态 HTML 替换 ----
# 顶栏日期
h = h.replace("2026-11-16 周一 收盘快照", "2026-11-17 周二 收盘快照")
# KPI
h = h.replace('<div class="val">20<small> /100</small></div><div class="desc down">弱势 · 冰点普跌</div>',
              '<div class="val">5<small> /100</small></div><div class="desc down">冰点 · 跌停潮</div>')
h = h.replace('<div class="val" style="font-size:20px">冰点</div><div class="desc">跌停潮 · 科技崩盘</div>',
              '<div class="val" style="font-size:20px">冰点</div><div class="desc">跌停潮 · 恐慌出清</div>')
h = h.replace('<div class="val"><span class="up">33</span><span style="color:var(--muted)"> / </span><span class="down">68</span></div><div class="desc">炸板 16 · 封板率 67.3%</div>',
              '<div class="val"><span class="up">38</span><span style="color:var(--muted)"> / </span><span class="down">84</span></div><div class="desc">炸板 20 · 封板率 65.5%</div>')
h = h.replace('<div class="val">1.48<small> 万亿</small></div><div class="desc down">缩量 · 冰点</div>',
              '<div class="val">1.46<small> 万亿</small></div><div class="desc down">缩量 · 冰点</div>')

# 指数概览
h = h.replace('<span class="hint">2026-11-16 收盘</span>', '<span class="hint">2026-11-17 收盘</span>')
h = h.replace('<div class="pr">3602.57</div><div class="chg down">-0.87%</div>', '<div class="pr">3584.58</div><div class="chg down">-0.50%</div>')
h = h.replace('<div class="pr">10690.78</div><div class="chg down">-2.53%</div>', '<div class="pr">10638.52</div><div class="chg down">-0.49%</div>')
h = h.replace('<div class="pr">2320.02</div><div class="chg down">-4.37%</div>', '<div class="pr">2292.20</div><div class="chg down">-1.20%</div>')
h = h.replace('<div class="pr">1213.68</div><div class="chg down">-5.16%</div>', '<div class="pr">1221.19</div><div class="chg up">+0.62%</div>')
h = h.replace('<div class="pr">836.57</div><div class="chg down">-4.54%</div>', '<div class="pr">841.49</div><div class="chg up">+0.59%</div>')

# 涨跌家数
h = h.replace('<b>77.9%</b><span>下跌占比</span>', '<b>73.8%</b><span>下跌占比</span>')
h = h.replace('上涨<b class="up">1136</b>', '上涨<b class="up">1326</b>')
h = h.replace('平盘<b>99</b>', '平盘<b>135</b>')
h = h.replace('下跌<b class="down">4344</b>', '下跌<b class="down">4119</b>')
h = h.replace('上涨占比仅 <b>20.4%</b>，跌停 <b class="down">68 家</b> 远超涨停 33 家，赚钱效应极弱。资金从元件、通信设备、半导体等科技成长方向大幅撤离，涌入银行、家电、煤炭、调味品等防御方向，属典型<b>冰点普跌日</b>。',
              '上涨占比 <b>23.8%</b>，跌停 <b class="down">84 家</b> 仍远超涨停 38 家。传媒链（数字媒体、影视院线、出版、广告营销）补跌，资金继续抱团银行、家电、调味品等防御方向，半导体（中芯国际 <span class="up">+6.59%</span>）逆势走强，属<b>冰点分化日</b>。')

# 国际指数 note
h = h.replace('日经 <b class="down">-2.42%</b>、KOSPI <b class="down">-3.59%</b> 领跌，美股纳指 <b class="down">-0.91%</b> 走弱，港股恒生 <span class="up">+0.43%</span> 微涨。外盘整体偏弱，对 A 股风险偏好形成压制。',
              '全球风险偏好信号：美股三大指数齐跌（道指 <b class="down">-1.41%</b>、标普 <b class="down">-1.92%</b>、纳指 <b class="down">-2.49%</b>），日韩领跌（KOSPI <b class="down">-2.59%</b>），港股恒生 <b class="down">-1.03%</b>。外盘普跌，对 A 股风险偏好形成压制。')

# 国际指数 hint 日期
h = h.replace('美股 / 港股 / 日股 / 韩股 · 2026-11-16', '美股 / 港股 / 日股 / 韩股 · 2026-11-17')

# 市场环境评分
h = h.replace('stroke-dashoffset="191.2"', 'stroke-dashoffset="227.1"')
h = h.replace('<div class="num" style="font-size:22px">20</div>', '<div class="num" style="font-size:22px">5</div>')
h = h.replace('弱势市：跌停潮、情绪冰点、封板率偏低，宜<b>轻仓防守</b>（≤2成），规避破位加速下跌的科技成长股，等待放量企稳信号。',
              '冰点市：跌停潮延续、情绪恐慌、封板率偏低，宜<b>轻仓防守</b>（≤2成），规避破位补跌的传媒/成长股，等待跌停家数收敛与放量企稳信号。')
h = h.replace('<div class="sb-row"><span class="sl">涨停/跌停比 0.49（33/68）</span><span class="sv">0</span></div><div class="sb-bar"><div class="fill" style="width:50%;background:var(--muted)"></div></div>',
              '<div class="sb-row"><span class="sl">涨停/跌停比 0.45（38/84）</span><span class="sv down">-20</span></div><div class="sb-bar"><div class="fill" style="width:45%;background:var(--down)"></div></div>')
h = h.replace('<div class="sb-row"><span class="sl">上涨占比 20.4%（普跌）</span><span class="sv down">-20</span></div><div class="sb-bar"><div class="fill" style="width:20.4%;background:var(--down)"></div></div>',
              '<div class="sb-row"><span class="sl">上涨占比 23.8%（普跌）</span><span class="sv down">-15</span></div><div class="sb-bar"><div class="fill" style="width:23.8%;background:var(--down)"></div></div>')
h = h.replace('两市成交 1.48万亿（缩量）', '两市成交 1.46万亿（缩量）')
h = h.replace('封板率 67.3%（炸板 16 家）', '封板率 65.5%（炸板 20 家）')
h = h.replace('<div class="fill" style="width:67.3%;background:var(--down)"></div>', '<div class="fill" style="width:65.5%;background:var(--down)"></div>')

# 涨停封板与炸板 stats
h = h.replace('<div class="zb-stat"><div class="zlabel">涨停封板</div><div class="zval up">33</div></div>', '<div class="zb-stat"><div class="zlabel">涨停封板</div><div class="zval up">38</div></div>')
h = h.replace('<div class="zb-stat"><div class="zlabel">炸板家数</div><div class="zval" style="color:var(--warn)">16</div></div>', '<div class="zb-stat"><div class="zlabel">炸板家数</div><div class="zval" style="color:var(--warn)">20</div></div>')
h = h.replace('<div class="zb-stat"><div class="zlabel">封板率</div><div class="zval">67.3%</div></div>', '<div class="zb-stat"><div class="zlabel">封板率</div><div class="zval">65.5%</div></div>')
h = h.replace('<div class="zb-stat"><div class="zlabel">炸板率</div><div class="zval" style="color:var(--warn)">32.7%</div></div>', '<div class="zb-stat"><div class="zlabel">炸板率</div><div class="zval" style="color:var(--warn)">34.5%</div></div>')
h = h.replace('炸板率偏高（近三成涨停板未能封住），说明做多情绪不稳固、承接力度弱，与「冰点期」判断一致。', '炸板率偏高（逾三成涨停板未能封住），做多情绪不稳固、承接力度弱，与「冰点期」判断一致。')

# 情绪周期
h = h.replace('涨停跌停比 0.49', '涨停跌停比 0.45')
h = h.replace('涨停 <b class="up">33 家</b> 明显少于跌停 <b class="down">68 家</b>（跌停潮），叠加 <b>约八成个股下跌</b> 的普跌结构与 <b>近四成炸板</b>，已进入<b>冰点期</b>：涨停多来自影视院线、电视广播等题材与银行、家电、煤炭等防御方向，科技成长主线全面崩盘，赚钱效应极差，需警惕「跌停潮后的惯性下杀」。',
              '涨停 <b class="up">38 家</b> 仍明显少于跌停 <b class="down">84 家</b>（跌停潮延续），叠加 <b>约七成个股下跌</b> 的普跌与 <b>逾三成炸板</b>，处于<b>冰点期</b>：涨停多来自小家电、电子化学品、渔业等防御/题材方向，传媒链（数字媒体、影视院线、出版、广告营销）补跌领跌，赚钱效应差，需警惕「跌停潮后的惯性下杀」。')
h = h.replace('当前位置：<b>冰点</b>（跌停潮 · 科技崩盘 · 防御抱团）', '当前位置：<b>冰点</b>（跌停潮 · 传媒补跌 · 防御抱团）')

# footer 日期
h = h.replace('行情为 2026-11-16 收盘一次性快照', '行情为 2026-11-17 收盘一次性快照')

# 明日计划
h = h.replace('<b>冰点普跌日，严控仓位（≤2成）。</b>规避破位加速下跌的科技成长股（元件/通信设备/半导体），防御方向（银行/红利/家电）可少量持有；重点盯上证 3600 整数关（今日收 3602.57，濒临跌破），未见放量企稳前不抄底。',
              '<b>冰点分化日，严控仓位（≤2成）。</b>规避破位补跌的传媒链（数字媒体/影视院线/出版/广告营销），防御方向（银行/家电/调味品）可少量持有；半导体（中芯国际）逆势走强可关注但勿追高；上证已失守 3600（收 3584.58），未见跌停收敛 + 放量企稳前不抄底。')
h = h.replace('<div class="scen"><div class="st st-opt">乐观</div><div class="tx">超跌反抽：上证守住 3600 并放量反包，科技股（半导体/元件）技术性修复，可小仓位博弈超跌反弹龙头。</div></div>',
              '<div class="scen"><div class="st st-opt">乐观</div><div class="tx">超跌反抽：跌停家数骤减、上证放量反包 3600，传媒股技术性修复、半导体（中芯国际）延续强势，可小仓位博弈超跌反弹龙头。</div></div>')
h = h.replace('<div class="scen"><div class="st st-mid">中性</div><div class="tx">缩量阴跌分化：防御板块继续占优，科技弱势整理，观望为主，不做左侧。</div></div>',
              '<div class="scen"><div class="st st-mid">中性</div><div class="tx">缩量阴跌分化：银行/家电防御继续占优，传媒股弱势整理，半导体高位震荡，观望为主，不做左侧。</div></div>')
h = h.replace('<div class="scen"><div class="st st-pes">悲观</div><div class="tx">破位下杀：跌破 3600 且放量，跌停潮延续，情绪冰点加深，D级持仓加速下探，空仓等拐点。</div></div>',
              '<div class="scen"><div class="st st-pes">悲观</div><div class="tx">破位下杀：跌停潮延续、跌破 3565 前低且放量，情绪冰点加深，D级持仓加速下探，空仓等拐点。</div></div>')

# 主线研判 renderInsight
h = h.replace('document.getElementById("sectorInsight").innerHTML =\n    `短线（1周）主线在银行',
              'document.getElementById("sectorInsight").innerHTML =\n    `短线（1周）主线在银行')
old_insight = '''`短线（1周）主线在银行（城商行 <span class="up">+4.02%</span>、国有大行 <span class="up">+3.43%</span>）、影视院线、电视广播与厨卫电器，防御 + 传媒属性突出，但元件 <b class="down">-8.71%</b>、通信设备 <b class="down">-8.67%</b>、半导体 <b class="down">-6.02%</b> 当天崩盘，成长方向全面破位；<br>` +
    `中期（1月/3月）强势主线是<b>数字媒体、影视院线、养殖业、小家电</b>，银行（国有大行）3月 <span class="up">+21.11%</span> / 6月 <span class="up">+22.83%</span> 持续走强，防御 + 红利属性突出；<br>` +
    `当天仅银行/家电/煤炭/调味品逆势上涨，属防御抱团；元件、通信设备、半导体、航天装备等科技成长领跌，且在 1月/3月 维度持续大幅走弱，反弹乏力，规避为主。`;'''
new_insight = '''`短线（1周）主线在银行（城商行 <span class="up">+4.38%</span>、国有大行 <span class="up">+4.13%</span>）、白色家电、小家电与渔业，防御属性突出，但影视院线 <b class="down">-8.59%</b>、数字媒体 <b class="down">-6.20%</b>、出版 <b class="down">-5.12%</b> 当天补跌，传媒链全面走弱；<br>` +
    `中期（1月/3月）强势主线是<b>小家电、养殖业、酒店餐饮、白酒</b>，银行（国有大行）3月 <span class="up">+21.23%</span> / 6月 <span class="up">+23.13%</span> 持续走强，防御 + 红利属性突出；<br>` +
    `当天仅小家电/贵金属/电子化学品/家电逆势上涨，属防御抱团；影视院线、电视广播、数字媒体、出版、广告营销等传媒领跌，且广告营销、电机、航天装备在 3月/6月 维度持续大幅走弱，反弹乏力，规避为主。`;'''
h = h.replace(old_insight, new_insight)

open(HTML, "w", encoding="utf-8").write(h)
print("HTML 更新完成")

# 校验 JS
import subprocess
r = subprocess.run(["node", "-e", "const fs=require('fs');const h=fs.readFileSync('trade-review.html','utf8');const m=h.match(/<script>([\\s\\S]*?)<\\/script>/);try{new Function(m[1]);console.log('JS OK')}catch(e){console.log('JS ERROR:',e.message)}"], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
