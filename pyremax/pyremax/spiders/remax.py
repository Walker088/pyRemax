
import scrapy
import logging
import yaml
import os
import json
import pathlib
import requests as rq
from time import sleep
from random import randint
from re import sub
from decimal import Decimal, ROUND_HALF_UP
from scrapy.utils.project import get_project_settings

from pyremax.items import PyremaxItem
from pyremax.items import MiticPostalItem

# selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOpts
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.remote_connection import LOGGER as SeleniumLogger
from urllib3.connectionpool import log as UrllibLogger

getCurrencyVal = lambda c : Decimal(sub(r"[^\d.]", "", c))

def getFtpStorePath() -> dict:
    crr_parent_path = pathlib.Path(__file__).parent.parent.resolve()
    with open(f"{crr_parent_path}/pg.conf.yml", "r") as f:
        config = yaml.safe_load(f)
        ftp = {
            "FTP_HOST": config.get("ftp").get("FTP_HOST"),
            "FTP_USER": config.get("ftp").get("FTP_USER"),
            "FTP_PASSWORD": config.get("ftp").get("FTP_PASSWORD"),
            "PATH": config.get("ftp").get("PATH"),
        }
        return f'ftp://{ftp["FTP_USER"]}:{ftp["FTP_PASSWORD"]}@{ftp["FTP_HOST"]}/{ftp["PATH"]}'

