"""
Goal Template Generator
Run ONCE to populate Supabase with 500+ goal templates.
After this runs, your app uses the database — not the API — for quest suggestions.

Usage:
  source venv/bin/activate
  python generate_templates.py
"""

import os
import json
import time
import requests

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://rcxuqpdlzrdzamrgwtjs.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "sb_publishable_UGydllMpryYrIsQnphtW3g_N4hW7AHZ")

SB_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

# ─────────────────────────────────────────────────────────────
# GOAL CATEGORIES + TEMPLATES
# Pre-built so we don't use API on every user request
# ─────────────────────────────────────────────────────────────

GOAL_TEMPLATES = {

    # ── FINANCIAL GOALS ──────────────────────────────────────
    "pay_off_credit_card": {
        "category": "financial",
        "title": "Pay off credit card debt",
        "icon": "💳",
        "description": "Eliminate credit card debt completely",
        "roadmap": [
            "List all cards by balance and interest rate",
            "Stop adding new charges to any card",
            "Pay minimum on all but highest-rate card",
            "Throw every extra dollar at highest-rate card",
            "Celebrate each card paid off, roll payment to next",
        ],
        "quests": [
            {"title": "List all your debts", "description": "Write down every card: balance, interest rate, minimum payment. Know your enemy.", "xp": 30, "difficulty": "easy"},
            {"title": "Call your credit card company", "description": "Ask for a lower interest rate. Takes 5 min. Works 30% of the time.", "xp": 50, "difficulty": "easy"},
            {"title": "Cut one subscription", "description": "Cancel one recurring charge you don't really use. Put that money toward debt.", "xp": 40, "difficulty": "easy"},
            {"title": "Set up automatic minimum payments", "description": "Never miss a payment again. Late fees are the enemy.", "xp": 30, "difficulty": "easy"},
            {"title": "Calculate your payoff date", "description": "Use a debt calculator to see exactly when you'll be free. Knowledge = motivation.", "xp": 25, "difficulty": "easy"},
            {"title": "Find $50 extra this week", "description": "Sell something, skip eating out, pick up an extra shift. $50 extra = momentum.", "xp": 60, "difficulty": "medium"},
            {"title": "Research balance transfer cards", "description": "A 0% intro APR card could save you hundreds in interest. 30 min of research.", "xp": 50, "difficulty": "medium"},
            {"title": "Track every expense for 7 days", "description": "You can't cut what you can't see. Use your notes app or a free tracker.", "xp": 70, "difficulty": "medium"},
            {"title": "Create a bare-bones budget", "description": "Income minus necessities = debt payment. Everything else is optional.", "xp": 60, "difficulty": "medium"},
            {"title": "Start a side hustle research session", "description": "Spend 30 min finding one way to earn $100-500/month extra. One idea is all you need.", "xp": 80, "difficulty": "medium"},
            {"title": "Make an extra payment this week", "description": "Any amount above the minimum. Even $20 extra saves you interest.", "xp": 90, "difficulty": "hard"},
            {"title": "Meal prep for the week", "description": "Cook 5 days of meals in one session. Saves $50-100 vs eating out. All goes to debt.", "xp": 80, "difficulty": "hard"},
            {"title": "Negotiate a bill", "description": "Call your phone, internet, or insurance company. Ask for a better rate. 20 min call.", "xp": 100, "difficulty": "hard"},
            {"title": "Sell 3 things you don't use", "description": "Facebook Marketplace, eBay, or OfferUp. Extra cash straight to debt.", "xp": 90, "difficulty": "hard"},
            {"title": "Complete one month of no unnecessary spending", "description": "Only necessities for 30 days. Hard but transformative.", "xp": 150, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "First payment made", "xp": 50, "badge": "🎯 First Strike"},
            {"title": "First $500 paid off", "xp": 150, "badge": "💪 Momentum Builder"},
            {"title": "First card fully paid", "xp": 300, "badge": "✂️ Card Cutter"},
            {"title": "50% of debt eliminated", "xp": 500, "badge": "⚔️ Halfway Hero"},
            {"title": "Debt free", "xp": 1000, "badge": "🏆 Debt Slayer"},
        ]
    },

    "build_emergency_fund": {
        "category": "financial",
        "title": "Build a $1,000 emergency fund",
        "icon": "🛡️",
        "description": "Create a financial safety net",
        "roadmap": [
            "Open a separate high-yield savings account",
            "Set up automatic $50-100/week transfer",
            "Find one expense to cut temporarily",
            "Add any windfalls (tax refund, bonuses) directly",
            "Hit $1,000 — never touch it unless true emergency",
        ],
        "quests": [
            {"title": "Open a HYSA account", "description": "Marcus by Goldman, Ally, or SoFi. Takes 10 min. Earns 4-5% vs 0.01% at big banks.", "xp": 50, "difficulty": "easy"},
            {"title": "Transfer your first $50", "description": "The first transfer is the hardest. Do it today, right now.", "xp": 40, "difficulty": "easy"},
            {"title": "Set up automatic weekly transfer", "description": "$25-50/week = $1,300-2,600/year. Automate it and forget it.", "xp": 60, "difficulty": "easy"},
            {"title": "Calculate your monthly expenses", "description": "What does 3 months of expenses actually cost you? Know your target.", "xp": 30, "difficulty": "easy"},
            {"title": "Name your emergency fund", "description": "Seriously — name it 'Do Not Touch' or 'Freedom Fund'. Psychology matters.", "xp": 20, "difficulty": "easy"},
            {"title": "Cut eating out this week", "description": "Cook every meal this week. Save $50-100. Transfer it all.", "xp": 70, "difficulty": "medium"},
            {"title": "Find a no-spend weekend activity", "description": "Plan a free weekend. Park, cooking at home, free events. Save $100+.", "xp": 60, "difficulty": "medium"},
            {"title": "Review all subscriptions", "description": "Cancel anything you haven't used in 30 days. Redirect to fund.", "xp": 50, "difficulty": "medium"},
            {"title": "Sell something for $50+", "description": "Old phone, clothes, electronics. Put it straight in the fund.", "xp": 80, "difficulty": "medium"},
            {"title": "Apply tax refund to fund", "description": "If you have a refund coming, commit it to the emergency fund now.", "xp": 100, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "First $100 saved", "xp": 100, "badge": "🌱 First Seed"},
            {"title": "$500 saved", "xp": 200, "badge": "🛡️ Half Shield"},
            {"title": "$1,000 saved", "xp": 400, "badge": "🏰 Fortress Built"},
            {"title": "3 months expenses saved", "xp": 800, "badge": "⚡ Untouchable"},
        ]
    },

    "invest_first_dollar": {
        "category": "financial",
        "title": "Start investing for the first time",
        "icon": "📈",
        "description": "Open a brokerage account and make your first investment",
        "roadmap": [
            "Open a free brokerage account (Fidelity or Schwab)",
            "Learn what an index fund and ETF are (30 min)",
            "Transfer your first $50",
            "Buy your first share of VOO or VTI",
            "Set up automatic monthly investment",
        ],
        "quests": [
            {"title": "Read: What is an index fund?", "description": "Spend 20 min on this. It's the most important concept in personal investing.", "xp": 40, "difficulty": "easy", "url": "https://www.investopedia.com/terms/i/indexfund.asp"},
            {"title": "Open a Fidelity account", "description": "No minimums, no fees, best for beginners. Takes 10 min.", "xp": 60, "difficulty": "easy", "url": "https://www.fidelity.com/open-account/overview"},
            {"title": "Learn what VOO is", "description": "VOO = all 500 biggest US companies in one ETF. Warren Buffett recommends it.", "xp": 30, "difficulty": "easy", "url": "https://investor.vanguard.com/investment-products/etfs/profile/voo"},
            {"title": "Transfer $50 to your brokerage", "description": "Link your bank and transfer any amount. The habit is more important than the size.", "xp": 70, "difficulty": "medium"},
            {"title": "Buy your first fractional share", "description": "Buy $25-50 of VOO. You don't need a full share — fractional shares are fine.", "xp": 100, "difficulty": "medium"},
            {"title": "Set up automatic monthly investment", "description": "Even $25/month automated beats $500 once a year manually.", "xp": 80, "difficulty": "medium"},
            {"title": "Learn what a Roth IRA is", "description": "Tax-free growth. One of the best financial tools available to you.", "xp": 50, "difficulty": "easy", "url": "https://www.investopedia.com/terms/r/rothira.asp"},
            {"title": "Open a Roth IRA", "description": "Contribute up to $7,000/year. Grows tax-free. Open one today.", "xp": 120, "difficulty": "hard"},
            {"title": "Set a 10-year investment target", "description": "Calculate what $200/month becomes in 10 years at 7% return. Run the math.", "xp": 60, "difficulty": "easy"},
            {"title": "Don't touch it for 30 days", "description": "Markets go up and down. Stay the course for one full month. The hardest and most important quest.", "xp": 150, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "Account opened", "xp": 100, "badge": "🚪 Door Opened"},
            {"title": "First investment made", "xp": 200, "badge": "📈 Investor Born"},
            {"title": "First dividend received", "xp": 150, "badge": "💸 Passive Income Start"},
            {"title": "$1,000 invested", "xp": 400, "badge": "💎 Four Figures"},
            {"title": "Roth IRA opened", "xp": 300, "badge": "🏦 Tax Free Builder"},
        ]
    },

    "save_house_down_payment": {
        "category": "financial",
        "title": "Save for a house down payment",
        "icon": "🏠",
        "description": "Save 10-20% down payment for a home",
        "roadmap": [
            "Research home prices in your target area",
            "Calculate your target down payment (10-20%)",
            "Open dedicated HYSA for down payment savings",
            "Set monthly savings target and automate",
            "Track progress toward purchase date goal",
        ],
        "quests": [
            {"title": "Research home prices in your area", "description": "Spend 30 min on Zillow or Realtor.com. Know your target number.", "xp": 40, "difficulty": "easy"},
            {"title": "Calculate your down payment target", "description": "10% of $250K = $25,000. Know your exact number before you start saving.", "xp": 30, "difficulty": "easy"},
            {"title": "Check your credit score", "description": "Free at CreditKarma or AnnualCreditReport.com. Aim for 700+ for best rates.", "xp": 40, "difficulty": "easy", "url": "https://www.annualcreditreport.com"},
            {"title": "Research first-time homebuyer programs in Florida", "description": "Florida has grants and assistance programs. You might qualify.", "xp": 60, "difficulty": "medium", "url": "https://www.floridahousing.org/programs"},
            {"title": "Open a dedicated HYSA for down payment", "description": "Keep it separate. Label it 'Future Home'. Watch it grow.", "xp": 50, "difficulty": "easy"},
            {"title": "Calculate how long until you can buy", "description": "Target amount ÷ monthly savings = months to goal. Make it real.", "xp": 40, "difficulty": "easy"},
            {"title": "Get pre-approved for a mortgage", "description": "Just to see what you'd qualify for. No commitment. Takes 30 min.", "xp": 100, "difficulty": "hard"},
            {"title": "Save 1 month's extra payment", "description": "Go above your target this month. Momentum matters.", "xp": 80, "difficulty": "medium"},
        ],
        "milestones": [
            {"title": "First $1,000 saved", "xp": 100, "badge": "🌱 Foundation Laid"},
            {"title": "25% of target saved", "xp": 200, "badge": "🧱 Brick by Brick"},
            {"title": "50% of target saved", "xp": 400, "badge": "🏗️ Halfway Home"},
            {"title": "100% of target saved", "xp": 800, "badge": "🔑 Keys Ready"},
        ]
    },

    "increase_income": {
        "category": "financial",
        "title": "Increase your income by $500/month",
        "icon": "💰",
        "description": "Add a new income stream or get a raise",
        "roadmap": [
            "Identify your highest-value skill",
            "Research what that skill pays freelance",
            "Get your first paid project or raise ask",
            "Systematize it to repeat monthly",
            "Scale toward $500/month consistent",
        ],
        "quests": [
            {"title": "List your top 3 marketable skills", "description": "What can you do that others will pay for? Python, data analysis, writing, design?", "xp": 30, "difficulty": "easy"},
            {"title": "Research freelance rates for your skill", "description": "Check Upwork, Fiverr, Toptal. What does your skill actually pay per hour?", "xp": 40, "difficulty": "easy", "url": "https://www.upwork.com"},
            {"title": "Create a simple portfolio page", "description": "Even a Google Doc or GitHub with 3 examples. Takes 1 hour.", "xp": 80, "difficulty": "medium"},
            {"title": "Apply for one freelance job", "description": "One application on Upwork or LinkedIn. The first one is the hardest.", "xp": 100, "difficulty": "medium"},
            {"title": "Ask for a raise at your current job", "description": "Research market rates, document your value, schedule the conversation.", "xp": 120, "difficulty": "hard"},
            {"title": "Earn your first $50 outside of your job", "description": "Freelance, selling something, or a gig. Proof the path exists.", "xp": 200, "difficulty": "hard"},
            {"title": "Set up a simple invoice system", "description": "Wave or PayPal invoice. Look professional from day one.", "xp": 50, "difficulty": "easy"},
            {"title": "Find one recurring client or gig", "description": "Recurring income = real income stream. One client who pays monthly.", "xp": 250, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "First extra $50 earned", "xp": 150, "badge": "💡 Proof of Concept"},
            {"title": "First $100 month", "xp": 250, "badge": "🌊 New Stream"},
            {"title": "First $250 month", "xp": 400, "badge": "⚡ Building Momentum"},
            {"title": "$500/month consistent", "xp": 800, "badge": "🚀 Income Unlocked"},
        ]
    },

    # ── CAREER GOALS ─────────────────────────────────────────
    "get_first_job": {
        "category": "career",
        "title": "Land your first job after graduation",
        "icon": "🎓",
        "description": "Get hired for your first professional role",
        "roadmap": [
            "Build a clean resume and LinkedIn profile",
            "Apply to 5 jobs per day consistently",
            "Practice interview answers for top 20 questions",
            "Network with 3 people in your target field weekly",
            "Follow up on every application within 48 hours",
        ],
        "quests": [
            {"title": "Build a one-page resume", "description": "Clean, simple, one page. Use a free template. Focus on skills and projects.", "xp": 80, "difficulty": "medium", "url": "https://www.resume.com/resume-builder"},
            {"title": "Update your LinkedIn profile", "description": "Professional photo, complete summary, all experience filled in. Takes 1 hour.", "xp": 60, "difficulty": "easy"},
            {"title": "Apply to 5 jobs today", "description": "Indeed, LinkedIn, Glassdoor. 5 applications, done before noon.", "xp": 100, "difficulty": "medium"},
            {"title": "Research your target companies", "description": "Pick 10 companies you want to work for. Know their mission, products, culture.", "xp": 50, "difficulty": "easy"},
            {"title": "Answer: Tell me about yourself", "description": "Write and rehearse your 60-second professional story. You'll use it in every interview.", "xp": 70, "difficulty": "medium"},
            {"title": "Connect with 3 people on LinkedIn", "description": "Reach out to alumni, recruiters, or employees at your target companies.", "xp": 80, "difficulty": "medium"},
            {"title": "Ask someone for an informational interview", "description": "30 min call with someone in your target role. Ask how they got there.", "xp": 120, "difficulty": "hard"},
            {"title": "Complete a relevant online course", "description": "Coursera, LinkedIn Learning, or YouTube. One certification in your target field.", "xp": 150, "difficulty": "hard", "url": "https://www.coursera.org"},
            {"title": "Practice 5 behavioral interview questions", "description": "STAR method: Situation, Task, Action, Result. Practice out loud.", "xp": 90, "difficulty": "medium"},
            {"title": "Follow up on your applications", "description": "Email the hiring manager 5 days after applying. Most people never do this.", "xp": 100, "difficulty": "medium"},
            {"title": "Build a portfolio project", "description": "One project that shows your skills. GitHub repo, design portfolio, writing sample.", "xp": 200, "difficulty": "hard"},
            {"title": "Attend a networking event", "description": "Meetup.com, LinkedIn events, or industry association. Meet 3 real people.", "xp": 150, "difficulty": "hard", "url": "https://www.meetup.com"},
        ],
        "milestones": [
            {"title": "Resume completed", "xp": 100, "badge": "📄 Ready to Apply"},
            {"title": "First 10 applications sent", "xp": 150, "badge": "🎯 In the Game"},
            {"title": "First interview scheduled", "xp": 300, "badge": "🤝 Interview Ready"},
            {"title": "First offer received", "xp": 600, "badge": "🏆 Hired"},
        ]
    },

    "change_careers": {
        "category": "career",
        "title": "Change careers into tech/data",
        "icon": "💻",
        "description": "Transition to a tech or data role",
        "roadmap": [
            "Learn Python basics (60 hours over 2 months)",
            "Build 2-3 portfolio projects relevant to target role",
            "Get one relevant certification",
            "Start applying while continuing to learn",
            "Land first role — even if it's a step down in title",
        ],
        "quests": [
            {"title": "Complete Python basics", "description": "Codecademy Python course, free. 20 hours. Do 1 hour/day.", "xp": 150, "difficulty": "hard", "url": "https://www.codecademy.com/learn/learn-python-3"},
            {"title": "Build a data analysis project", "description": "Find a public dataset, analyze it with Python/pandas, publish to GitHub.", "xp": 200, "difficulty": "hard"},
            {"title": "Get Google Data Analytics Certificate", "description": "6 months, $49/month via Coursera. Recognized by employers.", "xp": 300, "difficulty": "hard", "url": "https://www.coursera.org/professional-certificates/google-data-analytics"},
            {"title": "Update LinkedIn to reflect new direction", "description": "Add your new skills, projects, and learning. Signal the transition.", "xp": 60, "difficulty": "easy"},
            {"title": "Apply to 3 entry-level data roles", "description": "Don't wait until you feel ready. Apply now and learn from feedback.", "xp": 120, "difficulty": "medium"},
            {"title": "Join a tech community", "description": "Local Python meetup, online Slack community, or subreddit. Get in the ecosystem.", "xp": 80, "difficulty": "medium"},
            {"title": "Find a mentor in your target field", "description": "One LinkedIn message to someone 2-3 years ahead of you.", "xp": 150, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "First course completed", "xp": 200, "badge": "🐍 Skills Building"},
            {"title": "First portfolio project published", "xp": 300, "badge": "🔨 Builder"},
            {"title": "First tech job interview", "xp": 400, "badge": "🚪 Door Opening"},
            {"title": "Career transition complete", "xp": 1000, "badge": "🦋 Transformed"},
        ]
    },

    "get_promoted": {
        "category": "career",
        "title": "Get promoted to the next level",
        "icon": "⬆️",
        "description": "Earn a promotion at your current job",
        "roadmap": [
            "Understand exactly what the next level requires",
            "Document all your current wins and impact",
            "Take on one project beyond your current role",
            "Build relationships with decision-makers",
            "Have the direct promotion conversation",
        ],
        "quests": [
            {"title": "Read your company's promotion criteria", "description": "What does the next level actually require? Get the job description or ask HR.", "xp": 40, "difficulty": "easy"},
            {"title": "Document your last 3 wins", "description": "Quantify your impact. Saved X hours, increased Y by Z%. Write it down.", "xp": 60, "difficulty": "medium"},
            {"title": "Schedule a career conversation with your manager", "description": "Ask directly: what do I need to do to earn the next level in 6-12 months?", "xp": 120, "difficulty": "hard"},
            {"title": "Volunteer for a high-visibility project", "description": "The project your manager or their manager is watching. Get on it.", "xp": 100, "difficulty": "medium"},
            {"title": "Build a relationship with a senior colleague", "description": "Lunch, coffee, or a genuine check-in with someone above your level.", "xp": 80, "difficulty": "medium"},
            {"title": "Complete one skill gap", "description": "What's the one skill the next level requires that you're missing? Close it.", "xp": 150, "difficulty": "hard"},
            {"title": "Write your promotion case document", "description": "One page: your impact, your skills, why you're ready. Used in the actual conversation.", "xp": 180, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "Promotion criteria understood", "xp": 100, "badge": "🗺️ Path Clear"},
            {"title": "First high-visibility win", "xp": 200, "badge": "⭐ Standing Out"},
            {"title": "Promotion conversation had", "xp": 300, "badge": "💬 Spoke Up"},
            {"title": "Promotion received", "xp": 800, "badge": "🚀 Level Up"},
        ]
    },

    "start_a_business": {
        "category": "career",
        "title": "Start your first business",
        "icon": "🏢",
        "description": "Launch a business and make your first dollar",
        "roadmap": [
            "Pick one business idea and research it for 2 weeks",
            "Talk to 10 potential customers before building anything",
            "Register your LLC and open a business bank account",
            "Make your first sale (any amount)",
            "Reach $1,000/month in revenue",
        ],
        "quests": [
            {"title": "Write down your top 3 business ideas", "description": "No filter. Whatever you've been thinking about. Just get them on paper.", "xp": 30, "difficulty": "easy"},
            {"title": "Research one idea for 2 hours", "description": "Market size, competitors, what customers actually pay. Is this real?", "xp": 80, "difficulty": "medium"},
            {"title": "Talk to 5 potential customers", "description": "Not to sell — to learn. What's their problem? Would they pay to solve it?", "xp": 150, "difficulty": "hard"},
            {"title": "Register an LLC in Florida", "description": "$125 online. Takes 15 min. Protects your personal assets.", "xp": 100, "difficulty": "medium", "url": "https://dos.myflorida.com/sunbiz/start-a-business/"},
            {"title": "Open a business bank account", "description": "Keep business and personal money completely separate from day one.", "xp": 60, "difficulty": "easy"},
            {"title": "Create a simple offer", "description": "One sentence: I help [who] with [what] for $[price]. That's your business.", "xp": 80, "difficulty": "medium"},
            {"title": "Make your first sale", "description": "Any amount. $5, $50, $500. Proof the business is real.", "xp": 300, "difficulty": "hard"},
            {"title": "Watch: Codie Sanchez on boring businesses", "description": "22 min. Changes how you think about what's worth building.", "xp": 60, "difficulty": "easy", "url": "https://www.youtube.com/watch?v=GHGBbVKIFGI"},
            {"title": "Set up a simple website or landing page", "description": "Carrd.co — free, 30 min. You need a place to send people.", "xp": 100, "difficulty": "medium", "url": "https://carrd.co"},
        ],
        "milestones": [
            {"title": "Idea validated with real customers", "xp": 200, "badge": "✅ Validated"},
            {"title": "LLC registered", "xp": 150, "badge": "📋 Official"},
            {"title": "First sale made", "xp": 400, "badge": "💵 First Dollar"},
            {"title": "$1,000/month revenue", "xp": 800, "badge": "🚀 Business Owner"},
        ]
    },

    # ── HEALTH GOALS ─────────────────────────────────────────
    "lose_weight": {
        "category": "health",
        "title": "Lose 20 pounds in 4 months",
        "icon": "⚖️",
        "description": "Healthy weight loss through diet and exercise",
        "roadmap": [
            "Track calories for 2 weeks to understand baseline",
            "Create a 500 calorie/day deficit",
            "Add 3 workouts per week minimum",
            "Remove one bad food habit per week",
            "Weigh in every Monday, adjust as needed",
        ],
        "quests": [
            {"title": "Track everything you eat today", "description": "Use MyFitnessPal or Cronometer. No judgment, just awareness.", "xp": 50, "difficulty": "easy"},
            {"title": "Calculate your daily calorie target", "description": "TDEE minus 500 = your target. Free calculators online.", "xp": 30, "difficulty": "easy", "url": "https://tdeecalculator.net"},
            {"title": "Complete a 30-minute workout", "description": "Walk, run, lift, swim — anything. 30 min counts.", "xp": 80, "difficulty": "medium"},
            {"title": "Cook all meals at home for 3 days", "description": "Restaurant food makes tracking nearly impossible. 3 days home cooking.", "xp": 100, "difficulty": "medium"},
            {"title": "Hit 10,000 steps today", "description": "Most people walk 3,000-4,000 steps/day. Double it.", "xp": 70, "difficulty": "medium"},
            {"title": "Drink only water for one week", "description": "Cut soda, juice, alcohol. Just water and black coffee/tea.", "xp": 120, "difficulty": "hard"},
            {"title": "Complete 5 workouts in one week", "description": "5 days of movement in 7 days. Builds the habit fast.", "xp": 150, "difficulty": "hard"},
            {"title": "Take progress photos", "description": "Front and side view. Weekly. You'll notice what the scale misses.", "xp": 40, "difficulty": "easy"},
            {"title": "Prep meals for 5 days", "description": "One Sunday session. 5 days of meals ready. No excuses.", "xp": 120, "difficulty": "hard"},
            {"title": "Get 7+ hours sleep 5 days in a row", "description": "Sleep deprivation causes weight gain. This is part of the plan.", "xp": 100, "difficulty": "medium"},
        ],
        "milestones": [
            {"title": "First 5 pounds lost", "xp": 200, "badge": "⚖️ Moving"},
            {"title": "30-day streak of tracking", "xp": 300, "badge": "📊 Consistent"},
            {"title": "10 pounds lost", "xp": 400, "badge": "💪 Halfway"},
            {"title": "Goal weight reached", "xp": 800, "badge": "🏆 Transformed"},
        ]
    },

    "build_gym_habit": {
        "category": "health",
        "title": "Work out consistently 4x per week",
        "icon": "🏋️",
        "description": "Build a sustainable exercise habit",
        "roadmap": [
            "Start with 2x/week for first 2 weeks",
            "Add third day in week 3",
            "Add fourth day in week 5",
            "Never miss twice in a row",
            "Log every session to track progress",
        ],
        "quests": [
            {"title": "Join a gym or plan home workout space", "description": "Planet Fitness is $10/month. Or clear space at home. Remove friction.", "xp": 60, "difficulty": "easy"},
            {"title": "Complete workout #1", "description": "Anything counts. 20 min walk, 15 min lifts. Just show up.", "xp": 80, "difficulty": "medium"},
            {"title": "Log your workout", "description": "Notes app, Strong app, or paper. Date, exercises, sets, reps. Takes 2 min.", "xp": 30, "difficulty": "easy"},
            {"title": "Complete your first full week (2 workouts)", "description": "Two sessions in 7 days. That's it. First goal.", "xp": 120, "difficulty": "medium"},
            {"title": "Pack your gym bag the night before", "description": "Reduce friction. Bag is packed, clothes are out. No excuses in the morning.", "xp": 40, "difficulty": "easy"},
            {"title": "Complete first month (8+ workouts)", "description": "8 workouts in 30 days. Habit research says this is when it starts to stick.", "xp": 200, "difficulty": "hard"},
            {"title": "Find a workout partner", "description": "Accountability doubles consistency. One friend who goes with you.", "xp": 100, "difficulty": "medium"},
            {"title": "Learn 5 compound movements", "description": "Squat, deadlift, bench, pull-up, row. The foundation of everything.", "xp": 80, "difficulty": "medium"},
        ],
        "milestones": [
            {"title": "First workout completed", "xp": 100, "badge": "🎬 Day One"},
            {"title": "First week (2+ workouts)", "xp": 150, "badge": "🔥 Started"},
            {"title": "30-day streak maintained", "xp": 400, "badge": "💪 Habit Forming"},
            {"title": "90 days consistent", "xp": 800, "badge": "⚡ Lifestyle Change"},
        ]
    },

    "reduce_screen_time": {
        "category": "health",
        "title": "Reduce screen time to under 3 hours/day",
        "icon": "📵",
        "description": "Reclaim your time from social media and apps",
        "roadmap": [
            "Audit current screen time (check phone settings)",
            "Delete the 2-3 worst offenders",
            "Set app limits for remaining apps",
            "Replace screen time with one physical activity",
            "Maintain under 3 hours for 30 consecutive days",
        ],
        "quests": [
            {"title": "Check your screen time right now", "description": "Settings → Screen Time (iPhone) or Digital Wellbeing (Android). What's the real number?", "xp": 30, "difficulty": "easy"},
            {"title": "Delete Instagram for one week", "description": "Just one week. See how you feel. You can reinstall. Or you won't want to.", "xp": 100, "difficulty": "hard"},
            {"title": "Turn off all social media notifications", "description": "Every platform. No more pull. You check on your terms, not theirs.", "xp": 60, "difficulty": "easy"},
            {"title": "Set app limits (1 hour social media max)", "description": "iPhone Screen Time or Android Digital Wellbeing. Hard limits.", "xp": 70, "difficulty": "medium"},
            {"title": "Phone-free morning for one week", "description": "No phone for first 30 min after waking. Every day for 7 days.", "xp": 120, "difficulty": "hard"},
            {"title": "Replace one hour of scrolling with something real", "description": "Walk, read, cook, work out. Any single replacement activity.", "xp": 100, "difficulty": "medium"},
            {"title": "Complete a full day under 2 hours", "description": "One complete day. Proves it's possible.", "xp": 150, "difficulty": "hard"},
            {"title": "7-day streak under 3 hours", "description": "Seven consecutive days. New baseline established.", "xp": 200, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "First day under 3 hours", "xp": 150, "badge": "📵 First Win"},
            {"title": "7-day streak under 3 hours", "xp": 300, "badge": "⏰ Time Reclaimed"},
            {"title": "30-day streak", "xp": 600, "badge": "🧠 Mind Clear"},
            {"title": "Instagram deleted permanently", "xp": 400, "badge": "🔥 Free"},
        ]
    },

    "improve_sleep": {
        "category": "health",
        "title": "Get consistent 7-8 hours of sleep",
        "icon": "😴",
        "description": "Fix your sleep schedule for energy and performance",
        "roadmap": [
            "Set a consistent bedtime and wake time",
            "No screens 1 hour before bed",
            "Make your room dark and cool",
            "No caffeine after 2pm",
            "Track sleep quality weekly",
        ],
        "quests": [
            {"title": "Set a consistent bedtime", "description": "Same time every night, including weekends. Pick a time and commit.", "xp": 40, "difficulty": "easy"},
            {"title": "Make your room completely dark", "description": "Blackout curtains or eye mask. Light is the enemy of deep sleep.", "xp": 50, "difficulty": "easy"},
            {"title": "No phone 30 min before bed for 7 days", "description": "Hardest one. Do it anyway. Your sleep quality will noticeably improve.", "xp": 120, "difficulty": "hard"},
            {"title": "Cut caffeine after 2pm for one week", "description": "Caffeine has a 6-hour half-life. 3pm coffee = half-dose at 9pm.", "xp": 100, "difficulty": "medium"},
            {"title": "Track your sleep for 7 days", "description": "Galaxy Watch, phone sleep tracker, or just log bedtime and wake time.", "xp": 60, "difficulty": "easy"},
            {"title": "Get 8 hours for 5 consecutive nights", "description": "Not just in bed — actual sleep. Track it.", "xp": 150, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "First night of 8 hours", "xp": 100, "badge": "💤 First Full Night"},
            {"title": "7-day streak of 7+ hours", "xp": 300, "badge": "😴 Consistent"},
            {"title": "30-day streak", "xp": 600, "badge": "⚡ Energy Restored"},
        ]
    },

    # ── EDUCATION GOALS ──────────────────────────────────────
    "complete_degree": {
        "category": "education",
        "title": "Complete your degree",
        "icon": "🎓",
        "description": "Finish your current degree program",
        "roadmap": [
            "Map out remaining courses and credits needed",
            "Create a semester-by-semester completion plan",
            "Connect with your academic advisor",
            "Identify any courses you can take simultaneously",
            "Graduate",
        ],
        "quests": [
            {"title": "Meet with your academic advisor", "description": "Know exactly what you need to graduate. No guessing.", "xp": 60, "difficulty": "easy"},
            {"title": "Map remaining courses on paper", "description": "Visual layout of what's left. Makes it feel manageable.", "xp": 50, "difficulty": "easy"},
            {"title": "Complete this week's assignments early", "description": "Not the night before. Done 2 days early.", "xp": 80, "difficulty": "medium"},
            {"title": "Attend every class this week", "description": "Sounds obvious. Attendance alone correlates strongly with grades.", "xp": 60, "difficulty": "easy"},
            {"title": "Find one study partner", "description": "Accountability + collaboration. One person in your program.", "xp": 80, "difficulty": "medium"},
            {"title": "Complete one module or unit ahead of schedule", "description": "Get ahead. The cushion reduces stress.", "xp": 100, "difficulty": "medium"},
            {"title": "Apply to graduate", "description": "Actually submit the graduation application. Don't assume it's automatic.", "xp": 80, "difficulty": "easy"},
        ],
        "milestones": [
            {"title": "First semester completed", "xp": 200, "badge": "📚 Progressing"},
            {"title": "50% complete", "xp": 400, "badge": "🏃 Halfway"},
            {"title": "Final semester started", "xp": 500, "badge": "🔜 Almost There"},
            {"title": "Graduated", "xp": 1000, "badge": "🎓 Graduate"},
        ]
    },

    "learn_new_skill": {
        "category": "education",
        "title": "Learn a new skill in 90 days",
        "icon": "🧠",
        "description": "Master a specific skill through deliberate practice",
        "roadmap": [
            "Define the skill specifically (not 'learn coding' but 'build a web app')",
            "Find the best free resource for that skill",
            "Practice 30 min/day minimum",
            "Build one real project using the skill",
            "Teach someone else what you learned",
        ],
        "quests": [
            {"title": "Define your specific skill goal", "description": "Not 'learn data science' — 'complete Google Data Analytics certificate by June 1'.", "xp": 30, "difficulty": "easy"},
            {"title": "Find the best free learning resource", "description": "YouTube, Coursera, Khan Academy, freeCodeCamp. 30 min of research.", "xp": 40, "difficulty": "easy"},
            {"title": "Complete day 1 of your course", "description": "Start. Today. The first session is the most important.", "xp": 80, "difficulty": "medium"},
            {"title": "Complete first full week (5 sessions)", "description": "5 days of 30-min sessions. Proof you'll stick with it.", "xp": 150, "difficulty": "hard"},
            {"title": "Build a small practice project", "description": "Apply what you've learned to something real. Even tiny.", "xp": 200, "difficulty": "hard"},
            {"title": "Explain what you've learned to someone", "description": "Teaching reveals gaps. Use the Feynman technique.", "xp": 100, "difficulty": "medium"},
        ],
        "milestones": [
            {"title": "First week completed", "xp": 150, "badge": "🌱 Started"},
            {"title": "30 days consistent", "xp": 300, "badge": "📈 Building"},
            {"title": "First real project built", "xp": 400, "badge": "🔨 Applied"},
            {"title": "Skill complete", "xp": 700, "badge": "🧠 Mastered"},
        ]
    },

    # ── LIFE GOALS ───────────────────────────────────────────
    "build_better_habits": {
        "category": "life",
        "title": "Build 3 core daily habits",
        "icon": "⚡",
        "description": "Create a sustainable morning/daily routine",
        "roadmap": [
            "Pick only 3 habits to focus on (not 10)",
            "Anchor each habit to an existing trigger",
            "Start stupidly small (2-min version)",
            "Track daily for 30 days",
            "Scale up after the habit is automatic",
        ],
        "quests": [
            {"title": "Pick your 3 core habits", "description": "Just 3. Not 10. What would change your life most? Exercise, reading, journaling?", "xp": 30, "difficulty": "easy"},
            {"title": "Start with 2-minute versions", "description": "1 pushup. Read 1 page. Write 1 sentence. Tiny is the point.", "xp": 40, "difficulty": "easy"},
            {"title": "Complete all 3 habits today", "description": "Day 1. However small. Just do them.", "xp": 80, "difficulty": "medium"},
            {"title": "Set up a habit tracker", "description": "Paper, app, or calendar. Visual streak creates accountability.", "xp": 40, "difficulty": "easy"},
            {"title": "Complete a 7-day streak", "description": "Seven consecutive days. All 3 habits. Every day.", "xp": 200, "difficulty": "hard"},
            {"title": "Scale one habit up", "description": "After 2 weeks of 1 pushup, make it 5. Tiny growth compounds.", "xp": 100, "difficulty": "medium"},
            {"title": "Complete a 30-day streak", "description": "This is where habits become identity. 30 days, all 3.", "xp": 400, "difficulty": "hard"},
        ],
        "milestones": [
            {"title": "3 habits defined", "xp": 50, "badge": "🎯 Clear Target"},
            {"title": "7-day streak", "xp": 200, "badge": "🔥 Streak"},
            {"title": "30-day streak", "xp": 500, "badge": "⚡ Identity Shift"},
            {"title": "90-day streak", "xp": 1000, "badge": "💎 Lifestyle"},
        ]
    },

    "find_relationship": {
        "category": "life",
        "title": "Build meaningful relationships",
        "icon": "🤝",
        "description": "Expand and deepen your social connections",
        "roadmap": [
            "Identify what kind of connections you want",
            "Put yourself in places where those people are",
            "Initiate 3 conversations per week",
            "Follow up within 48 hours",
            "Invest in existing relationships first",
        ],
        "quests": [
            {"title": "Reach out to 3 people you've lost touch with", "description": "A genuine 'hey, how are you?' Text or call. This week.", "xp": 80, "difficulty": "medium"},
            {"title": "Attend one social event you'd normally skip", "description": "The event you said no to. Go. Stay for 1 hour minimum.", "xp": 100, "difficulty": "hard"},
            {"title": "Have a meal with someone new", "description": "Lunch or dinner with someone you want to know better.", "xp": 120, "difficulty": "medium"},
            {"title": "Join one club, class, or recurring event", "description": "Book club, gym class, sports league, church group. Something that repeats.", "xp": 150, "difficulty": "hard"},
            {"title": "Ask someone meaningful questions", "description": "Not small talk. Ask about their goals, their story, what they care about.", "xp": 80, "difficulty": "medium"},
        ],
        "milestones": [
            {"title": "First new connection made", "xp": 100, "badge": "🤝 Connected"},
            {"title": "First recurring social commitment", "xp": 200, "badge": "🔄 Consistent"},
            {"title": "Meaningful friendship deepened", "xp": 400, "badge": "💙 Depth"},
        ]
    },

}


