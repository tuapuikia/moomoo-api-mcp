---
name: moomoo-news-trader
description: Automated news-based trading using web research and Moomoo MCP tools. Use when you need to analyze market news, perform sentiment analysis on specific stocks, and execute trades based on news events.
---

# Moomoo News Trader Skill

This skill provides a complete workflow for researching, analyzing, and executing trades based on the latest market news and social sentiment.

## Core Workflow

### 0. Session Initialization (MANDATORY)
Before any trading begins, the agent MUST ask the user to define the session's trading limits:
- **Max Session Budget:** The maximum total amount to be deployed in this session.
- **Daily Loss Limit:** The maximum loss (drawdown) allowed before the agent stops trading for the day.
- **Max Position Size:** The maximum amount allowed for a single ticker.

**MANDATORY GUARDRAIL:** Do NOT propose or execute any trades until these limits are explicitly confirmed by the user.

### 1. Market Research (Web Researcher)
Use the `web researcher` skill (or search tools like `google_web_search`) to find the latest news for a specific stock ticker (e.g., "NVDA news", "TSLA sentiment reddit").
- **Timeframe:** Focus on the last 24-48 hours.
- **Sources:** Prioritize official press releases, major financial news (Bloomberg, Reuters, CNBC), and high-signal social sentiment (Reddit/X for retail trends).

### 2. Sentiment Analysis
Analyze the gathered information for:
- **Positive Catalysts:** Strong earnings (beat & raise), product launches, strategic partnerships, analyst upgrades, or bullish macro trends (rate cuts).
- **Negative Catalysts:** Earnings misses, lawsuits, product delays, analyst downgrades, or bearish macro trends.
- **Neutral:** No significant change or mixed signals.

Refer to [SENTIMENT.md](references/sentiment_criteria.md) for detailed evaluation criteria.

### 3. Market Context (Moomoo MCP)
Before proposing a trade, check the current state:
- **Quote:** Call `get_stock_quote` for the latest price and volume.
- **Account:** Call `get_account_summary` (default REAL) or `get_assets` (trd_env='SIMULATE') to verify buying power and existing positions.

### 4. Trade Proposal & Execution
Generate a 'Trade Proposal' for the user including:
- **Ticker & Action:** (e.g., "BUY 10 shares of NVDA")
- **Rationale:** A concise summary of the news catalyst and price context.
- **Environment:** Clearly state if it's REAL or SIMULATE.

**CRITICAL SAFETY MANDATE:**
- For **REAL** accounts: **NEVER** execute a trade without explicit user confirmation.
- For **SIMULATE** accounts: You may execute automatically if the user has provided a "continuous auto-trade" directive for the session.
- **Unlock:** Call `unlock_trade` before any real account trade. It handles env vars automatically.

## Standard Commands

### /news-trade <ticker>
Executes the full research -> analysis -> proposal workflow for a single ticker.

### /news-monitor <tickers...>
Performs a batch scan of multiple tickers and only proposes trades for those with high-signal news.

## Best Practices
- **Parallel Research:** Search for multiple tickers simultaneously to reduce latency.
- **Volume Check:** Verify current trading volume before proposing a trade to ensure liquidity.
- **Risk Management:** Do not propose trades that exceed 5% of the total account market value unless specifically directed.
