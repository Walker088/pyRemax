# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
#from dataclasses import dataclass

# TODO: Use dataclass to validate the input data 
# Ref: https://stackoverflow.com/questions/67360406/is-there-any-example-about-how-to-use-dataclass-and-scrapy-items
#@dataclass
class PyremaxItem(scrapy.Item):
    # table: remax_realestate, prvKey: (remax_prod_id, serial_number)
    remaxProdId = scrapy.Field() # key to the images
    serialNumber = scrapy.Field() # will be increased when the data of corresponded remaxProdId is changed
    businessType = scrapy.Field() # Rent/Sale
    propTitle = scrapy.Field()
    propType = scrapy.Field() # Land/Apartment/Duplex...
    propPrice = scrapy.Field()
    currency = scrapy.Field()
    totalRooms = scrapy.Field()
    bedRooms = scrapy.Field()
    bathRooms = scrapy.Field()
    livingSqM = scrapy.Field() # Round down to Int
    livingSqmNote = scrapy.Field() # original value in string
    propLink = scrapy.Field()
    latitud = scrapy.Field()
    longitud = scrapy.Field()
    location = scrapy.Field()
    creationTimestamp = scrapy.Field()
    imageLst = scrapy.Field()

