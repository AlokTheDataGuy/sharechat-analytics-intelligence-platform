-- ============================================================
-- SHARECHAT ANALYTICS — SQL ANALYSIS QUERIES
-- Engine: Amazon Redshift (PostgreSQL-compatible)
-- Author: Product Analyst Internship Project
-- ============================================================


-- ─────────────────────────────────────────────────────────────
-- 1. DAILY ACTIVE USERS (DAU) & DAU/MAU RATIO
-- ─────────────────────────────────────────────────────────────
WITH daily_active AS (
    SELECT
        DATE(session_start_ts)          AS activity_date,
        platform,
        COUNT(DISTINCT user_id)         AS dau
    FROM user_sessions
    WHERE session_start_ts >= DATEADD(day, -90, CURRENT_DATE)
    GROUP BY 1, 2
),
monthly_active AS (
    SELECT
        DATE_TRUNC('month', session_start_ts)   AS activity_month,
        platform,
        COUNT(DISTINCT user_id)                 AS mau
    FROM user_sessions
    WHERE session_start_ts >= DATEADD(day, -90, CURRENT_DATE)
    GROUP BY 1, 2
)
SELECT
    d.activity_date,
    d.platform,
    d.dau,
    m.mau,
    ROUND(d.dau::FLOAT / NULLIF(m.mau, 0) * 100, 2) AS dau_mau_ratio_pct
FROM daily_active d
JOIN monthly_active m
    ON d.platform = m.platform
    AND DATE_TRUNC('month', d.activity_date) = m.activity_month
ORDER BY d.activity_date, d.platform;


-- ─────────────────────────────────────────────────────────────
-- 2. MONTHLY COHORT RETENTION MATRIX
-- ─────────────────────────────────────────────────────────────
WITH cohort_base AS (
    SELECT
        user_id,
        DATE_TRUNC('month', signup_date)    AS cohort_month
    FROM users
    WHERE signup_date >= '2025-01-01'
),
user_activity AS (
    SELECT
        s.user_id,
        DATE_TRUNC('month', s.session_start_ts) AS activity_month
    FROM user_sessions s
    JOIN cohort_base c ON s.user_id = c.user_id
    GROUP BY 1, 2
),
cohort_activity AS (
    SELECT
        c.cohort_month,
        DATEDIFF('month', c.cohort_month, ua.activity_month) AS month_number,
        COUNT(DISTINCT ua.user_id)          AS retained_users
    FROM user_activity ua
    JOIN cohort_base c ON ua.user_id = c.user_id
    GROUP BY 1, 2
),
cohort_size AS (
    SELECT cohort_month, COUNT(DISTINCT user_id) AS cohort_users
    FROM cohort_base
    GROUP BY 1
)
SELECT
    TO_CHAR(ca.cohort_month, 'Mon YYYY')    AS cohort,
    cs.cohort_users,
    ca.month_number,
    ca.retained_users,
    ROUND(ca.retained_users::FLOAT / cs.cohort_users * 100, 2) AS retention_pct
FROM cohort_activity ca
JOIN cohort_size cs ON ca.cohort_month = cs.cohort_month
WHERE ca.month_number BETWEEN 0 AND 12
ORDER BY ca.cohort_month, ca.month_number;


