CREATE TABLE news_item (
    id SERIAL PRIMARY KEY,  -- Typically, tables should have an identifier. I've added an auto-incrementing ID.
    ticker VARCHAR(255) NOT NULL,
    title TEXT,
    summary TEXT,
    published_gmt TIMESTAMP,
    description TEXT,
    link TEXT,
    language VARCHAR(8),
    subject TEXT,
    sector TEXT,
    published_est TIMESTAMP,
    market VARCHAR(255),
    hour_of_day INT
);

CREATE TABLE news_price (
    id SERIAL PRIMARY KEY,  -- Typically, tables should have an identifier. I've added an auto-incrementing ID.
    ticker VARCHAR(255) NOT NULL,
    title TEXT NOT NULL,
    summary TEXT,
    published_gmt TIMESTAMP NOT NULL,
    description TEXT,
    link TEXT NOT NULL,
    language VARCHAR(50),  -- This field appears empty in the example, but I've added it in case you need it in the future.
    subject VARCHAR(255),
    sector VARCHAR(255) NOT NULL,
    published_est TIMESTAMP NOT NULL,
    market VARCHAR(255),
    hour_of_day INT,
    begin_price NUMERIC(20,10),
    end_price NUMERIC(20,10),
    index_begin_price NUMERIC(20,10),
    index_end_price NUMERIC(20,10),
    return NUMERIC(20,10),
    index_return NUMERIC(20,10),
    daily_alpha NUMERIC(20,10),
    action VARCHAR(8)
);

-- check for duplicates
SELECT link, COUNT(link) as count
FROM news_item
GROUP BY link
HAVING COUNT(link) > 1;

select title, summary, description, subject, daily_alpha, action from news_price

select count(*), subject from news_item
group by subject
order by 1 desc

