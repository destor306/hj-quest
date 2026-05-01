"""
HJ Intelligence Engine — Weekly Brief Generator
With Supabase backend for phone app sync
"""

import os
import sys
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
    "location": "Tallahassee, FL",
    "goals": [
        "Build LifeRPG into a real product with paying users",
        "Complete MSSE degree at FSU",
        "Reach SES-level government role by 2028",
        "Launch first business (vending machines or laundromat)",
        "Buy first investment/rental property",
    ],
    "watchlist": ["VOO", "VTI", "SCHD", "AAPL", "MSFT", "O", "KO"],
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
    {"name": "Galbi Jjim (Braised Beef Short Ribs)", "time": "2 hr", "url": "https://www.koreanbapsang.com/galbijjim-braised-beef-short-ribs/"},
    {"name": "Japchae (Glass Noodles)", "time": "30 min", "url": "https://www.maangchi.com/recipe/japchae"},
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
# DATA FETCHERS (same as before)
# ─────────────────────────────────────────

def fetch_stock_data(tickers):
    results = {}
    print(f"  📈 Fetching stocks: {', '.join(tickers)}")
    for ticker in tickers:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?interval=1d&range=5d"
            headers = {"User-Agent": "HJQuest/1.0"}
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                meta = data.get("chart", {}).get("result", [{}])[0].get("meta", {})
                price = round(meta.get("regularMarketPrice", 0), 2)
                prev = round(meta.get("chartPreviousClose", 0), 2)
                change_pct = round(((price - prev) / prev * 100) if prev else 0, 2)
                results[ticker] = {
                    "price": price, "prev_close": prev,
                    "change_pct": change_pct,
                    "52w_high": round(meta.get("fiftyTwoWeekHigh", 0), 2),
                    "52w_low": round(meta.get("fiftyTwoWeekLow", 0), 2),
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
                "q": "personal finance investing stocks dividends",
                "sortBy": "relevancy", "pageSize": 8, "language": "en",
                "apiKey": api_key,
                "from": (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d"),
            }, timeout=10)
            if resp.status_code == 200:
                for a in resp.json().get("articles", [])[:8]:
                    articles.append({"title": a.get("title",""), "source": a.get("source",{}).get("name",""), "url": a.get("url","")})
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
            for item in resp.text.split("<item>")[1:6]:
                title = item.split("<title>")[1].split("</title>")[0].replace("<![CDATA[","").replace("]]>","").strip() if "<title>" in item else ""
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
    for sub in ["personalfinance", "financialindependence"]:
        try:
            resp = requests.get(
                f"https://www.reddit.com/r/{sub}/top.json?t=week&limit=3",
                headers={"User-Agent": "HJQuest/1.0"}, timeout=10
            )
            if resp.status_code == 200:
                for p in resp.json().get("data",{}).get("children",[]):
                    d = p.get("data",{})
                    posts.append({"title": d.get("title",""), "subreddit": f"r/{sub}", "score": d.get("score",0)})
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
            result = resp.json().get("chart",{}).get("result",[{}])[0]
            meta = result.get("meta",{})
            prices = [p for p in result.get("indicators",{}).get("quote",[{}])[0].get("close",[]) if p]
            if prices:
                ytd_change = ((meta.get("regularMarketPrice", prices[-1]) - prices[0]) / prices[0] * 100)
                macro["sp500_price"] = round(meta.get("regularMarketPrice", prices[-1]), 2)
                macro["sp500_ytd"] = f"{round(ytd_change, 1)}%"
    except Exception:
        pass
    return macro


def get_rotation(items):
    idx = datetime.now().isocalendar()[1] % len(items)
    return items[idx]


# ─────────────────────────────────────────
# AI ANALYSIS
# ─────────────────────────────────────────

def analyze_with_claude(stock_data, news, reddit_posts, macro, profile):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return "[Add ANTHROPIC_API_KEY to .env for AI analysis]"

    print("  🤖 Generating AI analysis...")

    stock_lines = []
    for ticker, d in stock_data.items():
        if "error" not in d:
            arrow = "▲" if d.get("change_pct", 0) >= 0 else "▼"
            stock_lines.append(f"  {ticker}: ${d['price']} ({arrow}{abs(d['change_pct'])}%)")

    prompt = f"""You are the personal financial analyst for {profile['name']}.

PROFILE: {profile['full_name']}, {profile['role']}, ${profile['income']:,}/yr, {profile['location']}
GOALS: {', '.join(profile['goals'][:3])}
TONE: {profile['narrator_tone']}

WATCHLIST THIS WEEK:
{chr(10).join(stock_lines)}

S&P 500: {macro.get('sp500_price','N/A')} (YTD: {macro.get('sp500_ytd','N/A')})

TOP NEWS:
{chr(10).join(['• ' + a['title'] for a in news[:5]])}

REDDIT THIS WEEK:
{chr(10).join(['• [' + p['subreddit'] + '] ' + p['title'] for p in reddit_posts[:4]])}

Write a weekly brief for {profile['name']}. Sections:
1. MARKET PULSE (2-3 sentences, what matters to him)
2. WATCHLIST (one line per ticker — change, meaning, action if any)
3. NEWS FOR YOU (3 bullets relevant to his goals/location)
4. THIS WEEK'S MOVE (1-2 specific actions based on the data)
5. STRAIGHT TALK (1 paragraph, direct, personal, his narrator tone, calls him by name)

Keep under 350 words. No markdown. No asterisks. Plain text only."""

    try:
        resp = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": "claude-sonnet-4-20250514", "max_tokens": 800, "messages": [{"role": "user", "content": prompt}]},
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

