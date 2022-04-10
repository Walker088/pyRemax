
from scrapy.crawler import CrawlerProcess
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from os import environ

from pyremax.spiders.remax import RemaxSpider

def InitCrawlerConfigs():
    load_dotenv(".proj.env")
    PG = {
        "HOST": environ.get("PG_HOST"),
        "PORT": environ.get("PG_PORT"),
        "SCHEMA": environ.get("PG_SCHEMA"),
        "DB_NAME": environ.get("PG_DB_NAME"),
        "USER": environ.get("PG_USER"),
        "PASS": environ.get("PG_PASS"),
    }
    FTP = {
        "HOST": environ.get("FTP_HOST"),
        "USER": environ.get("FTP_USER"),
        "PASSWORD": environ.get("FTP_PASSWORD"),
        "PATH": environ.get("FTP_PATH"),
    }
    env = Environment(loader = FileSystemLoader("./pyremax/pyremax"))
    template = env.get_template("pg.conf.yml.j2")
    content = template.render(PG=PG, FTP=FTP)
    with open('./pyremax/pyremax/pg.conf.yml','w') as fp:
	    fp.write(content)

def StartCrawler():
    process = CrawlerProcess(settings={
        "DEFAULT_REQUEST_HEADERS": {
            "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en",
        },
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 2,
        "EXTENSIONS": {
            "pyremax.extensions.spider_stat_ext.SpiderStatExt": 100,
        }
    })
    process.crawl(RemaxSpider)
    process.start() # the script will block here until the crawling is finished

InitCrawlerConfigs()
StartCrawler()
