# -*- coding: utf-8 -*-
import re
from scrapy import Request, Spider
from urllib.parse import urljoin

import stockspider.items
from stockspider.items import StockItem


class IfengSpider(Spider):
    name = 'ifeng'
    # allowed_domains = ['app.finance.ifeng.com']
    start_urls = ['http://app.finance.ifeng.com/list/stock.php']
    count = 0
    total = 0

    def parse(self, response):
        item = StockItem()
        li_list = response.xpath('//div[@class="block"]/ul/li')
        for li in li_list:
            url = urljoin(response.url, li.xpath('.//a/@href').extract_first())
            item['stock_attr'] = li.xpath('.//a/text()').extract_first()
            yield Request(url, callback=self.parse_table, meta={'data': item})

    def parse_table(self, response):
        print(response.url)
        item = response.meta['data']
        tr_list = response.xpath('//table/tr')
        tr_list.pop(0)
        next_tr = tr_list.pop(-1)
        for tr in tr_list:
            self.count += 1
            self.total += 1
            url = tr.xpath('./td[1]/a/@href').extract_first()
            item['stock_id'] = tr.xpath('./td[1]/a/text()').extract_first()
            item['stock_name'] = tr.xpath('./td[2]/a/text()').extract_first()
            item['last_price'] = tr.xpath('./td[3]/span/text()').extract_first()
            item['up_down_prop'] = tr.xpath('./td[4]/span/text()').extract_first()
            item['up_down_value'] = tr.xpath('./td[5]/span/text()').extract_first()
            item['shack_num'] = tr.xpath('./td[6]/text()').extract_first()
            item['shack_value'] = tr.xpath('./td[7]/text()').extract_first()
            item['today_open'] = tr.xpath('./td[8]/span/text()').extract_first()
            item['yesterday_close'] = tr.xpath('./td[9]/text()').extract_first()
            item['lowest_price'] = tr.xpath('./td[10]/span/text()').extract_first()
            item['highest_price'] = tr.xpath('./td[11]/span/text()').extract_first()
            print(self.total)
            yield item
            # yield Request(url, callback=self.parse_detail, meta={'data': item})
        print(self.count)

        next_url = next_tr.xpath('./td/a[text()="下一页"]/@href').extract_first()
        if next_url:
            next_url = urljoin(response.url, next_url)
            print('next_url', next_url)
            yield Request(next_url, callback=self.parse_table, meta={'data': item})

    @staticmethod
    def string_handle(val):
        try:
            json = val.strip().split('=')
            json_str = json[1][0:-1]
            json_list = json_str.split(':')[1][0:-1]
            json_q = eval(json_list)
            return json_q
        except Exception as e:
            print(e)
            return None

    def parse_detail(self, response):
        item = response.meta['data']
        stockid = re.search(r'\w+\d{6}', response.url)
        if stockid:
            detail_url = 'https://hq.finance.ifeng.com/q.php?l={}'.format(stockid.group(0))
            if not re.search(r'data =', response.text):
                yield Request(response.request.url, callback=self.parse_detail, meta={'data': item})
                return
            ltg = re.search(r'ltg : (\d+)', response.text)
            if ltg is not None:
                ltg = int(ltg.group(1))
            else:
                ltg = None
            mgsy = re.search(r'mgsy : ([-]*\d+[.]*\d+)', response.text)
            if mgsy is not None:
                mgsy = float(mgsy.group(1))
            else:
                mgsy = None
            mgjzc = re.search(r'mgjzc : ([-]*\d+[.]*\d+)', response.text)
            if mgjzc is not None:
                mgjzc = float(mgjzc.group(1))
            else:
                mgjzc = None

            yield Request(detail_url, callback=self.parse_detail_data,
                          meta={'data': item, 'ltg': ltg, 'mgsy': mgsy, 'mgjzc': mgjzc})
        else:
            self.count -= 1
            print('error:', response.url)
            yield Request(response.request.url, callback=self.parse_detail, meta={'data': item})

    def parse_detail_data(self, response):
        item = response.meta['data']
        ltg = response.meta['ltg']
        mgsy = response.meta['mgsy']
        mgjzc = response.meta['mgjzc']

        json_q = self.string_handle(response.text)
        if not json_q:
            print("not json data error:", response.request.url)
            yield Request(response.request.url, callback=self.parse_detail_data,
                          meta={'data': item, 'ltg': ltg, 'mgsy': mgsy, 'mgjzc': mgjzc})

        if ltg is not None and int(ltg) != 0:
            hand = str(json_q[9] / int(ltg) * 100) + "%"
            free_float = ltg / 100000000
        else:
            hand = "--"
            free_float = '--'

        if mgsy is not None and float(mgsy) != 0:
            P_E = json_q[0] / float(mgsy) if json_q[0] / float(mgsy) > 0 else '亏损'
        else:
            P_E = '--'
        if mgjzc is not None and float(mgjzc) != 0:
            P_B = json_q[0] / float(mgjzc)
        else:
            P_B = '--'

        detail_dict = {
            'amplitude': str((json_q[5] - json_q[6]) / json_q[1] * 100) + "%",  # 振幅
            'hand': hand,  # 换手率
            'P_E': P_E,  # 市盈率
            'P_B': P_B,  # 市净率
            'earnings_per_share': mgsy,  # 每股收益
            'free_float': free_float,  # 流通盘
        }

        for field in detail_dict.keys():
            item[field] = detail_dict[field]

        self.count -= 1

        print(self.count)
        print(self.total)
        yield item
