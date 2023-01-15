SELECT
   team AS home,
   opponent AS away,
   home_code,
   away_code,
   home_last_wins,
   home_last_draws,
   home_last_loses,
   away_last_wins,
   away_last_draws,
   away_last_loses,
   GF,
   GA 
FROM
   df_matches 
WHERE
   GF < 10 
   AND GA < 10;