class RemaxSpider(scrapy.Spider):
    name = "remax"
    allowed_domains = ["www.remax.com.py"]
    start_urls = ["https://www.remax.com.py/PublicListingList.aspx"]
    PY_GEO_API = "https://codigopostal.paraguay.gov.py/dinacopa/zona/geometry"
    custom_settings = {
        "ITEM_PIPELINES": {
            "pyremax.pipelines.PyremaxPipeline": 100,
            "pyremax.pipelines.PyremaxPostalPipeline": 150,
            "pyremax.pipelines.PyremaxImgPipeline": 200,
        },
        "IMAGES_STORE": getFtpStorePath(),
        "SAVE_STATS_TO_DB": True
    }
    page_loading_delay = 15 # seconds
    max_page_toggling_delay = 10 # seconds
    max_page_refresh_times = 3

    def __init__(self):
        SeleniumLogger.setLevel(logging.INFO)
        UrllibLogger.setLevel(logging.INFO)
        opts = FirefoxOpts()
        opts.log.level = "INFO"
        opts.add_argument("--headless")
        self.driver = webdriver.Firefox(options=opts, service_log_path=os.devnull)
        self.imgDriver = webdriver.Firefox(options=opts)

    def start_requests(self):
        """
        Using a dummy website to start scrapy request
        """
        yield scrapy.Request(url="http://quotes.toscrape.com", callback=self.parse)

    def parse_page(self) -> list:
        estateLst = []
        try:
            wait = WebDriverWait(self.driver, self.page_loading_delay)
            props = wait.until(EC.presence_of_all_elements_located( (By.XPATH, "//div[@class='gallery-item-container']") ))
            remaxProdIds = [prop.get_attribute("id") for prop in props]
            for propId in remaxProdIds:
                try:
                    rawBusinessTypeWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//div[contains(@class, 'card-trans-type')]")
                    rawPropTitleWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//div[contains(@class, 'gallery-title')]/a")
                    rawPropTypeWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//div[contains(@class, 'gallery-transtype')]/span")
                    rawPriceWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//span[contains(@class, 'gallery-price-main')]/a")
                    rawTotalRoomsWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//div[contains(@class, 'gallery-icons')]/img[contains(@data-original-title, 'Total Rooms')]/following-sibling::span[contains(@class, 'gallery-attr-item-value')][1]")
                    rawBedRoomsWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//div[contains(@class, 'gallery-icons')]/img[contains(@data-original-title, 'Bedrooms')]/following-sibling::span[contains(@class, 'gallery-attr-item-value')][1]")
                    rawBathRoomsWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//div[contains(@class, 'gallery-icons')]/img[contains(@data-original-title, 'Bathrooms')]/following-sibling::span[contains(@class, 'gallery-attr-item-value')][1]")
                    rawLivingSqMWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//div[contains(@class, 'gallery-icons')]/img[contains(@data-original-title, 'Living SqM')]/following-sibling::span[contains(@class, 'gallery-attr-item-value')][1]")
                    rawLinkWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//span[contains(@class, 'gallery-price-main')]/a")
                    rawLocationWebEle = self.driver.find_elements(By.XPATH, f"//div[@id='{propId}']//i[@data-lat or @data-lng]")

                    estate = PyremaxItem()
                    estate["remaxProdId"] = propId
                    estate["businessType"] = rawBusinessTypeWebEle[0].text if len(rawBusinessTypeWebEle) == 1 else None
                    estate["propTitle"] = rawPropTitleWebEle[0].get_attribute("title") if len(rawPropTitleWebEle) == 1 else None
                    estate["propType"] = rawPropTypeWebEle[0].text if len(rawPropTypeWebEle) == 1 else None
                    if len(rawPriceWebEle) == 1:
                        rawPrice = rawPriceWebEle[0].text
                        USD = sub(r"[^((?!USD).)*$]", "", rawPrice)
                        #PYG = sub(r"[^((?!₲).)*$]", "", rawPrice)
                        currency = "USD" if USD != "" else "PYG"
                        estate["propPrice"] = int(getCurrencyVal(rawPrice).quantize(Decimal('0'), ROUND_HALF_UP))
                        estate["currency"] = currency if currency != "" else sub(r"[^A-Za-z₲]+", "", rawPrice)
                    estate["totalRooms"] = int(rawTotalRoomsWebEle[0].text) if len(rawTotalRoomsWebEle) == 1 else None
                    estate["bedRooms"] = int(rawBedRoomsWebEle[0].text) if len(rawBedRoomsWebEle) == 1 else None
                    estate["bathRooms"] = int(rawBathRoomsWebEle[0].text) if len(rawBathRoomsWebEle) == 1 else None
                    estate["livingSqM"] = getCurrencyVal(rawLivingSqMWebEle[0].text) if len(rawLivingSqMWebEle) == 1 else None
                    estate["livingSqmNote"] = None
                    estate["propLink"] = rawLinkWebEle[0].get_attribute("href") if len(rawLinkWebEle) == 1 else None
                    estate["latitud"] = rawLocationWebEle[0].get_attribute("data-lat") if len(rawLocationWebEle) == 1 else None
                    estate["longitud"] = rawLocationWebEle[0].get_attribute("data-lng") if len(rawLocationWebEle) == 1 else None
                    estate["location"] = f'POINT({estate["longitud"]} {estate["latitud"]})' if estate["latitud"] is not None and estate["longitud"] is not None else None
                    estateLst.append(estate)
                except Exception as e:
                    self.logger.error("Parse Remax Prop Info Error")
                    self.logger.error(e)
            for e in estateLst:
                if e["propLink"] is not None:
                    try:
                        self.imgDriver.get(e["propLink"])
                        wait = WebDriverWait(self.imgDriver, self.page_loading_delay)
                        imgs = wait.until(EC.presence_of_all_elements_located( (By.XPATH, "//div[contains(@class, 'sp-image-container')]/img") ))
                        if(len(imgs) > 0): e["imageLst"] = [ i.get_attribute("data-medium") for i in imgs ]
                    except Exception as e:
                        self.logger.error("Get Property Img Error")
                        self.logger.error(e)
            for e in estateLst:
                if e["location"] is not None:
                    try:
                        resp = rq.get(f'{self.PY_GEO_API}?latitud={e["latitud"]}&longitud={e["longitud"]}').json()
                        e["dpto"] = resp.get("properties").get("dpto")
                        e["distrito"] = resp.get("properties").get("distrito")
                        e["barloc"] = resp.get("properties").get("barloc")
                        e["postalInfo"] = MiticPostalItem(
                                dpto = resp.get("properties").get("dpto"),
                                dpto_desc = resp.get("properties").get("dpto_desc"),
                                distrito = resp.get("properties").get("distrito"),
                                dist_desc = resp.get("properties").get("dist_desc"),
                                barloc = resp.get("properties").get("barloc"),
                                barloc_desc = resp.get("properties").get("barloc_desc"),
                                cod_post = resp.get("properties").get("cod_post"),
                                barrio_polygon = json.dumps(resp.get("geometry"))
                            )
                    except Exception as e:
                        self.logger.error("Query Mitic Postal Info Error")
                        self.logger.error(e)
        except Exception as e:
            self.logger.error("Selenium Get Remax Main Page Error")
            self.logger.error(e)
        return estateLst

    def parse(self, response):
        REMAX_MAX_PAGE_NUM = self.settings.getint('REMAX_MAX_PAGE_NUM')
        for page in range(1, REMAX_MAX_PAGE_NUM):
            try:
                self.driver.get(f"{self.start_urls[0]}?CurrentPage={page}")
                estateLst = self.parse_page()
                for e in estateLst: yield e

                sleep(randint(1, self.max_page_toggling_delay))
            except Exception:
                self.driver.get(f"{self.start_urls[0]}?CurrentPage={page}")
                estateLst = self.parse_page()
                for e in estateLst: yield e

                sleep(randint(1, self.max_page_toggling_delay))
                continue

    def closed(self, reason):
        from pyremax.postgres import conn
        from datetime import timedelta as td
        stats = self.crawler.stats.get_stats()
        elapsed_time = td(seconds=stats.get("elapsed_time_seconds", 0))
        self.logger.info(f'Crawler finished, inserted {stats.get("item_scraped_count", 0)} properties and {stats.get("file_count", 0)} images in {str(elapsed_time)}')

        conn.close() # close the global db connection
        self.driver.close()
        self.imgDriver.close()
