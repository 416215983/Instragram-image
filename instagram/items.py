# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class InstagramItem(scrapy.Item):
    # define the fields for your item here like:
    images = scrapy.Field()
    image_urls = scrapy.Field()
    image_paths = scrapy.Field()
    pass
