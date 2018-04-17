# -*- coding: utf-8 -*-
import scrapy

from prichan_items.spiders.utils import create_note_dict


class ItemsSpider(scrapy.Spider):
    name = 'items'
    allowed_domains = ['prichan.jp']
    start_urls = ['https://prichan.jp/items/']

    note_dict = create_note_dict()

    def parse(self, response):
        """アイテム一覧トップページからシリーズへのリンクを取得してリクエストする"""

        series_links = response.css('.items-nav a::attr(href)').extract()
        for series_link in series_links:
            url = response.urljoin(series_link)
            yield scrapy.Request(url=url, callback=self.parse_series)

    def parse_series(self, response):
        """各シリーズページ全体をパースする"""

        # ノート情報は self.note_dict を使って変なやり方で取得する
        # 詳細は utils.py を参照してね
        note = ''

        # みらいちゃんたちがモデルになってる画像付きのコーデセットごとのブロックのリスト
        coordinate_list = response.css('li.coordinate-list')

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
                'series_name': ' '.join(response.css('.items-nav .active ::text').extract()).strip(),
                'series_url': response.url,
                'note': note,
            }

            item_list = coordinate.css('.-detail')
            for item in item_list:
                detail_url = response.urljoin(item.css('a::attr(href)').extract_first())
                yield scrapy.Request(url=detail_url, meta=meta, callback=self.parse_detail_item)

    def parse_detail_item(self, response):
        """アイテム詳細ページをパースする"""

        category, item_id, ticket_id, color = response.css('.-detail .-value::text').extract()[:4]

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
