# -*- coding: utf-8 -*-
import scrapy
from instagram.items import InstagramItem
import json
import hashlib


def hashStr(strInfo):
    h = hashlib.md5()
    h.update(strInfo.encode("utf-8"))
    return h.hexdigest()


class InspiderSpider(scrapy.Spider):
    name = 'inspider'
    allowed_domains = ['www.instagram.com']
    start_urls = ['http://www.instagram.com/rastaclat']
    first = 12
    rhx_gis = ''
    id = ''
    def parse(self, response):

        items = InstagramItem()
        js = response.selector.xpath('//script[contains(., "window._sharedData")]/text()').extract()
        js = js[0].replace("window._sharedData = ", "")
        jscleaned = js[:-1]

        # Load it as a json object
        locations = json.loads(jscleaned)
        self.rhx_gis = locations['rhx_gis']
        graphql = locations['entry_data']['ProfilePage'][0]['graphql']
        user = graphql['user']
        edges = []
        edges = user['edge_owner_to_timeline_media']['edges']
        page_info = user['edge_owner_to_timeline_media']['page_info']
        has_next_page = page_info['has_next_page']
        end_cursor = page_info['end_cursor']
        self.id = user['id']
        for item in edges:
            display_url = item['node']['display_url']
            items['image_urls'] = display_url
            yield items

        self.first += 12
        query_hash = '66eb9403e44cc12e5b5ecda48b667d41'
        variables = '{"id":"' + self.id + '","first":12,"after":"' +end_cursor+ '"}'
        print('--------------%s--------%s',self.id,end_cursor)
        next_URL = 'https://www.instagram.com/graphql/query/?query_hash='+ query_hash +'&variables='+ variables +''
        m = hashStr(self.rhx_gis + ":" + variables)
        if has_next_page == 1:
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, '
                                     'like Gecko) Chrome/71.0.3578.98 Safari/537.36','x-instagram-gis': m}
            print(headers)
            requset = scrapy.Request(next_URL,headers=headers, callback=self.parse_page)
            yield  requset
        else:
            return
    def parse_page(self,response):
        items = InstagramItem()
        data = json.loads(response.text)
        data = data['data']
        # print('---------%s---------', response.text)
        user = data['user']
        edges = []
        edges = user['edge_owner_to_timeline_media']['edges']
        page_info = user['edge_owner_to_timeline_media']['page_info']
        has_next_page = page_info['has_next_page']
        end_cursor = page_info['end_cursor']
        for item in edges:
            display_url = item['node']['display_url']
            items['image_urls'] = display_url
            yield items

        self.first += 12
        query_hash = '66eb9403e44cc12e5b5ecda48b667d41'
        variables = '{"id":"' + self.id + '","first":12,"after":"' + end_cursor + '"}'
        print('--------------%s--------%s', self.id, end_cursor)
        next_URL = 'https://www.instagram.com/graphql/query/?query_hash=' + query_hash + '&variables=' + variables + ''
        m = hashStr(self.rhx_gis + ":" + variables)
        if has_next_page == 1:
            headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, '
                                     'like Gecko) Chrome/71.0.3578.98 Safari/537.36', 'x-instagram-gis': m}
            print(headers)
            yield scrapy.Request(next_URL, headers=headers, callback=self.parse_page)
        else:
            return