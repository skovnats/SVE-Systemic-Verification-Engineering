SELECT
    feature_name,
    COUNT(DISTINCT match_id) as matches_covered,
    COUNT(*) / COUNT(DISTINCT match_id) as avg_values_per_match
FROM feast_features
GROUP BY 1
