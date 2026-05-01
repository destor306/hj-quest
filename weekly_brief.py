"""
HJ Intelligence Engine v3
- Weekly brief with AI analysis
- Investment suggestions (long-term + short-term, limited budget)
- Saves to Supabase briefs + investment_suggestions tables
"""

import os
import json
import time
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path

# ─────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────
USER_PROFILE = {
    "name": "Hyunjun",
    "full_name": "Hyunjun Yoo",
    "role": "Senior Court Analyst II",
    "income": 61000,
    "monthly_investable": 200,  # realistic monthly amount to invest
    "location": "Tallahassee, FL",
    "goals": [
        "Build LifeRPG into a product with paying users",
        "Complete MSSE degree at FSU",
        "Reach SES-level role by 2028",
        "Launch first business",
        "Buy first investment property",
    ],
    "watchlist": ["VOO", "VTI", "SCHD", "AAPL", "MSFT", "O", "KO"],
    "risk_tolerance": "moderate",  # low, moderate, high
    "investment_horizon": "long",  # long = 10+ years
    "narrator_tone": "mix of tough love + coach — direct, calls him by name, no fluff",
}

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rcxuqpdlzrdzamrgwtjs.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_UGydllMpryYrIsQnphtW3g_N4hW7AHZ")

ARTICLES = [
    {"title": "The Psychology of Money (free PDF)", "url": "https://www.collaborativefund.com/uploads/Collaborative_Fund_The_Psychology_of_Money.pdf", "topic": "Wealth mindset"},
    {"title": "The Shockingly Simple Math Behind Early Retirement", "url": "https://www.mrmoneymustache.com/2012/01/13/the-shockingly-simple-math-behind-early-retirement/", "topic": "Financial independence"},
    {"title": "How to Get Rich (without getting lucky) — Naval", "url": "https://nav.al/rich", "topic": "Wealth building"},
    {"title": "Wealth, Actually", "url": "https://collabfund.com/blog/wealth-actually/", "topic": "What wealth really means"},
    {"title": "The Ladders of Wealth Creation", "url": "https://nathanbarry.com/wealth-creation/", "topic": "4 stages from $0 to business"},
    {"title": "The Boring Business Empire — Codie Sanchez", "url": "https://contrarianthinking.co/the-boring-business-empire/", "topic": "Small business acquisition"},
    {"title": "Do Things That Don't Scale — Paul Graham", "url": "http://paulgraham.com/ds.html", "topic": "Startup mindset"},
    {"title": "The Four Levels of Financial Independence", "url": "https://affordanything.com/four-levels-of-financial-independence/", "topic": "FI framework"},
    {"title": "If You're So Smart, Why Aren't You Rich?", "url": "https://fs.blog/why-smart-people-dont-get-rich/", "topic": "Career + wealth gap"},
    {"title": "Supabase Quickstart Guide", "url": "https://supabase.com/docs/guides/getting-started/quickstarts/reactjs", "topic": "LifeRPG backend build"},
    {"title": "r/personalfinance Wiki", "url": "https://www.reddit.com/r/personalfinance/wiki/index/", "topic": "Finance fundamentals"},
    {"title": "Florida Retirement System (FRS) Overview", "url": "https://www.myfrs.com/TblOfContents.htm", "topic": "Your pension"},
]

RECIPES = [
    {"name": "Doenjang Jjigae", "time": "20 min", "url": "https://www.koreanbapsang.com/doenjang-jjigae-korean-soybean-paste/"},
    {"name": "Kimchi Fried Rice", "time": "15 min", "url": "https://www.maangchi.com/recipe/kimchi-bokkeumbap"},
    {"name": "Sheet Pan Chicken Thighs", "time": "35 min", "url": "https://www.seriouseats.com/crispy-roasted-chicken-thighs-sheet-pan"},
    {"name": "Bibimbap", "time": "30 min", "url": "https://www.maangchi.com/recipe/bibimbap"},
    {"name": "Tamago Gohan (Egg Rice Bowl)", "time": "5 min", "url": "https://www.justonecookbook.com/tamago-gohan/"},
    {"name": "Pasta Aglio e Olio", "time": "20 min", "url": "https://www.seriouseats.com/pasta-aglio-e-olio-recipe"},
    {"name": "Galbi Jjim", "time": "2 hr", "url": "https://www.koreanbapsang.com/galbijjim-braised-beef-short-ribs/"},
    {"name": "Japchae", "time": "30 min", "url": "https://www.maangchi.com/recipe/japchae"},
]

