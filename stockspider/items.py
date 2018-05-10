# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class StockItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    stock_attr = scrapy.Field()  # 种类·
    stock_id = scrapy.Field()  # 代码·
    stock_name = scrapy.Field()  # 名称·
    last_price = scrapy.Field()  # 最新价·
    up_down_prop = scrapy.Field()  # 涨跌幅·
    up_down_value = scrapy.Field()  # 涨跌额·
    shack_num = scrapy.Field()  # 成交量·
    shack_value = scrapy.Field()  # 成交额·
    today_open = scrapy.Field()  # 今开盘·
    yesterday_close = scrapy.Field()  # 昨收盘·
    lowest_price = scrapy.Field()  # 最低价·
    highest_price = scrapy.Field()  # 最高价·

    amplitude = scrapy.Field()  # 振幅
    hand = scrapy.Field()  # 换手率
    P_E = scrapy.Field()  # 市盈率
    P_B = scrapy.Field()  # 市净率
    earnings_per_share = scrapy.Field()  # 每股收益
    free_float = scrapy.Field()  # 流通盘
