SELECT
    f.feature_name,
    CORR(f.value, b.profit) as correlation
FROM feast_features f
JOIN bets b ON f.match_id = b.match_id
GROUP BY 1
ORDER BY ABS(correlation) DESC
