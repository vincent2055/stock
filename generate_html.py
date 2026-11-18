# -*- coding: utf-8 -*-
"""读取 final_data.json，生成自包含 trade-review.html"""
import json, os

BASE = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(BASE, "final_data.json"), encoding='utf-8'))

LEADERS = data['leaders']; TODAY = data['today_sectors']; DOWN = data['sector_down']
INTL = data['intl']; DIST = data['dist']; ZB = data['zb']; STOCKS = data['stocks']
B = data['breadth']; P = data['pools']; SCORE = data['market_score']

up = B['up']; down = B['down']; flat = B['flat']; total = B['total']; up_ratio = B['up_ratio']
zt = P['zt']; dt = P['dt']; zb = P['zb']; fr = P['feng_rate']
date_label = data.get('date_label', '2026-11-16 周一 收盘快照')
amount = data.get('amount', '1.48')
zt_dt_ratio = data.get('zt_dt_ratio', round(zt/dt, 2) if dt else 0)

def fmt(v):
    if v is None:
        return None
    v = round(v, 2)
    return ("+" + str(v)) if v > 0 else str(v)

def fcl(v):
    if v is None:
        return '<span style="color:var(--muted)">—</span>'
    v = round(v, 2)
    return f'<span class="{"up" if v>0 else "down" if v<0 else ""}">{fmt(v)}%</span>'

def fclv(v):
    if v is None:
        return '<span style="color:var(--muted)">—</span>'
    v = round(v, 2)
    return f'<span class="{"up" if v>0 else "down" if v<0 else ""}">{fmt(v)}%</span>'

# 指数
idx = data.get("index", [])
idx_html = "".join(
    f'<div class="idx-row"><div class="nm">{n}<small>{c}</small></div><div><div class="pr">{p}</div><div class="chg {"up" if chg>0 else "down"}">{fmt(chg)}%</div></div></div>'
    for n, c, p, chg in idx
)

# 国际指数
intl_html = "".join(
    f'<div class="intl-group"><div class="gh">{g["market"]}</div>' +
    "".join(f'<div class="ir"><span>{i["name"]}</span><span class="iv"><span class="ip">{i["price"]}</span><span class="{"up" if i["chg"]>0 else "down" if i["chg"]<0 else ""}">{fmt(i["chg"])}%</span></span></div>' for i in g["items"]) +
    '</div>'
    for g in INTL
)

# 涨跌分布（sqrt 缩放，避免小数字不可见）
maxn = max((d['n'] ** 0.5 for d in DIST), default=1)
dist_html = "".join(
    f'<div class="dist-row"><div class="tag">{d["tag"]}</div><div class="bar-wrap"><div class="bar" style="background:{"var(--up)" if d["c"]=="up" else "var(--down)" if d["c"]=="down" else "var(--muted)"};width:{max(3, (d["n"] ** 0.5 / maxn) * 100):.1f}%"></div></div><div class="cnt">{d["n"]}</div></div>'
    for d in DIST
)

# 炸板
zb_html = "".join(f'<span class="zb-chip">{z}</span>' for z in ZB)

# 涨停封板率
fr_down = round(100 - fr, 1)

# 情绪周期（基于数据）
emotion_label = "退潮"
emotion_desc = "普跌 · 防御切换"
# 涨停/跌停比
zt_dt_ratio = round(zt / dt, 2) if dt else 0

HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<title>复盘看盘工作台</title>
<style>
:root{
  --bg:#f2f4f7; --card:#ffffff; --text:#1a2233; --muted:#6b7280; --border:#e6e8ee;
  --accent:#2f6bed; --accent-bg:#eaf1fe;
  --up:#e02828; --up-bg:#fdecec;
  --down:#0a9d5c; --down-bg:#e6f6ef;
  --warn:#e8a33d; --warn-bg:#fdf3e3;
  --radius:14px;
}
*{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
html{font-size:16px}
body{font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei","Segoe UI",sans-serif;background:var(--bg);color:var(--text);line-height:1.5;padding-bottom:80px}
header.topbar{position:sticky;top:0;z-index:50;background:var(--card);border-bottom:1px solid var(--border);padding:10px 16px;display:flex;align-items:center;justify-content:space-between;gap:12px}
.brand{display:flex;flex-direction:column;min-width:0}
.brand h1{font-size:16px;font-weight:600;white-space:nowrap}
.brand .sub{font-size:12px;color:var(--muted);white-space:nowrap}
.badge{display:inline-block;padding:2px 10px;border-radius:20px;font-size:12px;font-weight:500}
.badge.real{background:var(--accent-bg);color:var(--accent)}
.badge.snapshot{background:var(--warn-bg);color:var(--warn)}
nav.tabs{position:sticky;top:58px;z-index:49;background:var(--bg);display:flex;gap:6px;padding:8px 16px;overflow-x:auto;scrollbar-width:none}
nav.tabs::-webkit-scrollbar{display:none}
nav.tabs button{flex:0 0 auto;height:40px;padding:0 16px;border-radius:20px;border:1px solid var(--border);background:var(--card);color:var(--muted);font-size:14px;font-weight:500;cursor:pointer;white-space:nowrap}
nav.tabs button.active{background:var(--text);color:#fff;border-color:var(--text)}
main{max-width:1080px;margin:0 auto;padding:12px 16px}
.panel{display:none}
.panel.active{display:block}
.card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:14px;margin-bottom:12px}
.card h2{font-size:15px;font-weight:600;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between}
.card h2 .hint{font-size:11px;color:var(--muted);font-weight:400}
.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}
.kpi{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:12px 14px}
.kpi .label{font-size:12px;color:var(--muted)}
.kpi .val{font-size:24px;font-weight:700;margin-top:2px;letter-spacing:-.5px}
.kpi .val small{font-size:12px;font-weight:500}
.kpi .desc{font-size:11px;margin-top:2px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid2 .card{margin-bottom:0}
.idx-row{display:flex;align-items:center;justify-content:space-between;padding:7px 0;border-bottom:1px solid var(--border)}
.idx-row:last-child{border-bottom:none}
.idx-row .nm{font-size:14px;font-weight:500}
.idx-row .nm small{color:var(--muted);font-weight:400;margin-left:4px}
.idx-row .pr{font-size:14px;font-weight:600;text-align:right}
.idx-row .chg{font-size:12px;font-weight:500;text-align:right}
.up{color:var(--up)} .down{color:var(--down)}
.up-bg{background:var(--up-bg)} .down-bg{background:var(--down-bg)}
.breadth-box{display:flex;align-items:center;gap:16px}
.pie{position:relative;width:96px;height:96px;border-radius:50%;flex-shrink:0;background:conic-gradient(var(--down) 0 __PIE_DOWN__%, var(--muted) __PIE_DOWN__% __PIE_FLAT__%, var(--up) __PIE_FLAT__% 100%)}
.pie::after{content:'';position:absolute;inset:24%;background:var(--card);border-radius:50%}
.pie .center{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:1}
.pie .center b{font-size:16px;font-weight:700}
.pie .center span{font-size:10px;color:var(--muted)}
.breadth-nums{flex:1;display:flex;flex-direction:column;gap:6px}
.bn-row{display:flex;align-items:center;gap:8px;font-size:13px}
.bn-dot{width:9px;height:9px;border-radius:50%;flex-shrink:0}
.bn-row b{margin-left:auto}
.dist-row{display:flex;align-items:center;gap:8px;margin-bottom:8px}
.dist-row .tag{width:46px;font-size:11px;color:var(--muted);text-align:right;flex-shrink:0}
.dist-row .bar-wrap{flex:1;height:16px;background:var(--bg);border-radius:4px;overflow:hidden}
.dist-row .bar{height:100%;border-radius:4px;min-width:2px}
.dist-row .cnt{width:48px;font-size:11px;text-align:right;flex-shrink:0;color:var(--muted)}
table{width:100%;border-collapse:collapse;font-size:13px}
th{font-size:11px;color:var(--muted);font-weight:500;text-align:right;padding:7px 6px;border-bottom:1px solid var(--border);white-space:nowrap}
td{padding:9px 6px;border-bottom:1px solid var(--border);text-align:right;white-space:nowrap}
th:first-child,td:first-child{text-align:left}
td .nm{font-weight:500}
td .code{font-size:11px;color:var(--muted)}
.pos-tag{display:inline-block;padding:2px 7px;border-radius:5px;font-size:11px;white-space:nowrap}
.pos-strong{background:var(--up-bg);color:var(--up)}
.pos-mid{background:var(--warn-bg);color:var(--warn)}
.pos-weak{background:var(--down-bg);color:var(--down)}
.grade{display:inline-flex;align-items:center;justify-content:center;width:24px;height:24px;border-radius:50%;font-weight:700;font-size:12px}
.g-A{background:var(--up-bg);color:var(--up)}
.g-B{background:var(--accent-bg);color:var(--accent)}
.g-C{background:var(--warn-bg);color:var(--warn)}
.g-D{background:var(--down-bg);color:var(--down)}
.score-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.score-card{background:var(--card);border:1px solid var(--border);border-radius:var(--radius);padding:12px}
.score-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.score-top .nm{font-size:14px;font-weight:600}
.ring{position:relative;width:50px;height:50px}
.ring svg{transform:rotate(-90deg)}
.ring .num{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700}
.dim-row{display:flex;align-items:center;gap:7px;margin-bottom:5px}
.dim-row .dn{width:34px;font-size:11px;color:var(--muted);flex-shrink:0}
.dim-row .db{flex:1;height:6px;border-radius:3px;background:var(--bg);overflow:hidden}
.dim-row .df{height:100%;border-radius:3px;background:var(--accent)}
.dim-row .dv{width:20px;font-size:11px;text-align:right;color:var(--muted)}
.plan-box{background:var(--accent-bg);border-radius:10px;padding:12px;font-size:13px;margin-bottom:10px;line-height:1.6}
.scen{display:flex;gap:10px;padding:9px 0;border-bottom:1px solid var(--border)}
.scen:last-child{border-bottom:none}
.scen .st{flex-shrink:0;width:52px;height:24px;border-radius:7px;font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center}
.st-opt{background:var(--up-bg);color:var(--up)}
.st-mid{background:var(--warn-bg);color:var(--warn)}
.st-pes{background:var(--down-bg);color:var(--down)}
.scen .tx{font-size:13px}
.score-breakdown{display:flex;flex-direction:column;gap:8px}
.sb-row{display:flex;align-items:center;justify-content:space-between;font-size:13px}
.sb-row .sl{color:var(--muted)}
.sb-row .sv{font-weight:600}
.sb-bar{height:6px;border-radius:3px;background:var(--bg);margin-top:4px;overflow:hidden}
.sb-bar .fill{height:100%;border-radius:3px}
.zb-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}
.zb-stat{background:var(--bg);border-radius:10px;padding:10px;text-align:center}
.zb-stat .zlabel{font-size:11px;color:var(--muted)}
.zb-stat .zval{font-size:20px;font-weight:700;margin-top:2px}
.zb-list{display:flex;flex-wrap:wrap;gap:6px}
.zb-chip{background:var(--bg);border-radius:6px;padding:3px 8px;font-size:12px}
.intl-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.intl-group{background:var(--bg);border-radius:10px;padding:10px 12px}
.intl-group .gh{font-size:11px;color:var(--muted);font-weight:500;margin-bottom:6px}
.intl-group .ir{display:flex;align-items:center;justify-content:space-between;padding:3px 0;font-size:13px}
.intl-group .ir .iv{display:flex;align-items:center;gap:7px}
.intl-group .ir .ip{font-weight:600}
.intl-note{margin-top:10px;font-size:12px;color:var(--muted)}
.leader-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.leader-col .lc-h{font-size:12px;color:var(--muted);font-weight:500;margin-bottom:6px;padding-bottom:6px;border-bottom:1px solid var(--border)}
.lc-item{padding:7px 0;border-bottom:1px solid var(--border)}
.lc-item:last-child{border-bottom:none}
.lc-main{display:flex;align-items:center;justify-content:space-between;font-size:13px}
.lc-name{font-weight:500}
.lc-ld{font-size:11px;color:var(--muted);margin-top:2px}
.lc-ld b{font-weight:500}
footer.disclaimer{max-width:1080px;margin:0 auto;padding:0 16px 16px;font-size:11px;color:var(--muted);text-align:center;line-height:1.7}
@media (max-width:760px){
  .kpi-grid{grid-template-columns:repeat(2,1fr)}
  .grid2{grid-template-columns:1fr}
  .score-grid{grid-template-columns:repeat(auto-fill,minmax(160px,1fr))}
  .intl-grid{grid-template-columns:repeat(2,1fr)}
  .leader-grid{grid-template-columns:repeat(2,1fr)}
  .zb-stats{grid-template-columns:repeat(2,1fr)}
}
</style>
</head>
<body>
<header class="topbar">
  <div class="brand">
    <h1>复盘看盘工作台</h1>
    <div class="sub"><span class="badge real">腾讯自选股/东财/新浪 · 真实数据</span> 2026-11-16 周一 收盘快照</div>
  </div>
  <div class="top-actions">
    <span class="badge snapshot">复盘专用 · 一次快照 · 不实时刷新</span>
  </div>
</header>

<nav class="tabs" id="tabs">
  <button class="active" data-tab="overview" onclick="switchTab('overview')">总览</button>
  <button data-tab="emotion" onclick="switchTab('emotion')">情绪</button>
  <button data-tab="sector" onclick="switchTab('sector')">板块</button>
  <button data-tab="stock" onclick="switchTab('stock')">个股</button>
  <button data-tab="score" onclick="switchTab('score')">评分</button>
  <button data-tab="review" onclick="switchTab('review')">复盘</button>
</nav>

<main>
  <section class="panel active" id="panel-overview">
    <div class="kpi-grid">
      <div class="kpi"><div class="label">市场环境评分</div><div class="val">__SCORE__<small> /100</small></div><div class="desc down">弱势 · 冰点普跌</div></div>
      <div class="kpi"><div class="label">情绪周期</div><div class="val" style="font-size:20px">冰点</div><div class="desc">跌停潮 · 科技崩盘</div></div>
      <div class="kpi"><div class="label">涨停 / 跌停</div><div class="val"><span class="up">__ZT__</span><span style="color:var(--muted)"> / </span><span class="down">__DT__</span></div><div class="desc">炸板 __ZBCNT__ · 封板率 __FR__%</div></div>
      <div class="kpi"><div class="label">两市成交</div><div class="val">1.48<small> 万亿</small></div><div class="desc down">缩量 · 冰点</div></div>
    </div>

    <div class="grid2">
      <div class="card">
        <h2>指数概览 <span class="hint">2026-11-16 收盘</span></h2>
        __IDX__
      </div>
      <div class="card">
        <h2>涨跌家数 <span class="hint">全市场 __TOTAL__ 家</span></h2>
        <div class="breadth-box">
          <div class="pie"><div class="center"><b>__DOWN_PCT__%</b><span>下跌占比</span></div></div>
          <div class="breadth-nums">
            <div class="bn-row"><span class="bn-dot" style="background:var(--up)"></span>上涨<b class="up">__UP__</b></div>
            <div class="bn-row"><span class="bn-dot" style="background:var(--muted)"></span>平盘<b>__FLAT__</b></div>
            <div class="bn-row"><span class="bn-dot" style="background:var(--down)"></span>下跌<b class="down">__DOWN__</b></div>
          </div>
        </div>
        <div class="plan-box" style="margin-top:10px;margin-bottom:0">
          上涨占比仅 <b>__UP_RATIO__%</b>，跌停 <b class="down">__DT__ 家</b> 远超涨停 __ZT__ 家，赚钱效应极弱。资金从元件、通信设备、半导体等科技成长方向大幅撤离，涌入银行、家电、煤炭、调味品等防御方向，属典型<b>冰点普跌日</b>。
        </div>
      </div>
    </div>
    <div class="card">
      <h2>国际指数 <span class="hint">美股 / 港股 / 日股 / 韩股 · 2026-11-16</span></h2>
      <div class="intl-grid" id="intlGrid"></div>
      <div class="intl-note">
        全球风险偏好信号：日经 <b class="down">-2.42%</b>、KOSPI <b class="down">-3.59%</b> 领跌，美股纳指 <b class="down">-0.91%</b> 走弱，港股恒生 <span class="up">+0.43%</span> 微涨。外盘整体偏弱，对 A 股风险偏好形成压制。
      </div>
    </div>
  </section>

  <section class="panel" id="panel-emotion">
    <div class="card">
      <h2>市场环境评分 <span class="hint">满分 100 · 分析判断</span></h2>
      <div style="display:flex;gap:16px;align-items:center;margin-bottom:12px">
        <div class="ring" style="width:88px;height:88px">
          <svg width="88" height="88"><circle cx="44" cy="44" r="38" stroke="var(--bg)" stroke-width="10" fill="none"/><circle cx="44" cy="44" r="38" stroke="var(--down)" stroke-width="10" fill="none" stroke-linecap="round" stroke-dasharray="239" stroke-dashoffset="__SCORE_OFFSET__"/></svg>
          <div class="num" style="font-size:22px">__SCORE__</div>
        </div>
        <div style="font-size:13px;color:var(--muted)">弱势市：跌停潮、情绪冰点、封板率偏低，宜<b>轻仓防守</b>（≤2成），规避破位加速下跌的科技成长股，等待放量企稳信号。</div>
      </div>
      <div class="score-breakdown">
        <div><div class="sb-row"><span class="sl">基础分</span><span class="sv">50</span></div></div>
        <div><div class="sb-row"><span class="sl">涨停/跌停比 __ZTR__（__ZT__/__DT__）</span><span class="sv">0</span></div><div class="sb-bar"><div class="fill" style="width:50%;background:var(--muted)"></div></div></div>
        <div><div class="sb-row"><span class="sl">上涨占比 __UP_RATIO__%（普跌）</span><span class="sv down">-20</span></div><div class="sb-bar"><div class="fill" style="width:__UP_RATIO__%;background:var(--down)"></div></div></div>
        <div><div class="sb-row"><span class="sl">两市成交 1.48万亿（缩量）</span><span class="sv down">-5</span></div><div class="sb-bar"><div class="fill" style="width:40%;background:var(--down)"></div></div></div>
        <div><div class="sb-row"><span class="sl">封板率 __FR__%（炸板 __ZBCNT__ 家）</span><span class="sv down">-5</span></div><div class="sb-bar"><div class="fill" style="width:__FR__%;background:var(--down)"></div></div></div>
      </div>
    </div>

    <div class="card">
      <h2>涨停封板与炸板 <span class="hint">真实数据</span></h2>
      <div class="zb-stats">
        <div class="zb-stat"><div class="zlabel">涨停封板</div><div class="zval up">__ZT__</div></div>
        <div class="zb-stat"><div class="zlabel">炸板家数</div><div class="zval" style="color:var(--warn)">__ZBCNT__</div></div>
        <div class="zb-stat"><div class="zlabel">封板率</div><div class="zval">__FR__%</div></div>
        <div class="zb-stat"><div class="zlabel">炸板率</div><div class="zval" style="color:var(--warn)">__FRDOWN__%</div></div>
      </div>
      <div class="zb-list" id="zbList"></div>
      <div class="intl-note" style="margin-top:10px">炸板率偏高（近三成涨停板未能封住），说明做多情绪不稳固、承接力度弱，与「冰点期」判断一致。</div>
    </div>

    <div class="card">
      <h2>情绪周期 <span class="hint">涨停跌停比 __ZTR__</span></h2>
      <div class="plan-box">
        涨停 <b class="up">__ZT__ 家</b> 明显少于跌停 <b class="down">__DT__ 家</b>（跌停潮），叠加 <b>约八成个股下跌</b> 的普跌结构与 <b>近四成炸板</b>，已进入<b>冰点期</b>：涨停多来自影视院线、电视广播等题材与银行、家电、煤炭等防御方向，科技成长主线全面崩盘，赚钱效应极差，需警惕「跌停潮后的惯性下杀」。
      </div>
      <div style="font-size:13px;color:var(--muted);line-height:1.8">
        情绪周期五阶段：<b style="color:var(--up)">高潮</b> → <b>发酵</b> → <b>分歧</b> → <b>退潮</b> → <b style="color:var(--down)">冰点</b><br>
        当前位置：<b>冰点</b>（跌停潮 · 科技崩盘 · 防御抱团）
      </div>
    </div>

    <div class="card">
      <h2>涨跌分布 <span class="hint">沪深A股 · 涨/平/跌 + 涨停/跌停 · 精确统计</span></h2>
      <div id="distChart">__DISTHTML__</div>
    </div>
  </section>

  <section class="panel" id="panel-sector">
    <div class="card">
      <h2>龙头板块 · 多时间维度 <span class="hint">龙头股为对应周期涨幅最大个股 · 精确数据</span></h2>
      <div class="leader-grid" id="leaderGrid"></div>
    </div>
    <div class="card" style="overflow-x:auto">
      <h2>当天热点板块 · 多周期表现 <span class="hint">真实数据</span></h2>
      <table id="sectorTable">
        <thead><tr><th>板块</th><th style="text-align:left">龙头股</th><th>当天</th><th>1周</th><th>1月</th><th>3月</th><th>6月</th></tr></thead>
        <tbody id="sectorTbody"></tbody>
      </table>
    </div>
    <div class="card" style="overflow-x:auto">
      <h2>板块跌幅榜 <span class="hint">真实数据 · 附各板块领跌股（当天跌幅最大）</span></h2>
      <table id="sectorDownTable">
        <thead><tr><th>板块</th><th style="text-align:left">领跌股</th><th>当天</th><th>1周</th><th>1月</th><th>3月</th><th>6月</th></tr></thead>
        <tbody id="sectorDownTbody"></tbody>
      </table>
      <div class="intl-note" style="margin-top:10px">领跌股为板块内当天跌幅最大个股，来源：东方财富妙想选股器（精确获取）。</div>
    </div>
    <div class="card">
      <h2>主线研判 <span class="hint">分析判断</span></h2>
      <div class="plan-box" id="sectorInsight" style="margin-bottom:0"></div>
    </div>
  </section>

  <section class="panel" id="panel-stock">
    <div class="card" style="padding:0;overflow-x:auto">
      <table id="stockTable">
        <thead><tr><th>名称/代码</th><th>现价</th><th>涨跌幅</th><th>均线位置</th><th>止损价</th><th>评级</th></tr></thead>
        <tbody id="stockTbody"></tbody>
      </table>
    </div>
    <div class="card">
      <h2>持仓分层 <span class="hint">分析判断</span></h2>
      <div id="gradeList"></div>
    </div>
  </section>

  <section class="panel" id="panel-score">
    <div class="score-grid" id="scoreGrid"></div>
  </section>

  <section class="panel" id="panel-review">
    <div class="card">
      <h2>明日一句话计划</h2>
      <div class="plan-box">
        <b>冰点普跌日，严控仓位（≤2成）。</b>规避破位加速下跌的科技成长股（元件/通信设备/半导体），防御方向（银行/红利/家电）可少量持有；重点盯上证 3600 整数关（今日收 3602.57，濒临跌破），未见放量企稳前不抄底。
      </div>
    </div>
    <div class="card">
      <h2>明日剧本（三情景）</h2>
      <div class="scen"><div class="st st-opt">乐观</div><div class="tx">超跌反抽：上证守住 3600 并放量反包，科技股（半导体/元件）技术性修复，可小仓位博弈超跌反弹龙头。</div></div>
      <div class="scen"><div class="st st-mid">中性</div><div class="tx">缩量阴跌分化：防御板块继续占优，科技弱势整理，观望为主，不做左侧。</div></div>
      <div class="scen"><div class="st st-pes">悲观</div><div class="tx">破位下杀：跌破 3600 且放量，跌停潮延续，情绪冰点加深，D级持仓加速下探，空仓等拐点。</div></div>
    </div>
    <div class="card">
      <h2>纪律审计 <span class="hint">分析判断</span></h2>
      <div id="auditList"></div>
    </div>
  </section>
</main>

<footer class="disclaimer">
  数据来源：腾讯自选股（指数、涨跌分布、自选股行情、板块多周期）、东方财富（国际指数、涨停/跌停/炸板池）、东方财富妙想选股器（周期龙头股、领跌股）、新浪财经（北证50）。行情为 2026-11-16 收盘一次性快照，复盘专用，页面不发起实时数据请求，以交易所为准。<br>
  ⚠️ 本页面由 AI 基于公开数据整理生成，仅供参考，不构成任何投资建议。投资有风险，决策需谨慎。
</footer>

<script>
const STOCKS = __STOCKS__;
const INTL = __INTL__;
const LEADERS = __LEADERS__;
const TODAY_SECTORS = __TODAY__;
const SECTOR_DOWN = __SECDOWN__;
const DIST = __DIST__;
const ZB = __ZB__;

function fmt(n){if(n===null||n===undefined)return "—";return n>=0?"+"+n.toFixed(2):n.toFixed(2)}
function cls(chg){if(chg===null||chg===undefined)return "";return chg>0?"up":chg<0?"down":""}
function posCls(pos){if(pos==="5/10/20上方")return "pos-strong";if(pos==="全线下方")return "pos-weak";return "pos-mid"}

function renderIntl(){
  document.getElementById("intlGrid").innerHTML = INTL.map(g=>`
    <div class="intl-group"><div class="gh">${g.market}</div>
      ${g.items.map(i=>`<div class="ir"><span>${i.name}</span><span class="iv"><span class="ip">${i.price}</span><span class="${cls(i.chg)}">${fmt(i.chg)}%</span></span></div>`).join("")}
    </div>`).join("");
}
function renderLeaders(){
  const cols=[{key:"w1",label:"1周"},{key:"m1",label:"1月"},{key:"m3",label:"3月"},{key:"m6",label:"6月"}];
  document.getElementById("leaderGrid").innerHTML = cols.map(c=>`
    <div class="leader-col"><div class="lc-h">${c.label} 龙头板块</div>
      ${LEADERS[c.key].map(s=>`<div class="lc-item">
        <div class="lc-main"><span class="lc-name">${s.name}</span><span class="${cls(s.v)}">${fmt(s.v)}%</span></div>
        <div class="lc-ld">龙头 <b>${s.ld||"—"}</b> ${s.lc!=null?`<span class="${cls(s.lc)}">${fmt(s.lc)}%</span>`:''}</div>
      </div>`).join("")}
    </div>`).join("");
}
function renderTodaySectors(){
  document.getElementById("sectorTbody").innerHTML = TODAY_SECTORS.map(s=>`
    <tr>
      <td><span class="nm">${s.name}</span></td>
      <td style="text-align:left">${s.ld?`<span class="nm">${s.ld}</span> <span class="${cls(s.lc)}">${fmt(s.lc)}%</span>`:`<span style="color:var(--muted)">—</span>`}</td>
      <td class="${cls(s.today)}">${fmt(s.today)}%</td>
      <td class="${cls(s.w1)}">${fmt(s.w1)}%</td>
      <td class="${cls(s.m1)}">${fmt(s.m1)}%</td>
      <td class="${cls(s.m3)}">${fmt(s.m3)}%</td>
      <td class="${cls(s.m6)}">${fmt(s.m6)}%</td>
    </tr>`).join("");
}
function renderSectorDown(){
  document.getElementById("sectorDownTbody").innerHTML = SECTOR_DOWN.map(s=>{
    const ldStr = s.ld ? `<span class="nm">${s.ld}</span> <span class="${cls(s.lc)}">${fmt(s.lc)}%</span>` : `<span style="color:var(--muted)">—</span>`;
    return `<tr>
      <td><span class="nm">${s.name}</span></td>
      <td style="text-align:left">${ldStr}</td>
      <td class="${cls(s.today)}">${fmt(s.today)}%</td>
      <td class="${cls(s.w1)}">${fmt(s.w1)}%</td>
      <td class="${cls(s.m1)}">${fmt(s.m1)}%</td>
      <td class="${cls(s.m3)}">${fmt(s.m3)}%</td>
      <td class="${cls(s.m6)}">${fmt(s.m6)}%</td>
    </tr>`;
  }).join("");
}
function renderInsight(){
  document.getElementById("sectorInsight").innerHTML =
    `短线（1周）主线在银行（城商行 <span class="up">+4.02%</span>、国有大行 <span class="up">+3.43%</span>）、影视院线、电视广播与厨卫电器，防御 + 传媒属性突出，但元件 <b class="down">-8.71%</b>、通信设备 <b class="down">-8.67%</b>、半导体 <b class="down">-6.02%</b> 当天崩盘，成长方向全面破位；<br>` +
    `中期（1月/3月）强势主线是<b>数字媒体、影视院线、养殖业、小家电</b>，银行（国有大行）3月 <span class="up">+21.11%</span> / 6月 <span class="up">+22.83%</span> 持续走强，防御 + 红利属性突出；<br>` +
    `当天仅银行/家电/煤炭/调味品逆势上涨，属防御抱团；元件、通信设备、半导体、航天装备等科技成长领跌，且在 1月/3月 维度持续大幅走弱，反弹乏力，规避为主。`;
}
function renderZb(){
  document.getElementById("zbList").innerHTML = ZB.map(z=>`<span class="zb-chip">${z}</span>`).join("");
}
function renderStocks(){
  document.getElementById("stockTbody").innerHTML = STOCKS.map(s=>{
    const c = cls(s.chg);
    const stopStr = s.dist<=0 ? `<span class="down">已破位</span>` : s.stop.toFixed(2);
    return `<tr>
      <td><div class="nm">${s.name}</div><div class="code">${s.code}${s.etf?' <span style="color:var(--accent)">ETF</span>':''}</div></td>
      <td>${s.price.toFixed(s.price<1?3:2)}</td>
      <td class="${c}">${fmt(s.chg)}%</td>
      <td><span class="pos-tag ${posCls(s.pos)}">${s.pos}</span></td>
      <td>${stopStr}</td>
      <td><span class="grade g-${s.grade}">${s.grade}</span></td>
    </tr>`;
  }).join("");
}
function renderScores(){
  document.getElementById("scoreGrid").innerHTML = STOCKS.map(s=>{
    const dims = [["趋势",s.dims.trend,30],["量价",s.dims.vol,20],["强度",s.dims.strength,20],["板块",s.dims.sector,15],["风险",s.dims.risk,15]];
    const dimRows = dims.map(d=>`<div class="dim-row"><div class="dn">${d[0]}</div><div class="db"><div class="df" style="width:${d[1]/d[2]*100}%"></div></div><div class="dv">${d[1]}</div></div>`).join("");
    return `<div class="score-card">
      <div class="score-top"><div class="nm">${s.name}</div>
        <div class="ring"><svg width="50" height="50"><circle cx="25" cy="25" r="20" stroke="var(--bg)" stroke-width="5" fill="none"/><circle cx="25" cy="25" r="20" stroke="var(--accent)" stroke-width="5" fill="none" stroke-linecap="round" stroke-dasharray="126" stroke-dashoffset="${(126-126*s.total/100).toFixed(1)}"/></svg><div class="num">${s.total}</div></div>
      </div>
      <div style="font-size:11px;color:var(--muted);margin-bottom:8px"><span class="${cls(s.chg)}">${fmt(s.chg)}%</span> · ${s.sector} · <span class="grade g-${s.grade}" style="vertical-align:middle">${s.grade}</span></div>
      ${dimRows}
    </div>`;
  }).join("");
}
function renderGrades(){
  const order = {A:"A级 · 强势（持有/加仓）",B:"B级 · 健康（持有不动）",C:"C级 · 关注（盯盘观察）",D:"D级 · 处理（减仓/止损）"};
  const colors = {A:"up",B:"accent",C:"warn",D:"down"};
  let html = "";
  ["A","B","C","D"].forEach(g=>{
    const list = STOCKS.filter(s=>s.grade===g);
    if(list.length===0){ html += `<div style="font-size:13px;color:var(--muted);padding:5px 0">${order[g]}：无</div>`; return; }
    html += `<div style="padding:7px 0;border-bottom:1px solid var(--border)"><b style="color:var(--${colors[g]})">${order[g]}</b>（${list.length}只）<br>
      <span style="font-size:12px;color:var(--muted)">${list.map(s=>s.name).join("、")}</span></div>`;
  });
  document.getElementById("gradeList").innerHTML = html;
}
function renderAudit(){
  const d = STOCKS.filter(s=>s.grade==="D");
  const c = STOCKS.filter(s=>s.grade==="C");
  let html = `<div class="scen"><div class="st st-pes">止损</div><div class="tx">D级持仓 <b>${d.map(s=>s.name).join("、")||"无"}</b> 已破位或大跌，按纪律执行减仓/止损，不要因浮亏死扛。</div></div>`;
  html += `<div class="scen"><div class="st st-mid">观察</div><div class="tx">C级持仓 <b>${c.map(s=>s.name).join("、")||"无"}</b> 处于均线下方，设好止损位，跌破立即离场。</div></div>`;
  html += `<div class="scen"><div class="st st-opt">纪律</div><div class="tx">弱势市不追高、不抄底、不满仓。单票止损严格按「止损价」执行，跌破不留恋。</div></div>`;
  document.getElementById("auditList").innerHTML = html;
}
function switchTab(t){
  document.querySelectorAll(".panel").forEach(p=>p.classList.remove("active"));
  document.getElementById("panel-"+t).classList.add("active");
  document.querySelectorAll("nav.tabs button").forEach(b=>b.classList.toggle("active",b.dataset.tab===t));
}
renderIntl(); renderLeaders(); renderTodaySectors(); renderSectorDown(); renderInsight(); renderZb(); renderStocks(); renderScores(); renderGrades(); renderAudit();
</script>
</body>
</html>
"""

# 计算 pie 与评分环
down_pct = round(down / total * 100, 1) if total else 0
flat_pct = round(flat / total * 100, 1) if total else 0
up_pct = round(100 - down_pct - flat_pct, 1)
pie_down = down_pct
pie_flat = down_pct + flat_pct

score_offset = round(239 * (1 - SCORE / 100), 1)

HTML = HTML.replace("__SCORE__", str(SCORE))
HTML = HTML.replace("__SCORE_OFFSET__", str(score_offset))
HTML = HTML.replace("__ZT__", str(zt)).replace("__DT__", str(dt)).replace("__ZBCNT__", str(zb))
HTML = HTML.replace("__FR__", str(fr)).replace("__FRDOWN__", str(fr_down))
HTML = HTML.replace("__ZTR__", str(zt_dt_ratio))
HTML = HTML.replace("__UP__", str(up)).replace("__DOWN__", str(down)).replace("__FLAT__", str(flat))
HTML = HTML.replace("__TOTAL__", str(total))
HTML = HTML.replace("__UP_RATIO__", str(up_ratio))
HTML = HTML.replace("__DOWN_PCT__", str(down_pct))
HTML = HTML.replace("__IDX__", idx_html)
HTML = HTML.replace("__DISTHTML__", dist_html)
HTML = HTML.replace("__STOCKS__", json.dumps(STOCKS, ensure_ascii=False))
HTML = HTML.replace("__INTL__", json.dumps(INTL, ensure_ascii=False))
HTML = HTML.replace("__LEADERS__", json.dumps(LEADERS, ensure_ascii=False))
HTML = HTML.replace("__TODAY__", json.dumps(TODAY, ensure_ascii=False))
HTML = HTML.replace("__SECDOWN__", json.dumps(DOWN, ensure_ascii=False))
HTML = HTML.replace("__DIST__", json.dumps(DIST, ensure_ascii=False))
HTML = HTML.replace("__ZB__", json.dumps(ZB, ensure_ascii=False))

# 修正 pie 的 conic-gradient 百分比（在 CSS 里用 token 已替换，但需要确保数值）
HTML = HTML.replace("__PIE_DOWN__", str(pie_down)).replace("__PIE_FLAT__", str(pie_flat))

out = os.path.join(BASE, "trade-review.html")
open(out, "w", encoding="utf-8").write(HTML)
print("已生成 trade-review.html，大小", len(HTML), "字符")
print("市场评分", SCORE, "上涨占比", up_ratio, "%", "封板率", fr, "%")
