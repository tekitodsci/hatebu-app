#!/usr/bin/env python3
"""
ネタ探知機 - はてなブックマーク ランキング（クラウドデプロイ版）

ローカル実行:
  pip install -r requirements.txt
  python app.py

デプロイ:
  Render / Railway / Heroku 等にプッシュしてください。
"""

import json
import os
from urllib.parse import urlparse

import feedparser
import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

CATEGORIES = {
    "all": ("総合", "https://b.hatena.ne.jp/entrylist.rss"),
    "it": ("テクノロジー", "https://b.hatena.ne.jp/entrylist/it.rss"),
    "social": ("社会", "https://b.hatena.ne.jp/entrylist/social.rss"),
    "economics": ("政治経済", "https://b.hatena.ne.jp/entrylist/economics.rss"),
    "life": ("暮らし", "https://b.hatena.ne.jp/entrylist/life.rss"),
    "knowledge": ("学び", "https://b.hatena.ne.jp/entrylist/knowledge.rss"),
    "entertainment": ("エンタメ", "https://b.hatena.ne.jp/entrylist/entertainment.rss"),
}


def get_domain(url):
    try:
        return urlparse(url).hostname.replace("www.", "")
    except:
        return ""


def fetch_articles(cat_key):
    if cat_key not in CATEGORIES:
        return []

    _, url = CATEGORIES[cat_key]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    feed = feedparser.parse(resp.text)

    articles = []
    for entry in feed.entries:
        bookmarks = 0
        if hasattr(entry, "hatena_bookmarkcount"):
            bookmarks = int(entry.hatena_bookmarkcount)
        articles.append({
            "title": entry.get("title", ""),
            "link": entry.get("link", ""),
            "bookmarks": bookmarks,
            "domain": get_domain(entry.get("link", "")),
        })

    articles.sort(key=lambda x: x["bookmarks"], reverse=True)
    return articles[:30]


@app.route("/")
def index():
    return HTML_PAGE


@app.route("/api/articles")
def api_articles():
    cat = request.args.get("cat", "all")
    try:
        articles = fetch_articles(cat)
        return jsonify({"articles": articles})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