-- ─────────────────────────────────────────────────────────────
-- 3. CONTENT ENGAGEMENT FUNNEL ANALYSIS
-- ─────────────────────────────────────────────────────────────
WITH content_funnel AS (
    SELECT
        c.content_type,
        c.language,
        c.platform,
        COUNT(DISTINCT e.user_id)               AS reached_users,     -- saw content
        COUNT(DISTINCT CASE WHEN e.watch_pct >= 0.25 THEN e.user_id END) AS watched_25pct,
        COUNT(DISTINCT CASE WHEN e.watch_pct >= 0.50 THEN e.user_id END) AS watched_50pct,
        COUNT(DISTINCT CASE WHEN e.watch_pct >= 0.75 THEN e.user_id END) AS watched_75pct,
        COUNT(DISTINCT CASE WHEN e.liked = TRUE  THEN e.user_id END)    AS liked,
        COUNT(DISTINCT CASE WHEN e.shared = TRUE THEN e.user_id END)    AS shared,
        COUNT(DISTINCT CASE WHEN e.commented = TRUE THEN e.user_id END) AS commented
    FROM content c
    JOIN content_engagement e ON c.content_id = e.content_id
    WHERE c.upload_date >= DATEADD(day, -30, CURRENT_DATE)
    GROUP BY 1, 2, 3
)
SELECT
    content_type,
    language,
    platform,
    reached_users,
    ROUND(watched_25pct::FLOAT / NULLIF(reached_users,0) * 100, 2) AS watch_25pct_rate,
    ROUND(watched_50pct::FLOAT / NULLIF(reached_users,0) * 100, 2) AS watch_50pct_rate,
    ROUND(watched_75pct::FLOAT / NULLIF(reached_users,0) * 100, 2) AS watch_75pct_rate,
    ROUND(liked::FLOAT          / NULLIF(reached_users,0) * 100, 2) AS like_rate,
    ROUND(shared::FLOAT         / NULLIF(reached_users,0) * 100, 2) AS share_rate,
    ROUND(commented::FLOAT      / NULLIF(reached_users,0) * 100, 2) AS comment_rate
FROM content_funnel
ORDER BY reached_users DESC;


-- ─────────────────────────────────────────────────────────────
-- 4. MONTHLY REVENUE TREND WITH YoY COMPARISON
-- ─────────────────────────────────────────────────────────────
WITH monthly_revenue AS (
    SELECT
        DATE_TRUNC('month', revenue_date)   AS rev_month,
        platform,
        ad_format,
        SUM(revenue_inr) / 1e7             AS revenue_cr,   -- convert paise → crore
        SUM(impressions)                    AS total_impressions,
        SUM(clicks)                         AS total_clicks,
        ROUND(SUM(revenue_inr) / NULLIF(SUM(impressions), 0) * 1000, 2) AS ecpm
    FROM ad_revenue
    GROUP BY 1, 2, 3
)
SELECT
    curr.rev_month,
    curr.platform,
    curr.ad_format,
    curr.revenue_cr,
    prev.revenue_cr                                         AS revenue_cr_yoy,
    ROUND((curr.revenue_cr - prev.revenue_cr)
          / NULLIF(prev.revenue_cr, 0) * 100, 2)           AS yoy_growth_pct,
    curr.ecpm,
    curr.total_impressions,
    ROUND(curr.total_clicks::FLOAT / NULLIF(curr.total_impressions,0) * 100, 3) AS ctr_pct
FROM monthly_revenue curr
LEFT JOIN monthly_revenue prev
    ON curr.platform   = prev.platform
    AND curr.ad_format = prev.ad_format
    AND curr.rev_month = DATEADD(year, 1, prev.rev_month)
ORDER BY curr.rev_month DESC, curr.platform;


-- ─────────────────────────────────────────────────────────────
-- 5. USER SEGMENTATION BY ENGAGEMENT TIER (RFM-STYLE)
-- ─────────────────────────────────────────────────────────────
WITH user_metrics AS (
    SELECT
        user_id,
        platform,
        language,
        DATEDIFF('day', MAX(session_start_ts), CURRENT_DATE)    AS recency_days,
        COUNT(DISTINCT DATE(session_start_ts))                   AS frequency_days,
        SUM(session_duration_sec) / 60.0                        AS total_session_min,
        COUNT(DISTINCT DATE_TRUNC('month', session_start_ts))   AS active_months
    FROM user_sessions
    WHERE session_start_ts >= DATEADD(day, -90, CURRENT_DATE)
    GROUP BY 1, 2, 3
),
scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days ASC)       AS r_score,  -- lower recency = better
        NTILE(5) OVER (ORDER BY frequency_days DESC)    AS f_score,
        NTILE(5) OVER (ORDER BY total_session_min DESC) AS m_score
    FROM user_metrics
),
segmented AS (
    SELECT *,
        (r_score + f_score + m_score) AS rfm_total,
        CASE
            WHEN r_score >= 4 AND f_score >= 4                      THEN 'Champions'
            WHEN r_score >= 3 AND f_score >= 3                      THEN 'Loyal Users'
            WHEN r_score >= 4 AND f_score BETWEEN 1 AND 2           THEN 'Recent Users'
            WHEN r_score BETWEEN 2 AND 3 AND f_score BETWEEN 3 AND 4 THEN 'Promising'
            WHEN r_score <= 2 AND f_score >= 3                      THEN 'At Risk'
            WHEN r_score <= 2 AND f_score <= 2                      THEN 'Churned'
            ELSE 'Needs Attention'
        END AS segment
    FROM scored
)
SELECT
    segment,
    platform,
    COUNT(*)                                AS user_count,
    ROUND(AVG(recency_days), 1)            AS avg_recency_days,
    ROUND(AVG(frequency_days), 1)          AS avg_active_days,
    ROUND(AVG(total_session_min), 1)       AS avg_session_min,
    ROUND(AVG(active_months), 1)           AS avg_active_months