def push_template_to_supabase(goal_key, template):
    """Push a single goal template to Supabase."""

    # Push the main goal template
    goal_payload = {
        "goal_key": goal_key,
        "category": template["category"],
        "title": template["title"],
        "icon": template["icon"],
        "description": template["description"],
        "roadmap": json.dumps(template["roadmap"]),
        "milestones": json.dumps(template["milestones"]),
    }

    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/goal_templates",
        headers=SB_HEADERS,
        json=goal_payload,
        timeout=15
    )

    if resp.status_code not in (200, 201):
        print(f"  ⚠ Goal template error for {goal_key}: {resp.text[:100]}")
        return False

    # Push quests for this template
    for quest in template.get("quests", []):
        quest_payload = {
            "goal_key": goal_key,
            "category": template["category"],
            "title": quest["title"],
            "description": quest["description"],
            "xp_reward": quest["xp"],
            "difficulty": quest.get("difficulty", "medium"),
            "resource_url": quest.get("url", ""),
        }
        qresp = requests.post(
            f"{SUPABASE_URL}/rest/v1/quest_templates",
            headers=SB_HEADERS,
            json=quest_payload,
            timeout=15
        )
        if qresp.status_code not in (200, 201):
            print(f"    ⚠ Quest template error: {quest['title'][:30]}: {qresp.text[:80]}")

    return True


def main():
    print("\n" + "="*52)
    print("HJ QUEST — GOAL TEMPLATE GENERATOR")
    print(f"Pushing {len(GOAL_TEMPLATES)} goal templates to Supabase")
    print("="*52 + "\n")

    success = 0
    for key, template in GOAL_TEMPLATES.items():
        print(f"  Pushing: {template['icon']} {template['title']}...")
        if push_template_to_supabase(key, template):
            quest_count = len(template.get("quests", []))
            milestone_count = len(template.get("milestones", []))
            print(f"    ✓ {quest_count} quests + {milestone_count} milestones")
            success += 1
        time.sleep(0.2)

    print(f"\n✓ Done — {success}/{len(GOAL_TEMPLATES)} templates pushed")
    print("Your app can now pull quests from the database instead of the API.")
    print("="*52 + "\n")


if __name__ == "__main__":
    main()
