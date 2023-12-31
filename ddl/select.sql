-- clean news_item
SELECT DISTINCT 
    ticker, 
    title, 
    summary, 
    published_gmt, 
    description, 
    link, 
    language, 
    subject, 
    sector, 
    published_est, 
    market, 
    hour_of_day
into news_item_clean    
FROM news_item;


-- Create news_alpha
SELECT DISTINCT ticker, title, subject as topic, return, daily_alpha, action, published_est, hour_of_day, market 
INTO news_alpha 
FROM news_price 
WHERE daily_alpha IS NOT NULL;


-- CTE
WITH news_alpha AS (
    SELECT DISTINCT title, summary, description, subject, return, daily_alpha, action 
    FROM news_price 
    WHERE daily_alpha IS NOT NULL
)
SELECT * FROM news_alpha;

-- check for duplicates
SELECT link, COUNT(link) as count
FROM news_item
GROUP BY link
HAVING COUNT(link) > 1;

select title, summary, description, subject, return, daily_alpha, action from news_price
where subject non in ('Other News', 'Press releases', 'Conference Calls/ Webcasts', 'Environmental, Social, and Governance Criteria', 
      'Government News', 'Press releases')

select count(*) from news_price
where subject not in ('Other News', 'Press releases', 'Conference Calls/ Webcasts', 'Environmental, Social, and Governance Criteria', 
      'Government News', 'Press releases')
       

select published_est, ticker, subject, title, return, daily_alpha, action from news_price
where subject in
('Interim information',
'Regulatory information',
'Licensing Agreements',
'Contests/Awards',
'Law & Legal Issues',
'Mergers and Acquisitions',
'Initial Public Offerings',
'Warrants and Certificates',
'Dividend Reports and Estimates',
'Business Contracts',
'Research Analysis and Reports',
'Product / Services Announcement',
'Partnerships',
'Health',
'European Regulatory News',
'Clinical Study') and action is not null
order by published_est desc
limit 30
      
      
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
