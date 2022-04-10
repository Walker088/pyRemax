# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

# useful for handling different item types with a single interface
# from xmlrpc.client import Boolean
# from itemadapter import ItemAdapter

import scrapy
from xmlrpc.client import Boolean
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
#from scrapy.utils.project import get_project_settings

from pyremax.postgres import conn
import psycopg2.extras
import psycopg2 as pgd

class PyremaxPipeline:
    def process_item(self, item, spider):
        if(item.get("remaxProdId", None) is None):
            print("[Error] Item id is None: ", item)
            return item
        itemDict = dict(item)
        query_map = {
            "NEW_REG": "INSERT INTO paraguay.remax_realestate (remax_prod_id, serial_number, business_type, prop_title, prop_type, prop_price, currency, total_rooms, bed_rooms, bath_rooms, living_sqm, living_sqm_note, prop_link, location, creation_timestamp) VALUES ( %(remaxProdId)s, 1, %(businessType)s, %(propTitle)s, %(propType)s, %(propPrice)s, %(currency)s, %(totalRooms)s, %(bedRooms)s, %(bathRooms)s, %(livingSqM)s, %(livingSqmNote)s, %(propLink)s, ST_GeomFromText(%(location)s, 4326), CURRENT_TIMESTAMP )",
            "CHANGED": "INSERT INTO paraguay.remax_realestate (remax_prod_id, serial_number, business_type, prop_title, prop_type, prop_price, currency, total_rooms, bed_rooms, bath_rooms, living_sqm, living_sqm_note, prop_link, location, creation_timestamp) SELECT %(remaxProdId)s, MAX(serial_number) + 1, %(businessType)s, %(propTitle)s, %(propType)s, %(propPrice)s, %(currency)s, %(totalRooms)s, %(bedRooms)s, %(bathRooms)s, %(livingSqM)s, %(livingSqmNote)s, %(propLink)s, ST_GeomFromText(%(location)s, 4326), CURRENT_TIMESTAMP FROM remax_realestate WHERE remax_prod_id = %(remaxProdId)s"
        }
        query_type = self.is_prop_updated(itemDict)
        query = query_map.get(query_type, None)
        if query is not None:
            with conn.cursor() as curs:
                try:
                    curs.execute(query, (itemDict))
                except Exception as e:
                    self.logger.error(e)
                    self.logger.error(curs.mogrify(query, (itemDict)))
        return item

    def is_prop_updated(self, remax_prop: dict) -> str:
        ''' 
        New registry: Insert with serial_number 1
        Changed registry: Insert with max serial_number + 1
        Unchanged registry: Skip the insertion
        '''
        query = "SELECT rr.remax_prod_id, rr.business_type, rr.prop_title, rr.prop_type, rr.prop_price, rr.currency, rr.total_rooms, rr.bed_rooms, rr.bath_rooms, rr.living_sqm FROM paraguay.remax_realestate rr WHERE rr.remax_prod_id = %(remax_prod_id)s AND rr.serial_number = (SELECT MAX(serial_number) FROM remax_realestate WHERE remax_prod_id = rr.remax_prod_id);"
        try:
            with conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor) as curs:
                #print(curs.mogrify(query, {"remax_prod_id": remax_prop.get("remaxProdId", "")}))
                curs.execute(query, {"remax_prod_id": remax_prop.get("remaxProdId", "")})
                lastReg = curs.fetchone()
                if (lastReg is None ): return "NEW_REG" # New registry
                if (lastReg.get("business_type", "") == remax_prop.get("businessType", "")
                    and lastReg.get("prop_title", "") == remax_prop.get("propTitle", "")
                    and lastReg.get("prop_type", "") == remax_prop.get("propType", "")
                    and lastReg.get("prop_price", "") == remax_prop.get("propPrice", "")
                    and lastReg.get("currency", "") == remax_prop.get("currency", "")
                    and lastReg.get("total_rooms", "") == remax_prop.get("totalRooms", "")
                    and lastReg.get("bed_rooms", "") == remax_prop.get("bedRooms", "")
                    and lastReg.get("bath_rooms", "") == remax_prop.get("bathRooms", "")
                    and lastReg.get("living_sqm", "") == remax_prop.get("livingSqM", "")
                ):
                    return "UNCHANGED" # Unchanged registry
                return "CHANGED" # Changed registry
        except pgd.Error as e:
            self.logger.error(e)


class PyremaxImgPipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None, *, item=None):
        from scrapy.utils.python import to_bytes
        import os, hashlib, mimetypes

        media_folder = item.get("remaxProdId", "others")
        media_guid = hashlib.sha1(to_bytes(request.url)).hexdigest()
        media_ext = os.path.splitext(request.url)[1]
        if media_ext not in mimetypes.types_map:
            media_ext = ''
            media_type = mimetypes.guess_type(request.url)[0]
            if media_type:
                media_ext = mimetypes.guess_extension(media_type)
        return f'{media_folder}/{media_guid}{media_ext}'

    def get_media_requests(self, item, info):
        for image_url in item['imageLst']:
            yield scrapy.Request(image_url)

    def item_completed(self, results, item, info):
        stored_image_paths = [x["path"] for ok, x in results if ok]
        if not stored_image_paths:
            raise DropItem("Item contains no images")
        
        for stored_img_path in stored_image_paths: self.insert_image_info(item["remaxProdId"], stored_img_path)
        return item

    def insert_image_info(self, remaxProdId, imagePath):
        def is_image_exists() -> Boolean:
            query = "SELECT 1 FROM remax_realestate_img WHERE remax_prod_id = %(remaxProdId)s AND image_path = %(imagePath)s"
            with conn.cursor() as curs:
                curs.execute(query, {"remaxProdId": remaxProdId, "imagePath": imagePath})
                res = curs.fetchone()
                if res is None: return False
                else: return True
        if is_image_exists(): return
        query = "INSERT INTO remax_realestate_img(remax_prod_id, serial_number, image_path, creation_timestamp) SELECT %(remaxProdId)s, (SELECT COALESCE(MAX(serial_number) + 1, 1) FROM remax_realestate_img WHERE remax_prod_id = %(remaxProdId)s), %(imagePath)s, CURRENT_TIMESTAMP"
        with conn.cursor() as curs:
            try:
                curs.execute(query, ({"remaxProdId": remaxProdId, "imagePath": imagePath}))
            except Exception as e:
                self.logger.error(e)
                self.logger.info(curs.mogrify(query, ({"remaxProdId": remaxProdId, "imagePath": imagePath})))

