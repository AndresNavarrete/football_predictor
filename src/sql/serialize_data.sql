SELECT
   MatchNumber::INT AS id,
   RoundNumber::INT AS round,
   DateUtc::DATE AS DATE,
   HomeTeam AS home,
   AwayTeam AS away,
   TRY_CAST(HomeTeamScore AS INTEGER) AS home_goals,
   TRY_CAST(AwayTeamScore AS INTEGER) AS away_goals,
   CASE
      WHEN
         HomeTeamScore IS NULL 
      THEN
         FALSE 
      ELSE
         TRUE 
   END
   AS played 
FROM
   raw_data ;