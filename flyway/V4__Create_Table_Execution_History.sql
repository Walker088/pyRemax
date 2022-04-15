
ALTER TABLE paraguay.remax_realestate ALTER column prop_price TYPE INT8;

CREATE TABLE IF NOT EXISTS paraguay.spider_exec_history (
    spider_name TEXT NOT NULL,
    serial_number INT4 NOT NULL,
    items_scraped INT4,
    files_scraped INT4,
    finish_reason TEXT,
    start_timestamp TIMESTAMP,
    finish_timestamp TIMESTAMP,
    PRIMARY KEY (spider_name, serial_number)
);
