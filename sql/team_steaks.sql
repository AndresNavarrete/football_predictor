WITH matches AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY season, team ORDER BY datetime) AS match_number_home,
        ROW_NUMBER() OVER (PARTITION BY season, opponent ORDER BY datetime) AS match_number_away
    FROM df_matches
    ORDER BY season, datetime
)
SELECT
    m.*,
    (SELECT COUNT(*) FROM matches WHERE season = m.season AND team = m.team AND result = 'W' AND match_number_home > m.match_number_home - 6 AND match_number_home < m.match_number_home) AS home_last_wins,
    (SELECT COUNT(*) FROM matches WHERE season = m.season AND team = m.team AND result = 'L' AND match_number_home > m.match_number_home - 6 AND match_number_home < m.match_number_home) AS home_last_loses,
    (SELECT COUNT(*) FROM matches WHERE season = m.season AND team = m.team AND result = 'D' AND match_number_home > m.match_number_home - 6 AND match_number_home < m.match_number_home) AS home_last_draws,
    (SELECT COUNT(*) FROM matches WHERE season = m.season AND opponent = m.opponent AND result = 'W' AND match_number_away > m.match_number_away - 6 AND match_number_away < m.match_number_away) AS away_last_wins,
    (SELECT COUNT(*) FROM matches WHERE season = m.season AND opponent = m.opponent AND result = 'L' AND match_number_away > m.match_number_away - 6 AND match_number_away < m.match_number_away) AS away_last_loses,
    (SELECT COUNT(*) FROM matches WHERE season = m.season AND opponent = m.opponent AND result = 'D' AND match_number_away > m.match_number_away - 6 AND match_number_away < m.match_number_away) AS away_last_draws            
FROM matches m;