HTML_PAGE = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ネタ探知機 - はてブ急上昇検出</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@300;400;500;700;900&family=DM+Mono:wght@400;500&display=swap');

  :root {
    --bg: #08090c;
    --surface: #111318;
    --surface-hover: #191c24;
    --border: #252836;
    --text: #e4e6f0;
    --text-dim: #7a7f96;
    --hot: #ff4d4d;
    --warm: #ff9f43;
    --rising: #54e0c7;
    --hatena: #00a4de;
    --rank-gold: #ffd700;
    --rank-silver: #b0b8cc;
    --rank-bronze: #c87533;
  }

  * { margin: 0; padding: 0; box-sizing: border-box; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Noto Sans JP', sans-serif;
    min-height: 100vh;
  }

  .container {
    max-width: 800px;
    margin: 0 auto;
    padding: 36px 20px;
  }

  header { margin-bottom: 28px; }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
  }

  .logo-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, var(--hot), var(--warm));
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    color: white;
  }

  h1 { font-size: 21px; font-weight: 700; }
  .subtitle { color: var(--text-dim); font-size: 12px; margin-top: 3px; }

  .controls {
    display: flex;
    gap: 6px;
    margin-bottom: 20px;
    flex-wrap: wrap;
    align-items: center;
  }

  .tab {
    padding: 7px 14px;
    border-radius: 18px;
    border: 1px solid var(--border);
    background: transparent;
    color: var(--text-dim);
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.2s;
  }

  .tab:hover { border-color: var(--hatena); color: var(--text); }
  .tab.active { background: var(--hatena); border-color: var(--hatena); color: white; font-weight: 500; }

  .fetch-btn {
    padding: 7px 18px;
    border-radius: 18px;
    border: none;
    background: linear-gradient(135deg, var(--hot), var(--warm));
    color: white;
    font-family: 'Noto Sans JP', sans-serif;
    font-size: 12px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    margin-left: auto;
  }

  .fetch-btn:hover { opacity: 0.85; }
  .fetch-btn:disabled { opacity: 0.4; cursor: not-allowed; }

  .info-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    font-size: 11px;
  }

  .status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
  }

  .status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    animation: pulse 2s ease-in-out infinite;
  }

  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }

  .update-time {
    font-family: 'DM Mono', monospace;
    color: var(--text-dim);
  }

  .article-list {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .article-item {
    display: grid;
    grid-template-columns: 40px 1fr;
    gap: 14px;
    padding: 14px 16px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    transition: all 0.2s;
    animation: slideIn 0.35s ease-out both;
    text-decoration: none;
    color: var(--text);
  }

  .article-item:hover {
    background: var(--surface-hover);
    border-color: rgba(0, 164, 222, 0.25);
    transform: translateX(3px);
  }

  @keyframes slideIn {
    from { opacity: 0; transform: translateX(-16px); }
    to { opacity: 1; transform: translateX(0); }
  }

  .rank-num {
    font-family: 'DM Mono', monospace;
    font-size: 18px;
    font-weight: 500;
    text-align: center;
    padding-top: 2px;
  }

  .rank-1 .rank-num { color: var(--rank-gold); }
  .rank-2 .rank-num { color: var(--rank-silver); }
  .rank-3 .rank-num { color: var(--rank-bronze); }
  .article-item:not(.rank-1):not(.rank-2):not(.rank-3) .rank-num { color: var(--text-dim); }

  .article-title {
    font-size: 14px;
    font-weight: 500;
    line-height: 1.5;
    margin-bottom: 6px;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .article-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    align-items: center;
    font-size: 11px;
  }

  .bookmark-count {
    font-family: 'DM Mono', monospace;
    font-weight: 500;
  }

  .bk-hot { color: var(--hot); }
  .bk-warm { color: var(--warm); }
  .bk-rising { color: var(--rising); }
  .bk-normal { color: var(--text-dim); }

  .source-domain {
    color: var(--text-dim);
    font-family: 'DM Mono', monospace;
    font-size: 10px;
  }

  .heat-indicator {
    font-size: 10px;
    font-weight: 500;
  }

  .heat-fire { color: var(--hot); }
  .heat-warm { color: var(--warm); }
  .heat-new { color: var(--rising); }

  .msg-area {
    text-align: center;
    padding: 60px 20px;
    color: var(--text-dim);
    font-size: 14px;
    line-height: 1.8;
  }

  .spinner {
    width: 28px; height: 28px;
    border: 2px solid var(--border);
    border-top-color: var(--hatena);
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    margin: 0 auto 14px;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .footer {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
    text-align: center;
    color: var(--text-dim);
    font-size: 10px;
    line-height: 1.6;
  }

  .footer a { color: var(--hatena); text-decoration: none; }

  @media (max-width: 480px) {
    .container { padding: 20px 14px; }
    h1 { font-size: 18px; }
    .article-item { grid-template-columns: 32px 1fr; gap: 10px; padding: 12px; }
    .fetch-btn { margin-left: 0; width: 100%; margin-top: 6px; }
  }
</style>
</head>
<body>

<div class="container">
  <header>
    <div class="logo">
      <div class="logo-icon">🔥</div>
      <div>
        <h1>ネタ探知機</h1>
        <div class="subtitle">はてなブックマーク新着から「これから来る」ネタを早期検出</div>
      </div>
    </div>
  </header>

  <div class="controls">
    <button class="tab active" data-cat="all">総合</button>
    <button class="tab" data-cat="it">テクノロジー</button>
    <button class="tab" data-cat="social">社会</button>
    <button class="tab" data-cat="economics">政治経済</button>
    <button class="tab" data-cat="life">暮らし</button>
    <button class="tab" data-cat="knowledge">学び</button>
    <button class="tab" data-cat="entertainment">エンタメ</button>
    <button class="fetch-btn" id="fetchBtn">検出開始</button>
  </div>

  <div class="info-bar">
    <div class="status">
      <div class="status-dot" id="statusDot" style="background:var(--hatena)"></div>
      <span id="statusText" style="color:var(--hatena)">READY</span>
    </div>
    <span class="update-time" id="updateTime"></span>
  </div>

  <div id="articleList" class="article-list">
    <div class="msg-area">
      <div style="font-size:28px; margin-bottom:10px;">📡</div>
      「検出開始」を押すと、はてブ新着から<br>急上昇しそうなネタを探します。
    </div>
  </div>

  <div class="footer">
    データソース: <a href="https://b.hatena.ne.jp" target="_blank">はてなブックマーク</a> RSS
  </div>
</div>

<script>
let currentCat = 'all';

document.querySelectorAll('.tab').forEach(tab => {
  tab.addEventListener('click', () => {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    currentCat = tab.dataset.cat;
  });
});

document.getElementById('fetchBtn').addEventListener('click', fetchArticles);

function updateTime() {
  document.getElementById('updateTime').textContent =
    new Date().toLocaleString('ja-JP', { hour:'2-digit', minute:'2-digit', second:'2-digit' });
}

function setStatus(color, text) {
  document.getElementById('statusDot').style.background = color;
  const st = document.getElementById('statusText');
  st.style.color = color;
  st.textContent = text;
}

function getRankClass(i) {
  return i === 0 ? 'rank-1' : i === 1 ? 'rank-2' : i === 2 ? 'rank-3' : '';
}

function getBkClass(b) {
  if (b >= 50) return 'bk-hot';
  if (b >= 20) return 'bk-warm';
  if (b >= 5) return 'bk-rising';
  return 'bk-normal';
}

function getHeat(b) {
  if (b >= 100) return { icon: '🔥🔥', label: '爆発', cls: 'heat-fire' };
  if (b >= 50) return { icon: '🔥', label: '急上昇', cls: 'heat-fire' };
  if (b >= 20) return { icon: '📈', label: '上昇中', cls: 'heat-warm' };
  if (b >= 5) return { icon: '🌱', label: '芽が出始め', cls: 'heat-new' };
  return { icon: '', label: '', cls: '' };
}

function renderArticles(articles) {
  const list = document.getElementById('articleList');
  list.innerHTML = articles.map((a, i) => {
    const heat = getHeat(a.bookmarks);
    return `
    <a class="article-item ${getRankClass(i)}" style="animation-delay:${i*0.04}s" href="${a.link}" target="_blank" rel="noopener">
      <div class="rank-num">${String(i+1).padStart(2,'0')}</div>
      <div>
        <div class="article-title">${a.title}</div>
        <div class="article-meta">
          <span class="bookmark-count ${getBkClass(a.bookmarks)}">B! ${a.bookmarks}</span>
          ${heat.label ? `<span class="heat-indicator ${heat.cls}">${heat.icon} ${heat.label}</span>` : ''}
          <span class="source-domain">${a.domain}</span>
        </div>
      </div>
    </a>`;
  }).join('');
}

async function fetchArticles() {
  const btn = document.getElementById('fetchBtn');
  const list = document.getElementById('articleList');

  btn.disabled = true;
  btn.textContent = '検出中...';
  setStatus('var(--hatena)', 'LOADING');
  list.innerHTML = '<div class="msg-area"><div class="spinner"></div>はてなブックマークから取得中...</div>';

  try {
    const resp = await fetch(`/api/articles?cat=${currentCat}`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();

    if (data.articles && data.articles.length > 0) {
      renderArticles(data.articles);
      setStatus('var(--rising)', 'LIVE');
      updateTime();
    } else {
      throw new Error('記事が取得できませんでした');
    }
  } catch (err) {
    list.innerHTML = `<div class="msg-area" style="color:var(--hot)">
      取得に失敗しました。<br>
      <span style="font-size:12px;color:var(--text-dim)">${err.message}</span>
    </div>`;
    setStatus('var(--hot)', 'ERROR');
  }

  btn.disabled = false;
  btn.textContent = '検出開始';
}

updateTime();
setInterval(updateTime, 1000);
fetchArticles();
</script>

</body>
</html>"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"\\n  🔥 ネタ探知機 Web版")
    print(f"  http://localhost:{port} でアクセスしてください\\n")
    app.run(host="0.0.0.0", port=port, debug=False)
