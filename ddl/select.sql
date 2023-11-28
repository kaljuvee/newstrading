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