FROM segmented
GROUP BY 1, 2
ORDER BY user_count DESC;


-- ─────────────────────────────────────────────────────────────
-- 6. TOP CONTENT CREATORS BY LANGUAGE & PLATFORM
-- ─────────────────────────────────────────────────────────────
WITH creator_stats AS (
    SELECT
        c.creator_id,
        c.language,
        c.platform,
        COUNT(DISTINCT c.content_id)                    AS content_count,
        SUM(e.view_count)                               AS total_views,
        SUM(e.like_count + e.share_count + e.comment_count) AS total_engagements,
        ROUND(SUM(e.like_count + e.share_count + e.comment_count)::FLOAT
              / NULLIF(SUM(e.view_count), 0) * 100, 3)  AS overall_er_pct,
        SUM(e.watch_minutes)                            AS total_watch_min,
        COUNT(DISTINCT e.user_id)                       AS unique_viewers
    FROM content c
    JOIN content_engagement e ON c.content_id = e.content_id
    WHERE c.upload_date >= DATEADD(day, -30, CURRENT_DATE)
    GROUP BY 1, 2, 3
),
ranked AS (
    SELECT *,
        ROW_NUMBER() OVER (
            PARTITION BY language, platform
            ORDER BY total_views DESC
        ) AS rank_in_segment
    FROM creator_stats
)
SELECT
    creator_id, language, platform,
    content_count, total_views, total_engagements,
    overall_er_pct, total_watch_min, unique_viewers
FROM ranked
WHERE rank_in_segment <= 10
ORDER BY language, platform, rank_in_segment;


-- ─────────────────────────────────────────────────────────────
-- 7. 7-DAY AND 30-DAY ROLLING RETENTION RATES
-- ─────────────────────────────────────────────────────────────
WITH signup_cohort AS (
    SELECT user_id, DATE(signup_date) AS signup_day
    FROM users
    WHERE signup_date >= DATEADD(day, -60, CURRENT_DATE)
),
day7_return AS (
    SELECT DISTINCT s.user_id
    FROM signup_cohort s
    JOIN user_sessions sess ON s.user_id = sess.user_id
    WHERE DATE(sess.session_start_ts) BETWEEN s.signup_day + 6
                                          AND s.signup_day + 7
),
day30_return AS (
    SELECT DISTINCT s.user_id
    FROM signup_cohort s
    JOIN user_sessions sess ON s.user_id = sess.user_id
    WHERE DATE(sess.session_start_ts) BETWEEN s.signup_day + 29
                                          AND s.signup_day + 30
)
SELECT
    u.platform,
    COUNT(DISTINCT sc.user_id)                                          AS new_users,
    COUNT(DISTINCT d7.user_id)                                          AS returned_day7,
    COUNT(DISTINCT d30.user_id)                                         AS returned_day30,
    ROUND(COUNT(DISTINCT d7.user_id)::FLOAT  / COUNT(DISTINCT sc.user_id) * 100, 2) AS d7_retention_pct,
    ROUND(COUNT(DISTINCT d30.user_id)::FLOAT / COUNT(DISTINCT sc.user_id) * 100, 2) AS d30_retention_pct
