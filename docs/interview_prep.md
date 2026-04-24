# ShareChat Product Analyst Internship — Interview Preparation Guide

---

## 1. About the Company (Know This Cold)

| Fact | Detail |
|---|---|
| Founded | 2015 |
| Full name | Mohalla Tech Pvt Ltd |
| Platforms | ShareChat (social), Moj (short video), QuickTV (micro drama) |
| Languages | 15 regional languages |
| ARR | ₹1,000 Crore (~$120M USD) |
| MMU | 200M+ Monthly Monetizable Users |
| Revenue Growth | 28% YoY (July–Sept quarter); 60%+ QoQ (Oct–Dec quarter) |
| QuickTV | 10M downloads in 3 months of launch; 60M MAU across the network |
| Profitability | Only Indian social media company to achieve profitability |
| Differentiation | Only major social platform serving non-English Indian users at scale |

**Why ShareChat matters:** India has ~600M internet users; only ~150M are comfortable consuming English content. ShareChat owns the other 450M — the "Bharat" internet user.

---

## 2. This Project — What to Say to the Hiring Manager

> "I built a full-stack analytics platform simulating how a Product Analyst at ShareChat might approach daily work. It pulls together user behaviour, content performance, monetisation, and retention into one interactive dashboard — the kind of view I'd want before every weekly product review meeting."

### What the project demonstrates
1. **SQL fluency** — 11 queries covering retention cohorts, RFM segmentation, funnel analysis, revenue attribution, and feed quality scoring, all written for Redshift.
2. **Metric design** — Every KPI card has a label, value, delta, and context note. You understand the *why* behind each number (e.g., DAU/MAU as a stickiness proxy, eCPM as pricing health).
3. **Product thinking** — The Insight boxes on each page aren't just summaries; they connect data points to business decisions.
4. **Technical execution** — Python, Streamlit, Plotly, NumPy/Pandas, and enough synthetic data modelling to make all charts realistic and internally consistent.
5. **Brand awareness** — ShareChat orange, dark-navy sidebar, Inter typeface, and Indian-market framing (₹ throughout, 15 regional languages, Indian regions).

---

## 3. Key Metrics You Must Know

### User Metrics
| Metric | Formula | ShareChat Target |
|---|---|---|
| MAU | Unique users active in a 30-day window | 200M MMU |
| DAU | Unique users active in a single day | ~90–100M |
| DAU/MAU (Stickiness) | DAU ÷ MAU | >45% (excellent) |
| Session Duration | Average minutes per session per user | 18–22 min |
| Sessions per User | Monthly sessions ÷ active users | 40–60 |

### Content Metrics
| Metric | Formula | Why It Matters |
|---|---|---|
| Engagement Rate | (Likes+Shares+Comments) ÷ Views | Measures content resonance |
| Watch-Through Rate | Avg watch time ÷ content duration | Feed quality signal |
| Virality Score | Share velocity in first 6h | Predicts organic reach |
| Content per User | Posts consumed per session | Habit depth indicator |

### Monetisation Metrics
| Metric | Formula | Typical India Range |
|---|---|---|
| eCPM | Revenue ÷ Impressions × 1000 | ₹60–₹120 |
| ARPU | Monthly Revenue ÷ MAU | ₹4–₹8 for social apps |
| Fill Rate | Filled ad requests ÷ Total ad requests | >80% is good |
| CTR | Clicks ÷ Impressions | 0.3–1.2% for social |

### Retention Metrics
| Metric | Definition | Industry Benchmark |
|---|---|---|
| D1 Retention | % of users returning on Day 1 | 25–40% |
| D7 Retention | % of users returning on Day 7 | 15–25% |
| D30 Retention | % of users returning on Day 30 | 10–20% |
| M1 Retention | % of cohort active in Month 1 | 30–50% |

---

## 4. Common Interview Questions & Model Answers

### Analytical / SQL

**Q: How would you measure if a new content recommendation algorithm is performing better?**

> A: I'd run an A/B test and track: (1) Watch-Through Rate — are users watching more of each video? (2) DAU/MAU ratio — is daily engagement improving? (3) D7/D30 retention — are new users sticking around longer? (4) Skip rate — how often users scroll past recommended content. I'd also check eCPM since better-targeted content should attract higher-value ads. In Redshift, I'd use a CTE to split control and treatment users, compute these metrics per group per day, and test significance with a two-proportion z-test after the experiment reaches 80% power.

