import logging
from scrapy import signals
from pyremax.postgres import conn

logger = logging.getLogger(__name__)

class SpiderStatExt:

    def __init__(self, save_stats_to_db):
        self.save_stats_to_db = save_stats_to_db

    @classmethod
    def from_crawler(cls, crawler):
        save_stats_to_db = crawler.settings.getbool("SAVE_STATS_TO_DB", False)

        # instantiate the extension object
        ext = cls(save_stats_to_db)

        # connect the extension object to signals
        # crawler.signals.connect(ext.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(ext.spider_closed, signal=signals.spider_closed)

        # return the extension object
        return ext

    def spider_closed(self, spider):
        #logger.info("closed spider %s", spider.name)
        stats = spider.crawler.stats.get_stats()
        spider_result_stats = {
            "spider_name": spider.name,
            "items_scraped": stats.get('item_scraped_count', 0),
            "files_scraped": stats.get('file_count', 0),
            "finish_reason": stats.get('finish_reason'),
            "start_timestamp": stats.get('start_time'),
            "finish_timestamp": stats.get('finish_time'),
        }
        if self.save_stats_to_db:
            query = "INSERT INTO paraguay.spider_exec_history (spider_name, serial_number, items_scraped, files_scraped, finish_reason, start_timestamp, finish_timestamp) SELECT %(spider_name)s, COALESCE(MAX(serial_number) + 1, 1), %(items_scraped)s, %(files_scraped)s, %(finish_reason)s, %(start_timestamp)s, %(finish_timestamp)s FROM spider_exec_history WHERE spider_name = %(spider_name)s"
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (spider_result_stats))
                except Exception as e:
                    logger.error(e)
                    logger.info(curs.mogrify(query, (spider_result_stats)))
        logger.info(spider_result_stats)