HUSTLE_TASKS = [
    {"task": "Watch: Codie Sanchez on buying boring businesses", "time": "22 min", "url": "https://www.youtube.com/watch?v=GHGBbVKIFGI"},
    {"task": "Read: How to deploy on Vercel (free)", "time": "15 min", "url": "https://vercel.com/docs/getting-started-with-vercel"},
    {"task": "Watch: Supabase in 100 seconds", "time": "10 min", "url": "https://www.youtube.com/watch?v=znjIzEFMzTk"},
    {"task": "Research: Vending machine business guide", "time": "30 min", "url": "https://www.entrepreneur.com/starting-a-business/how-to-start-a-vending-machine-business/281409"},
    {"task": "Read: How to register an LLC in Florida", "time": "15 min", "url": "https://dos.myflorida.com/sunbiz/start-a-business/"},
    {"task": "Watch: Alex Hormozi — making your first $1M", "time": "25 min", "url": "https://www.youtube.com/watch?v=3KODk2bNGaM"},
    {"task": "Browse: Indie Hackers — side business stories", "time": "20 min", "url": "https://www.indiehackers.com/"},
    {"task": "Build: Add one new feature to HJ Quest", "time": "30 min", "url": ""},
]


# ─────────────────────────────────────────
# DATA FETCHERS
# ─────────────────────────────────────────

def fetch_stock_data(tickers):
    results = {}
    print(f"  📈 Fetching stocks: {', '.join(tickers)}")
    for ticker in tickers:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
            resp = requests.get(url, headers={"User-Agent": "HJQuest/1.0"}, timeout=10)
            if resp.status_code == 200:
                meta = resp.json().get("chart", {}).get("result", [{}])[0].get("meta", {})
                price = round(meta.get("regularMarketPrice", 0), 2)
                prev = round(meta.get("chartPreviousClose", 0), 2)
                high52 = round(meta.get("fiftyTwoWeekHigh", 0), 2)
                low52 = round(meta.get("fiftyTwoWeekLow", 0), 2)
                change_pct = round(((price - prev) / prev * 100) if prev else 0, 2)
                # How far from 52w low (buying opportunity indicator)
                pct_from_low = round(((price - low52) / low52 * 100) if low52 else 0, 1)
                results[ticker] = {
                    "price": price, "prev_close": prev,
                    "change_pct": change_pct,
                    "52w_high": high52, "52w_low": low52,
                    "pct_from_52w_low": pct_from_low,
                }
            time.sleep(0.3)
        except Exception as e:
            results[ticker] = {"error": str(e)}
    return results