FROM signup_cohort sc
JOIN users u ON sc.user_id = u.user_id
LEFT JOIN day7_return  d7  ON sc.user_id = d7.user_id
LEFT JOIN day30_return d30 ON sc.user_id = d30.user_id
GROUP BY u.platform
ORDER BY new_users DESC;


-- ─────────────────────────────────────────────────────────────
-- 8. CONTENT VIRALITY SCORE (SHARE VELOCITY)
-- ─────────────────────────────────────────────────────────────
WITH hourly_shares AS (
    SELECT
        content_id,
        DATEDIFF('hour', c.upload_date, e.event_ts)    AS hours_since_upload,
        COUNT(*)                                        AS shares_in_window
    FROM content_engagement e
    JOIN content c ON e.content_id = c.content_id
    WHERE e.action_type = 'share'
      AND e.event_ts <= c.upload_date + INTERVAL '48 hours'
    GROUP BY 1, 2
),
virality AS (
    SELECT
        content_id,
        SUM(CASE WHEN hours_since_upload <= 1  THEN shares_in_window ELSE 0 END) AS shares_1h,
        SUM(CASE WHEN hours_since_upload <= 6  THEN shares_in_window ELSE 0 END) AS shares_6h,
        SUM(CASE WHEN hours_since_upload <= 24 THEN shares_in_window ELSE 0 END) AS shares_24h,
        SUM(shares_in_window)                                                     AS shares_48h,
        -- Virality score: weighted by early acceleration
        SUM(shares_in_window * (1.0 / NULLIF(hours_since_upload, 0)))            AS virality_score
    FROM hourly_shares
    GROUP BY 1
)
SELECT
    c.content_id, c.content_type, c.language, c.category, c.platform,
    v.shares_1h, v.shares_6h, v.shares_24h, v.shares_48h,
    ROUND(v.virality_score, 2)  AS virality_score,
    NTILE(10) OVER (ORDER BY v.virality_score DESC) AS virality_decile
FROM virality v
JOIN content c ON v.content_id = c.content_id
ORDER BY v.virality_score DESC
LIMIT 100;


-- ─────────────────────────────────────────────────────────────
-- 9. LANGUAGE-LEVEL MONETISATION EFFICIENCY
-- ─────────────────────────────────────────────────────────────
WITH lang_users AS (
    SELECT language, COUNT(DISTINCT user_id) AS user_count
    FROM users
    GROUP BY 1
),
lang_revenue AS (
    SELECT
        u.language,
        SUM(ar.revenue_inr) / 1e7                          AS revenue_cr,
        SUM(ar.impressions)                                 AS impressions,
        ROUND(SUM(ar.revenue_inr)::FLOAT
              / NULLIF(SUM(ar.impressions), 0) * 1000, 2)  AS ecpm
    FROM ad_revenue ar
    JOIN user_sessions s ON ar.session_id = s.session_id
    JOIN users u          ON s.user_id    = u.user_id
    WHERE ar.revenue_date >= DATEADD(day, -30, CURRENT_DATE)
    GROUP BY 1
),
lang_engagement AS (
    SELECT
        u.language,
        AVG(s.session_duration_sec) / 60.0              AS avg_session_min,
        COUNT(DISTINCT s.session_id)
          / NULLIF(COUNT(DISTINCT s.user_id), 0)        AS sessions_per_user
    FROM user_sessions s
    JOIN users u ON s.user_id = u.user_id
    WHERE s.session_start_ts >= DATEADD(day, -30, CURRENT_DATE)
    GROUP BY 1
)
SELECT
    lu.language,
    lu.user_count,
    COALESCE(lr.revenue_cr, 0)          AS revenue_cr,
    COALESCE(lr.ecpm, 0)                AS ecpm,
    ROUND(lr.revenue_cr * 1e7
          / NULLIF(lu.user_count, 0), 2) AS arpu_inr,
    ROUND(le.avg_session_min, 2)        AS avg_session_min,
    ROUND(le.sessions_per_user, 2)      AS sessions_per_user
