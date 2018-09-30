# -*- coding: utf-8 -*-
import scrapy
import re

from prichan_items.spiders.utils import create_note_dict

class ItemsSpider(scrapy.Spider):
    name = 'items'
    allowed_domains = ['prichan.jp']
    start_urls = ['https://prichan.jp/items/']

    note_dict = create_note_dict()

    def parse(self, response):
        """アイテム一覧トップページからシリーズへのリンクを取得してリクエストする"""

        series_links = response.css('.items-nav a::attr(href)').extract()
        series_names = response.css('.items-nav li ::text').extract()
        names = re.sub(r"^[ \r\n]+","",re.sub(r"[\r\t　]+",""," ".join(series_names)), flags=(re.MULTILINE | re.DOTALL)).splitlines()
        for index in range(len(series_links)):
            url = response.urljoin(series_links[index])
            if url.find("promotion.html") == -1 and url.find("robots.txt") == -1:
                dan = "".join(re.sub("だい|だん|げんてい|きかん|ねん|がつ","",names[index],flags=(re.DOTALL)).split())
                yield scrapy.Request(url=url, callback=self.parse_series, meta={"number": dan})

    def parse_series(self, response):
        """各シリーズページ全体をパースする"""

        # ノート情報は self.note_dict を使って変なやり方で取得する
        # 詳細は utils.py を参照してね
        note = ''

        # みらいちゃんたちがモデルになってる画像付きのコーデセットごとのブロックのリスト
        coordinate_list = response.css('.coordinate-list')

        for coordinate in coordinate_list:
            # モデルの画像情報を取得
            outfit_id = coordinate.css('::attr(id)').extract_first()
            if outfit_id:
                outfit_image_url = response.urljoin(coordinate.css('.-outfit img::attr(data-src)').extract_first())
            else:
                outfit_image_url = ''

            # ノート情報を探す
            note = self.note_dict.get(outfit_id, '')
            meta = {
                'outfit_id': outfit_id,
                'outfit_image_url': outfit_image_url,
                'series_name': response.meta.get("number"),
                'series_url': response.url,
                'note': note,
            }

            item_list = coordinate.css('.-detail')
            for item in item_list:
                detail_url = response.urljoin(item.css('a::attr(href)').extract_first())
                yield scrapy.Request(url=detail_url, meta=meta, callback=self.parse_detail_item)

    def parse_detail_item(self, response):
        """アイテム詳細ページをパースする"""

        category, color = response.css('.-detail .-value::text').extract()[:2]
        color = re.sub(r"[\r\t\n　]+","",color, flags=(re.MULTILINE | re.DOTALL))
        item_id = response.css('.-id::text').extract_first()
        ticket_id = response.css('.-thumb img::attr(data-src)').re(r'/details\/(.+)\.(?:png|jpg)')

        # ブランド情報を取得
        m = response.css('.-detail.-brand img::attr(data-src)').re(r'/logo-(.+)\.(?:png|jpg)')
        if m:
            brand = m[0]
            brand_image_url = response.urljoin(response.css('.-detail.-brand img::attr(data-src)').extract_first())
        else:
            brand = ''
            brand_image_url = ''

        # ジャンル(ラブリー・ポップなどのタイプ)の情報を取得
        m = response.css('.-detail.-genre img::attr(data-src)').re(r'/icon-(.+)\.(?:png|jpg)')
        if m:
            genre = m[0]
            genre_image_url = response.urljoin(response.css('.-detail.-genre img::attr(data-src)').extract_first())
        else:
            genre = ''
            genre_image_url = ''

        # いいね☆
        try:
            like = int(response.css('.-like::text').extract_first())
        except ValueError:
            like = 0

        yield {
            'name': ' '.join(response.css('.the-item>.-title::text').extract()).strip(),
            'image_url': response.urljoin(response.css('.-thumb img::attr(data-src)').extract_first()),
            'category': category,
            'item_id': item_id,
            'ticket_id': ticket_id,
            'color': color,
            'brand': brand,
            'brand_image_url': brand_image_url,
            'genre': genre,
            'genre_image_url': genre_image_url,
            'rarity': response.css('.-rarity::text').extract_first(),
            'like': like,

            'outfit_id': response.meta['outfit_id'],
            'outfit_image_url': response.meta['outfit_image_url'],

            'note': response.meta['note'],

            'detail_url': response.url,
            'series_name': response.meta['series_name'],
            'series_url': response.meta['series_url'],
        }
