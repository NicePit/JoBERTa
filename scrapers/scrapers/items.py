# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapersItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    published = scrapy.Field()
    easy_apply = scrapy.Field()
    url = scrapy.Field()
    description = scrapy.Field()
    rating = scrapy.Field()
    company_name = scrapy.Field()
    company_size = scrapy.Field()
