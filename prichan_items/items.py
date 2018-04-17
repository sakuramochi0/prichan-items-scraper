# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PrichanItemsItem(scrapy.Item):
    # Meta data
    detail_url = scrapy.Field()
    series_name = scrapy.Field()
    series_url = scrapy.Field()

    # Item data
    name = scrapy.Field()
    image_url = scrapy.Field()
    category = scrapy.Field()
    item_id = scrapy.Field()
    ticket_id = scrapy.Field()
    color = scrapy.Field()
    brand = scrapy.Field()
    brand_image_url = scrapy.Field()
    genre = scrapy.Field()
    genre_image_url = scrapy.Field()
    rarity = scrapy.Field()
    like = scrapy.Field()

    # Outfit data by characters
    outfit_id = scrapy.Field()
    outfit_image_url = scrapy.Field()