---

**Q: Write a SQL query to find users who were active last month but not this month.**

```sql
SELECT DISTINCT last_month.user_id
FROM (
    SELECT DISTINCT user_id
    FROM user_sessions
    WHERE session_start_ts >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
      AND session_start_ts <  DATE_TRUNC('month', CURRENT_DATE)
) AS last_month
LEFT JOIN (
    SELECT DISTINCT user_id
    FROM user_sessions
    WHERE session_start_ts >= DATE_TRUNC('month', CURRENT_DATE)
      AND session_start_ts <  CURRENT_DATE
) AS this_month
  ON last_month.user_id = this_month.user_id
WHERE this_month.user_id IS NULL;
```

> These are your "at-risk" users. I'd then segment them by language, platform, and last content type to design a re-engagement campaign.

---

**Q: How would you find the top-performing language market for ShareChat?**

> I'd define "top-performing" along three dimensions: (1) Revenue per user (ARPU), (2) Engagement rate, and (3) Retention. A language with high engagement but low revenue is an untapped monetisation opportunity. A language with high revenue but low retention is at risk. I'd build a 2×2 matrix — Revenue vs Retention — and flag each language as: Invest, Monetise, Protect, or Harvest. See Query #9 in the SQL file for the full implementation.

---

**Q: QuickTV grew 60% QoQ in one quarter. How would you validate whether that growth is real?**

> I'd check for: (1) Bot/fraud activity — sudden spikes in low-tenure accounts with no engagement, (2) Acquisition channel mix — heavy paid-UA can inflate MAU cheaply, (3) Retention quality — if D7 retention dropped while MAU spiked, the new users aren't sticky, (4) Engagement depth — are these users actually watching drama episodes, or just opening the app once? Real growth shows up in all four; inflated growth usually fails 2-3 of these checks.

---

### Product Thinking

**Q: ShareChat's DAU/MAU drops for one week. Walk me through your investigation.**

