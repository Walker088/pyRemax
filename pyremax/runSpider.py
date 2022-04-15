
from scrapy.crawler import CrawlerProcess
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv
from os import environ
import pathlib

from pyremax.spiders.remax import RemaxSpider

crr_parent_path = pathlib.Path(__file__).parent.parent.resolve()
load_dotenv(f"{crr_parent_path}/.proj.env")

def InitCrawlerConfigs():
    PG = {
        "HOST": environ.get("PG_HOST", "localhost"),
        "PORT": environ.get("PG_PORT", "5432"),
        "SCHEMA": environ.get("PG_SCHEMA", "public"),
        "DB_NAME": environ.get("PG_DB_NAME", "pyinfo"),
        "USER": environ.get("PG_USER", "postgres"),
        "PASS": environ.get("PG_PASS", "postgresdefaultpass"),
    }
    FTP = {
        "HOST": environ.get("FTP_HOST"),
        "USER": environ.get("FTP_USER"),
        "PASSWORD": environ.get("FTP_PASSWORD"),
        "PATH": environ.get("FTP_PATH"),
    }
    env = Environment(loader = FileSystemLoader(f"{crr_parent_path}/pyremax/pyremax"))
    template = env.get_template("pg.conf.yml.j2")
    content = template.render(PG=PG, FTP=FTP)
    with open(f"{crr_parent_path}/pyremax/pyremax/pg.conf.yml", "w") as fp:
	    fp.write(content)

def StartCrawler():
    REMAX_MAX_PAGE_NUM = int(environ.get("REMAX_MAX_PAGE_NUM", "2"))
    SCRAPY_LOG_LEVEL = environ.get("SCRAPY_LOG_LEVEL", "INFO")
    #PY_GEO_API = environ.get("PY_GEO_API", None)

    process = CrawlerProcess(settings={
        "LOG_LEVEL": SCRAPY_LOG_LEVEL,
        "DEFAULT_REQUEST_HEADERS": {
            "USER_AGENT": "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en",
        },
        "ROBOTSTXT_OBEY": False,
        "DOWNLOAD_DELAY": 2,
        "EXTENSIONS": {
            "pyremax.extensions.spider_stat_ext.SpiderStatExt": 100,
        },
        "REMAX_MAX_PAGE_NUM": REMAX_MAX_PAGE_NUM,
        #"PY_GEO_API": PY_GEO_API,
    })
    process.crawl(RemaxSpider)
    process.start() # the script will block here until the crawling is finished

InitCrawlerConfigs()
StartCrawler()