FROM lang_users lu
LEFT JOIN lang_revenue    lr ON lu.language = lr.language
LEFT JOIN lang_engagement le ON lu.language = le.language
ORDER BY revenue_cr DESC;


-- ─────────────────────────────────────────────────────────────
-- 10. FEED QUALITY SCORE — PERSONALISATION EFFECTIVENESS
-- ─────────────────────────────────────────────────────────────
-- Measures how well the recommendation engine serves relevant content.
-- A high skip-rate or low watch-through on recommended content signals
-- feed quality degradation.
WITH feed_events AS (
    SELECT
        fe.user_id,
        fe.content_id,
        fe.recommendation_rank,         -- position in the feed (1 = top)
        fe.is_recommended,              -- TRUE if algo-ranked, FALSE if chronological
        fe.was_skipped,
        fe.watch_pct,
        fe.liked,
        fe.shared
    FROM feed_impressions fe
    WHERE fe.event_date >= DATEADD(day, -7, CURRENT_DATE)
),
quality AS (
    SELECT
        is_recommended,
        recommendation_rank,
        COUNT(*)                                                            AS impressions,
        ROUND(AVG(watch_pct) * 100, 2)                                    AS avg_watch_pct,
        ROUND(SUM(was_skipped::INT)::FLOAT / COUNT(*) * 100, 2)          AS skip_rate_pct,
        ROUND(SUM(liked::INT)::FLOAT       / COUNT(*) * 100, 2)          AS like_rate_pct,
        ROUND(SUM(shared::INT)::FLOAT      / COUNT(*) * 100, 2)          AS share_rate_pct
    FROM feed_events
    GROUP BY 1, 2
)
SELECT *,
    -- Composite feed quality score (higher is better)
    ROUND(avg_watch_pct * 0.4
          + like_rate_pct * 0.3
          + share_rate_pct * 0.2
          + (100 - skip_rate_pct) * 0.1, 2) AS feed_quality_score
FROM quality
ORDER BY is_recommended DESC, recommendation_rank;


-- ─────────────────────────────────────────────────────────────
-- 11. WEEK-OVER-WEEK NEW USER ACQUISITION FUNNEL
-- ─────────────────────────────────────────────────────────────
WITH weekly_funnel AS (
    SELECT
        DATE_TRUNC('week', event_ts)            AS week_start,
        platform,
        COUNT(DISTINCT CASE WHEN event = 'app_install'          THEN device_id END) AS installs,
        COUNT(DISTINCT CASE WHEN event = 'onboarding_start'     THEN device_id END) AS onboarding_started,
        COUNT(DISTINCT CASE WHEN event = 'onboarding_complete'  THEN device_id END) AS onboarding_complete,
        COUNT(DISTINCT CASE WHEN event = 'profile_created'      THEN user_id   END) AS profiles_created,
        COUNT(DISTINCT CASE WHEN event = 'first_content_view'   THEN user_id   END) AS first_content_view,
        COUNT(DISTINCT CASE WHEN event = 'first_share'          THEN user_id   END) AS first_share
    FROM app_events
    WHERE event_ts >= DATEADD(week, -12, CURRENT_DATE)
    GROUP BY 1, 2
)
SELECT
    week_start,
    platform,
    installs,
    onboarding_started,
    onboarding_complete,
    profiles_created,
    first_content_view,
    first_share,
    -- Conversion rates
    ROUND(onboarding_started::FLOAT / NULLIF(installs,0)         * 100, 2) AS install_to_onboard_pct,
    ROUND(onboarding_complete::FLOAT/ NULLIF(onboarding_started,0)* 100, 2) AS onboard_completion_pct,
    ROUND(first_content_view::FLOAT / NULLIF(profiles_created,0)  * 100, 2) AS activation_rate_pct,
    ROUND(first_share::FLOAT        / NULLIF(first_content_view,0)* 100, 2) AS share_activation_pct
FROM weekly_funnel
ORDER BY week_start DESC, platform;