> **Step 1 — Isolate**: Is it all platforms or one? All regions or one geography? All age groups or a cohort? Drill down systematically to find the smallest affected segment.
> **Step 2 — Timing**: Did it correlate with a release, a content moderation policy change, a server incident, or an external event (exam season, festival)?
> **Step 3 — Leading indicators**: Check notification CTR (if users aren't opening notifications, something changed in content relevance), session starts vs. session length (are users opening the app but leaving faster?).
> **Step 4 — Resolution**: If it's product-driven, revert or patch. If it's seasonal (e.g., exam season in North India every March-April), model for it and plan content campaigns to offset.

---

**Q: How would you improve user retention for a regional language market like Bhojpuri?**

> Bhojpuri users are often first-time smartphone internet users. Retention levers specific to this segment: (1) **Onboarding** — voice-guided onboarding in Bhojpuri (low literacy), (2) **Content seeding** — curate a 10-video playlist on signup based on declared interests, (3) **Creator growth** — even 50 high-quality Bhojpuri creators dramatically expands content supply, (4) **Notification personalisation** — send notifications at times correlated with historical session starts for this segment. I'd measure each lever's impact on D7 and D30 retention using holdout groups.

---

**Q: How would you prioritise which of ShareChat's 15 languages to invest in next?**

> I'd use a prioritisation framework with four factors:
> 1. **Market Size**: Total speakers in India who are smartphone internet users
> 2. **Current Penetration**: ShareChat MAU ÷ addressable market
> 3. **Monetisation Potential**: eCPM × expected MAU (revenue ceiling)
> 4. **Content Supply**: Existing creator count (limits growth without investment)
>
> Score each language 1–5 on these four axes. Languages with high market size, low penetration, and decent monetisation are the best investment (e.g., Odia or Assamese). Use the market map chart in the dashboard to visualise this.

---

### Behavioural

**Q: Tell me about a time you found an unexpected insight in data.**

> *(Tailor to your experience, but structure it as):* "I noticed [anomaly]. My initial hypothesis was [X], but when I sliced the data by [dimension], I found [unexpected pattern]. This turned out to be caused by [root cause], which led to [business action]. The outcome was [measurable result]."

**Q: How do you deal with incomplete or messy data?**

> My approach: (1) Quantify the missingness — is it random or systematic? Systematic missingness is dangerous (e.g., iOS users don't return session data on older SDK versions). (2) Document assumptions — never silently impute. (3) Validate conclusions on multiple data sources — if the Redshift aggregation matches the raw event log, I'm more confident. (4) Report uncertainty — present confidence intervals or "this finding holds if missingness < X%."

---

## 5. ShareChat-Specific Knowledge Cheat Sheet

**Why regional language social media is hard:**
- Unicode rendering across 15 scripts (Devanagari, Telugu, Tamil, Bengali…)
- Content moderation at scale in languages with little NLP tooling
- Creator economy is nascent — fewer professional creators, more user-generated
- Ad targeting is harder (fewer third-party data signals for Indian language users)

**ShareChat's moat:**
- First-mover advantage in vernacular social (2015)
- Network effects are language-specific — Telugu users follow Telugu creators
- Distribution deals with Jio and telecom operators for data-light mode
- Own ad network (not dependent on Google/Meta for monetisation)

**Risks to know:**
- Meta (Instagram Reels) and YouTube Shorts compete directly with Moj
- Content moderation at scale is an ongoing challenge (IT Rules 2021)
- Monetisation in tier-2/tier-3 cities has lower purchasing power → lower CPMs

**QuickTV insight:**
- Micro-drama is a format proven in China (Kuaishou, Douyin) — ShareChat is localising it
- 5–10 minute vertical episodes are highly bingeable — drives long sessions
- Premium content potential: users in India will pay for drama if it's high-quality

---

## 6. Dashboard Walkthrough Script (2 minutes)

> "Let me walk you through the platform. On the Overview page, you can see the network's 200M MMU and ₹1,000 Cr ARR — the stacked area chart breaks revenue down by platform, and you can see QuickTV's revenue growing rapidly in absolute terms despite being the youngest platform.
>
> Moving to User Analytics — the dashboard shows 15 regional languages with engagement and MAU breakdowns. Notice that Hindi is 38% of users but some smaller languages like Bhojpuri punch above their weight in engagement rate — a signal for creator investment.
>
> Content Performance shows that Drama Episodes have the highest engagement rate at around 12%, which aligns with QuickTV's rapid growth. The scatter plot maps categories by views and engagement — Entertainment and Comedy dominate reach, while Devotional content has disproportionately high engagement for its size.
>
> On Monetisation, I've built a waterfall chart showing QoQ revenue growth by platform, plus eCPM trends by ad format. In-Feed Video is the biggest revenue driver, and its eCPM is rising as advertiser demand catches up with inventory growth.
>
> Finally, the Retention page has a cohort heatmap — April 2025 cohorts (top row) have the most data, and you can see M1 retention around 48%, well above the industry average of 30-35%. The DAU/MAU trend line stays above 40%, confirming healthy daily engagement habits."

---

## 7. Questions to Ask the Interviewer

1. "What does a typical week look like for a Product Analyst intern — how much is dashboarding vs. ad hoc analysis vs. A/B test design?"
2. "Which language markets are you most focused on growing this year, and why?"
3. "How does the team decide which metrics to track for a new feature like QuickTV?"
4. "What's the biggest data quality challenge you face with Redshift at ShareChat's scale?"
5. "What would make this internship convert to a full-time role?"

---

## 8. Technical Stack to Be Comfortable With

| Tool | What to Know |
|---|---|
| **SQL / Redshift** | CTEs, window functions, DATE_TRUNC, DATEDIFF, NTILE, NULLIF |
| **Python** | pandas (groupby, merge, melt, pivot), numpy, basic stats |
| **Excel / Sheets** | Pivot tables, VLOOKUP, basic charting |
| **Dashboarding** | Streamlit, Tableau, Metabase, or Looker (know at least one) |
| **Statistics** | A/B testing, statistical significance, p-values, confidence intervals |
| **Git** | Basic version control for sharing scripts |

---

*Good luck — you've got this. The dashboard demonstrates everything they're hiring for: curiosity about data, technical execution, and the ability to tell a coherent product story.*