def fetch_news(api_key=None):
    articles = []
    print("  📰 Fetching news...")
    if api_key:
        try:
            resp = requests.get("https://newsapi.org/v2/everything", params={
                "q": "personal finance investing stocks dividends ETF",
                "sortBy": "relevancy", "pageSize": 8, "language": "en",
                "apiKey": api_key,
                "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            }, timeout=10)
            if resp.status_code == 200:
                for a in resp.json().get("articles", [])[:8]:
                    articles.append({"title": a.get("title", ""), "source": a.get("source", {}).get("name", ""), "url": a.get("url", "")})
                return articles
        except Exception:
            pass
    # RSS fallback
    try:
        resp = requests.get(
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=VOO,AAPL,MSFT&region=US&lang=en-US",
            timeout=8, headers={"User-Agent": "HJQuest/1.0"}
        )
        if resp.status_code == 200:
            for item in resp.text.split("<item>")[1:7]:
                title = item.split("<title>")[1].split("</title>")[0].replace("<![CDATA[", "").replace("]]>", "").strip() if "<title>" in item else ""
                link = item.split("<link>")[1].split("</link>")[0].strip() if "<link>" in item else ""
                if title:
                    articles.append({"title": title, "source": "Yahoo Finance", "url": link})
    except Exception:
        pass
    print(f"    ✓ {len(articles)} articles")
    return articles[:8]


def fetch_reddit():
    posts = []
    print("  🤖 Fetching Reddit...")
    for sub in ["personalfinance", "financialindependence", "stocks"]:
        try:
            resp = requests.get(
                f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=3",
                headers={"User-Agent": "HJQuest/1.0"}, timeout=10
            )
            if resp.status_code == 200:
                for p in resp.json().get("data", {}).get("children", []):
                    d = p.get("data", {})
                    posts.append({"title": d.get("title", ""), "subreddit": f"r/{sub}", "score": d.get("score", 0)})
            time.sleep(0.5)
        except Exception:
            pass
    print(f"    ✓ {len(posts)} posts")
    return posts


def fetch_macro():
    print("  🏦 Fetching macro data...")
    macro = {}
    try:
        resp = requests.get(
            "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC?interval=1d&range=1y",
            headers={"User-Agent": "HJQuest/1.0"}, timeout=10
        )
        if resp.status_code == 200:
            result = resp.json().get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            prices = [p for p in result.get("indicators", {}).get("quote", [{}])[0].get("close", []) if p]
            if prices:
                current = meta.get("regularMarketPrice", prices[-1])
                ytd_change = ((current - prices[0]) / prices[0] * 100)
                macro["sp500_price"] = round(current, 2)
                macro["sp500_ytd"] = f"{round(ytd_change, 1)}%"
    except Exception:
        pass
    return macro


def get_rotation(items):
    return items[datetime.now().isocalendar()[1] % len(items)]


# ─────────────────────────────────────────
# INVESTMENT SUGGESTIONS ENGINE
# ─────────────────────────────────────────

def generate_investment_suggestions(stock_data, macro, profile):
    """
    Generate specific investment suggestions for someone with limited monthly budget.
    Returns structured suggestions for long-term and short-term.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return get_fallback_suggestions(stock_data, profile)

    print("  💡 Generating investment suggestions...")

    monthly = profile["monthly_investable"]

    # Build stock context — identify what looks cheap vs expensive right now
    stock_context = []
    for ticker, d in stock_data.items():
        if "error" not in d:
            from_low = d.get("pct_from_52w_low", 0)
            from_high = ((d["52w_high"] - d["price"]) / d["52w_high"] * 100) if d.get("52w_high") else 0
            status = "near 52w low (potential buy zone)" if from_low < 15 else "near 52w high (be cautious)" if from_low > 80 else "mid-range"
            stock_context.append(f"  {ticker}: ${d['price']} | {from_low}% above 52w low | {status}")

    prompt = f"""You are giving personalized investment advice to {profile['name']}.

THEIR SITUATION:
- Income: ${profile['income']:,}/year (take home ~${int(profile['income'] * 0.75 / 12):,}/month)
- Monthly amount available to invest: ${monthly}
- Risk tolerance: {profile['risk_tolerance']}
- Investment horizon: {profile['investment_horizon']} term (10+ years)
- Location: {profile['location']}
- Goals: {', '.join(profile['goals'][:3])}
- Currently has: minimal investments, building from scratch

CURRENT MARKET DATA:
S&P 500: ${macro.get('sp500_price', 'N/A')} (YTD: {macro.get('sp500_ytd', 'N/A')})

WATCHLIST PRICES:
{chr(10).join(stock_context)}

Give SPECIFIC, ACTIONABLE investment suggestions for someone starting with limited money (${monthly}/month).

Structure your response as JSON with this exact format:
{{
  "long_term": [
    {{
      "ticker": "VOO",
      "name": "Vanguard S&P 500 ETF",
      "action": "Buy",
      "suggested_amount": 100,
      "why": "One sentence plain English reason",
      "how_to_start": "Specific first step",
      "time_horizon": "10-20 years",
      "risk_level": "Low"
    }}
  ],
  "short_term": [
    {{
      "ticker": "SCHD",
      "name": "Schwab Dividend ETF",
      "action": "Watch",
      "suggested_amount": 50,
      "why": "One sentence plain English reason",
      "how_to_start": "Specific first step",
      "time_horizon": "1-3 years",
      "risk_level": "Low-Medium"
    }}
  ],
  "with_200_dollars": {{
    "breakdown": [
      {{"ticker": "VOO", "amount": 120, "reason": "Core index fund foundation"}},
      {{"ticker": "SCHD", "amount": 50, "reason": "Dividend income building"}},
      {{"ticker": "cash", "amount": 30, "reason": "Keep liquid for opportunity"}}
    ],
    "total": 200,
    "summary": "One paragraph explaining the strategy for someone starting with $200/month"
  }},
  "avoid_right_now": [
    {{
      "ticker": "or concept",
      "reason": "Why to avoid"
    }}
  ],
  "wealth_building_path": "2-3 sentences on how $200/month compounded over 10-20 years gets Hyunjun to his goals"
}}

Be specific to HIS situation — Florida, government job, family, building toward generational wealth.
Respond with ONLY the JSON. No other text."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 1500,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        if resp.status_code == 200:
            raw = resp.json()["content"][0]["text"].strip()
            # Strip any markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
    except Exception as e:
        print(f"    ⚠ Investment suggestion error: {e}")

    return get_fallback_suggestions(stock_data, profile)


def get_fallback_suggestions(stock_data, profile):
    """Fallback suggestions when API is unavailable."""
    monthly = profile["monthly_investable"]
    return {
        "long_term": [
            {"ticker": "VOO", "name": "Vanguard S&P 500 ETF",
             "action": "Buy monthly", "suggested_amount": int(monthly * 0.6),
             "why": "Tracks the entire S&P 500 — the single best long-term wealth builder for most people.",
             "how_to_start": "Open a Fidelity or Schwab account, buy $1 worth to start — no minimum.",
             "time_horizon": "10-20 years", "risk_level": "Low"},
            {"ticker": "SCHD", "name": "Schwab US Dividend ETF",
             "action": "Buy monthly", "suggested_amount": int(monthly * 0.3),
             "why": "Pays quarterly dividends and grows them every year — passive income that compounds.",
             "how_to_start": "Same brokerage as VOO. Set up automatic monthly purchase.",
             "time_horizon": "10+ years", "risk_level": "Low"},
        ],
        "short_term": [
            {"ticker": "HYSA", "name": "High-Yield Savings Account",
             "action": "Open now", "suggested_amount": int(monthly * 0.1),
             "why": "4-5% interest on your emergency fund — better than a regular savings account.",
             "how_to_start": "Open Marcus by Goldman Sachs or Ally Bank — takes 10 minutes.",
             "time_horizon": "0-2 years", "risk_level": "None"},
        ],
        "with_200_dollars": {
            "breakdown": [
                {"ticker": "VOO", "amount": int(monthly * 0.6), "reason": "Core long-term foundation"},
                {"ticker": "SCHD", "amount": int(monthly * 0.25), "reason": "Dividend income building"},
                {"ticker": "HYSA", "amount": int(monthly * 0.15), "reason": "Emergency fund top-up"},
            ],
            "total": monthly,
            "summary": f"${monthly}/month invested consistently in VOO from age 30 grows to ~$400K by age 55 at historical returns. Add SCHD for dividend income. This is boring but it works."
        },
        "avoid_right_now": [
            {"ticker": "Individual stocks", "reason": "Build the index fund base first before picking individual stocks."},
            {"ticker": "Crypto", "reason": "Too volatile for a family with limited investable income."},
        ],
        "wealth_building_path": f"${monthly}/month in VOO for 20 years = ~$400K at 7% average return. Add SCHD dividends reinvested and you're looking at $500K+. That's the foundation. The rental property and business come later — they accelerate it."
    }


# ─────────────────────────────────────────
# AI ANALYSIS
# ─────────────────────────────────────────

def analyze_with_claude(stock_data, news, reddit_posts, macro, profile):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "[Add ANTHROPIC_API_KEY to .env for AI analysis]"

    print("  🤖 Generating weekly AI analysis...")

    stock_lines = []
    for ticker, d in stock_data.items():
        if "error" not in d:
            arrow = "▲" if d.get("change_pct", 0) >= 0 else "▼"
            stock_lines.append(f"  {ticker}: ${d['price']} ({arrow}{abs(d['change_pct'])}%)")

    prompt = f"""You are the personal financial analyst for {profile['name']}.

PROFILE: {profile['full_name']}, {profile['role']}, ${profile['income']:,}/yr, {profile['location']}
GOALS: {', '.join(profile['goals'][:3])}
TONE: {profile['narrator_tone']}

WATCHLIST:
{chr(10).join(stock_lines)}

S&P 500: {macro.get('sp500_price', 'N/A')} (YTD: {macro.get('sp500_ytd', 'N/A')})

NEWS:
{chr(10).join(['• ' + a['title'] for a in news[:5]])}

REDDIT:
{chr(10).join(['• [' + p['subreddit'] + '] ' + p['title'] for p in reddit_posts[:3]])}

Write a weekly brief. Sections:
1. MARKET PULSE (2-3 sentences)
2. WATCHLIST (one line per ticker)
3. NEWS FOR YOU (3 bullets relevant to his situation)
4. THIS WEEK'S MOVE (1-2 specific actions)
5. STRAIGHT TALK (1 paragraph, direct, personal, calls him by name)

Under 350 words. Plain text only. No markdown."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 800,
                  "messages": [{"role": "user", "content": prompt}]},
            timeout=30
        )
        if resp.status_code == 200:
            return resp.json()["content"][0]["text"]
        return f"[Claude error {resp.status_code}]"
    except Exception as e:
        return f"[Claude request failed: {e}]"


# ─────────────────────────────────────────
# FORMAT
# ─────────────────────────────────────────

def format_brief(stock_data, news, reddit_posts, macro, ai_analysis, suggestions):
    now = datetime.now()
    article = get_rotation(ARTICLES)
    recipe = get_rotation(RECIPES)
    hustle = get_rotation(HUSTLE_TASKS)
    monthly = USER_PROFILE["monthly_investable"]

    stock_lines = []
    for ticker, d in stock_data.items():
        if "error" not in d:
            arrow = "▲" if d.get("change_pct", 0) >= 0 else "▼"
            stock_lines.append(f"  {ticker:<6} ${d['price']:<9} {arrow}{abs(d['change_pct'])}%")

    # Format investment suggestions
    long_term = suggestions.get("long_term", [])
    short_term = suggestions.get("short_term", [])
    breakdown = suggestions.get("with_200_dollars", {}).get("breakdown", [])
    avoid = suggestions.get("avoid_right_now", [])
    path = suggestions.get("wealth_building_path", "")

    lt_lines = "\n".join([f"  {s['ticker']}: {s['action']} ${s['suggested_amount']}/mo — {s['why']}" for s in long_term])
    st_lines = "\n".join([f"  {s['ticker']}: {s['action']} — {s['why']}" for s in short_term])
    bd_lines = "\n".join([f"  ${b['amount']} → {b['ticker']}: {b['reason']}" for b in breakdown])
    avoid_lines = "\n".join([f"  ✗ {a['ticker']}: {a['reason']}" for a in avoid])

    return f"""{'='*52}
HJ QUEST — WEEKLY INTELLIGENCE BRIEF
Week {now.isocalendar()[1]} · {now.strftime('%B %d, %Y')}
{'='*52}

MARKET SNAPSHOT
S&P 500: ${macro.get('sp500_price', 'N/A')} · YTD: {macro.get('sp500_ytd', 'N/A')}

YOUR WATCHLIST
{chr(10).join(stock_lines)}

AI ANALYSIS
{ai_analysis}

{'='*52}
INVESTMENT SUGGESTIONS — ${monthly}/MONTH BUDGET
{'='*52}

LONG-TERM (10+ years — build wealth while you sleep)
{lt_lines}

SHORT-TERM MOVES
{st_lines}

HOW TO SPLIT YOUR ${monthly} THIS MONTH
{bd_lines}

WHAT TO AVOID RIGHT NOW
{avoid_lines}

THE BIGGER PICTURE
{path}

{'='*52}

THIS WEEK'S FREE READ
{article['title']}
{article['url']}

THIS WEEK'S RECIPE
{recipe['name']} ({recipe['time']})
{recipe['url']}

SIDE HUSTLE TASK
{hustle['task']} ({hustle['time']})
{hustle['url'] or '(open HJ Quest and build)'}

TOP NEWS
{chr(10).join(['• ' + a['title'] for a in news[:5]])}

REDDIT THIS WEEK
{chr(10).join(['• [' + p['subreddit'] + '] ' + p['title'] for p in reddit_posts[:3]])}

{'='*52}
Generated: {now.strftime('%Y-%m-%d %H:%M')} · Next: {(now + timedelta(days=7)).strftime('%A %B %d')}
{'='*52}"""


# ─────────────────────────────────────────
# SUPABASE
# ─────────────────────────────────────────

def push_to_supabase(brief_text, stock_data, article, recipe, hustle, suggestions, week_num):
    print("  📡 Pushing to Supabase...")
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }

    # Push brief
    payload = {
        "week_number": week_num,
        "brief_text": brief_text,
        "stock_data": json.dumps(stock_data),
        "article_title": article["title"],
        "article_url": article["url"],
        "recipe_name": recipe["name"],
        "recipe_url": recipe["url"],
        "hustle_task": hustle["task"],
        "hustle_url": hustle.get("url", ""),
    }
    resp = requests.post(f"{SUPABASE_URL}/rest/v1/briefs", headers=headers, json=payload, timeout=15)
    if resp.status_code in (200, 201):
        print("    ✓ Brief saved")
    else:
        print(f"    ⚠ Brief error {resp.status_code}: {resp.text[:200]}")

    # Push investment suggestions
    for term, items in [("long", suggestions.get("long_term", [])), ("short", suggestions.get("short_term", []))]:
        for s in items:
            inv_payload = {
                "ticker": s.get("ticker", ""),
                "action": s.get("action", ""),
                "price_at_time": stock_data.get(s.get("ticker", ""), {}).get("price", 0),
                "notes": f"{s.get('why', '')} | How to start: {s.get('how_to_start', '')}",
                "amount": s.get("suggested_amount", 0),
                "term": term,
            }
            resp2 = requests.post(f"{SUPABASE_URL}/rest/v1/investment_log", headers=headers, json=inv_payload, timeout=15)
            if resp2.status_code not in (200, 201):
                print(f"    ⚠ Investment log error for {s.get('ticker')}: {resp2.text[:100]}")

    print("    ✓ Investment suggestions saved")


def save_to_file(brief_text):
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / f"weekly_brief_{datetime.now().strftime('%Y-%m-%d')}.md"
    filepath.write_text(brief_text, encoding="utf-8")
    print(f"  ✓ Saved: {filepath}")


# ─────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────

def get_mock_data():
    stocks = {
        "VOO":  {"price": 521.40, "prev_close": 518.20, "change_pct": 0.62,  "52w_high": 545.00, "52w_low": 440.00, "pct_from_52w_low": 18.5},
        "VTI":  {"price": 248.15, "prev_close": 246.80, "change_pct": 0.55,  "52w_high": 265.00, "52w_low": 210.00, "pct_from_52w_low": 18.2},
        "SCHD": {"price": 79.40,  "prev_close": 78.90,  "change_pct": 0.63,  "52w_high": 85.00,  "52w_low": 68.00,  "pct_from_52w_low": 16.8},
        "AAPL": {"price": 189.30, "prev_close": 191.20, "change_pct": -0.99, "52w_high": 220.00, "52w_low": 165.00, "pct_from_52w_low": 14.7},
        "MSFT": {"price": 415.80, "prev_close": 412.40, "change_pct": 0.82,  "52w_high": 468.00, "52w_low": 360.00, "pct_from_52w_low": 15.5},
        "O":    {"price": 56.20,  "prev_close": 55.90,  "change_pct": 0.54,  "52w_high": 62.00,  "52w_low": 48.00,  "pct_from_52w_low": 17.1},
        "KO":   {"price": 68.45,  "prev_close": 68.10,  "change_pct": 0.51,  "52w_high": 73.00,  "52w_low": 58.00,  "pct_from_52w_low": 18.0},
    }
    news = [
        {"title": "Fed holds rates steady, signals patient approach", "source": "Reuters", "url": ""},
        {"title": "S&P 500 notches weekly gain on tech strength", "source": "MarketWatch", "url": ""},
        {"title": "Florida housing market cools slightly", "source": "Local", "url": ""},
        {"title": "SCHD ex-dividend date approaching", "source": "Seeking Alpha", "url": ""},
        {"title": "Microsoft cloud revenue beats estimates", "source": "CNBC", "url": ""},
    ]
    reddit = [
        {"title": "Finally maxed my Roth IRA at 32", "subreddit": "r/personalfinance", "score": 8420},
        {"title": "How I replaced my salary with dividends in 8 years", "subreddit": "r/financialindependence", "score": 6100},
        {"title": "VOO vs VTI — does it actually matter?", "subreddit": "r/stocks", "score": 3200},
    ]
    macro = {"sp500_ytd": "+8.4%", "sp500_price": "5,842"}
    return stocks, news, reddit, macro


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Use mock data")
    parser.add_argument("--no-save", action="store_true", help="Skip file save")
    args = parser.parse_args()

    print(f"\n{'='*52}")
    print("HJ QUEST — INTELLIGENCE ENGINE v3")
    print(f"Running: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*52}\n")

    if args.test:
        print("⚡ TEST MODE\n")
        stocks, news, reddit, macro = get_mock_data()
    else:
        print("Collecting live data...\n")
        stocks = fetch_stock_data(USER_PROFILE["watchlist"])
        news = fetch_news(os.environ.get("NEWS_API_KEY"))
        reddit = fetch_reddit()
        macro = fetch_macro()

    article = get_rotation(ARTICLES)
    recipe = get_rotation(RECIPES)
    hustle = get_rotation(HUSTLE_TASKS)
    week_num = datetime.now().isocalendar()[1]

    print("\nGenerating analysis...\n")
    ai_analysis = analyze_with_claude(stocks, news, reddit, macro, USER_PROFILE)
    suggestions = generate_investment_suggestions(stocks, macro, USER_PROFILE)

    brief = format_brief(stocks, news, reddit, macro, ai_analysis, suggestions)
    print(brief)

    if not args.no_save:
        print("\nSaving...\n")
        save_to_file(brief)

    push_to_supabase(brief, stocks, article, recipe, hustle, suggestions, week_num)
    print("\n✓ Done. Brief and investment suggestions live on your phone.\n")


if __name__ == "__main__":
    main()
