# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Item(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    name_en = scrapy.Field()
    description = scrapy.Field()
    categories = scrapy.Field()
    director = scrapy.Field()
    actors = scrapy.Field()
    links = scrapy.Field()
    image_path = scrapy.Field()
    vendor_url = scrapy.Field()
    vendor_name = scrapy.Field()
    vendor_id = scrapy.Field()