def format_brief(stock_data, news, reddit_posts, macro, ai_analysis):
    now = datetime.now()
    article = get_rotation(ARTICLES)
    recipe = get_rotation(RECIPES)
    hustle = get_rotation(HUSTLE_TASKS)

    stock_lines = []
    for ticker, d in stock_data.items():
        if "error" not in d:
            arrow = "▲" if d.get("change_pct", 0) >= 0 else "▼"
            stock_lines.append(f"  {ticker:<6} ${d['price']:<9} {arrow}{abs(d['change_pct'])}%")
        else:
            stock_lines.append(f"  {ticker:<6} [unavailable]")

    return f"""{'='*52}
HJ QUEST — WEEKLY INTELLIGENCE BRIEF
Week {now.isocalendar()[1]} · {now.strftime('%B %d, %Y')}
{'='*52}

MARKET SNAPSHOT
S&P 500: ${macro.get('sp500_price','N/A')} · YTD: {macro.get('sp500_ytd','N/A')}

YOUR WATCHLIST
{chr(10).join(stock_lines)}

AI ANALYSIS
{ai_analysis}

THIS WEEK'S FREE READ
{article['title']}
Topic: {article['topic']}
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

def push_to_supabase(brief_text, stock_data, article, recipe, hustle, week_num):
    """Write the weekly brief to Supabase so the phone app can read it."""
    print("  📡 Pushing to Supabase...")

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }

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

    try:
        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/briefs",
            headers=headers,
            json=payload,
            timeout=15
        )
        if resp.status_code in (200, 201):
            print("    ✓ Brief saved to Supabase")
            return True
        else:
            print(f"    ⚠ Supabase error {resp.status_code}: {resp.text[:200]}")
            return False
    except Exception as e:
        print(f"    ⚠ Supabase failed: {e}")
        return False


def fetch_latest_from_supabase():
    """Fetch the most recent brief from Supabase (for testing)."""
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }
    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/briefs?order=created_at.desc&limit=1",
            headers=headers, timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            return data[0] if data else None
    except Exception as e:
        print(f"Supabase fetch error: {e}")
    return None


# ─────────────────────────────────────────
# SAVE TO FILE
# ─────────────────────────────────────────

def save_to_file(brief_text):
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    filepath = output_dir / f"weekly_brief_{datetime.now().strftime('%Y-%m-%d')}.md"
    filepath.write_text(brief_text, encoding="utf-8")
    print(f"  ✓ Saved: {filepath}")
    return str(filepath)


# ─────────────────────────────────────────
# MOCK DATA
# ─────────────────────────────────────────

def get_mock_data():
    stocks = {
        "VOO":  {"price": 521.40, "prev_close": 518.20, "change_pct": 0.62,  "52w_high": 545.00, "52w_low": 440.00},
        "VTI":  {"price": 248.15, "prev_close": 246.80, "change_pct": 0.55,  "52w_high": 265.00, "52w_low": 210.00},
        "SCHD": {"price": 79.40,  "prev_close": 78.90,  "change_pct": 0.63,  "52w_high": 85.00,  "52w_low": 68.00},
        "AAPL": {"price": 189.30, "prev_close": 191.20, "change_pct": -0.99, "52w_high": 220.00, "52w_low": 165.00},
        "MSFT": {"price": 415.80, "prev_close": 412.40, "change_pct": 0.82,  "52w_high": 468.00, "52w_low": 360.00},
        "O":    {"price": 56.20,  "prev_close": 55.90,  "change_pct": 0.54,  "52w_high": 62.00,  "52w_low": 48.00},
        "KO":   {"price": 68.45,  "prev_close": 68.10,  "change_pct": 0.51,  "52w_high": 73.00,  "52w_low": 58.00},
    }
    news = [
        {"title": "Fed holds rates steady, signals patient approach", "source": "Reuters", "url": ""},
        {"title": "S&P 500 notches weekly gain on tech strength", "source": "MarketWatch", "url": ""},
        {"title": "Florida housing market cools but remains above national average", "source": "Local", "url": ""},
        {"title": "SCHD ex-dividend date approaches", "source": "Seeking Alpha", "url": ""},
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
    parser.add_argument("--fetch", action="store_true", help="Fetch latest brief from Supabase")
    args = parser.parse_args()

    # Just fetch and display latest brief
    if args.fetch:
        print("\nFetching latest brief from Supabase...")
        brief = fetch_latest_from_supabase()
        if brief:
            print(brief.get("brief_text", "No text found"))
        else:
            print("No briefs found in Supabase yet.")
        return

    print(f"\n{'='*52}")
    print("HJ QUEST — INTELLIGENCE ENGINE")
    print(f"Running: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*52}\n")

    # Collect data
    if args.test:
        print("⚡ TEST MODE — mock data\n")
        stocks, news, reddit, macro = get_mock_data()
    else:
        print("Collecting live data...\n")
        stocks = fetch_stock_data(USER_PROFILE["watchlist"])
        news = fetch_news(os.environ.get("NEWS_API_KEY"))
        reddit = fetch_reddit()
        macro = fetch_macro()

    # Rotate weekly content
    article = get_rotation(ARTICLES)
    recipe = get_rotation(RECIPES)
    hustle = get_rotation(HUSTLE_TASKS)
    week_num = datetime.now().isocalendar()[1]

    # Generate AI analysis
    print("\nGenerating analysis...\n")
    ai_analysis = analyze_with_claude(stocks, news, reddit, macro, USER_PROFILE)

    # Format
    brief = format_brief(stocks, news, reddit, macro, ai_analysis)

    # Output
    print(brief)

    if not args.no_save:
        print("\nSaving...\n")
        save_to_file(brief)

    # Push to Supabase
    push_to_supabase(brief, stocks, article, recipe, hustle, week_num)

    print("\n✓ Done. Brief is now live on your phone app.\n")


if __name__ == "__main__":
    main()
