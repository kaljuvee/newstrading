-- check for duplicates
SELECT link, COUNT(link) as count
FROM news_item
GROUP BY link
HAVING COUNT(link) > 1;

select title, summary, description, subject, daily_alpha, action from news_price

select count(*), subject from news_item
group by subject
order by 1 desc

SELECT subject, 
       COUNT(*) AS total_count, 
       STDDEV(return) AS return_stddev,  -- Standard deviation of 'return' for each subject
       STDDEV(daily_alpha) AS alpha_stddev  -- Standard deviation of 'index_return' for each subject
FROM news_price
GROUP BY subject
HAVING STDDEV(return) IS NOT NULL AND STDDEV(daily_alpha) IS NOT NULL
order by 4 desc