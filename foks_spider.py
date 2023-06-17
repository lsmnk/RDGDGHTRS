import scrapy
import csv

class FoksSpider(scrapy.Spider):
    name = 'foks'
    start_urls = ['https://foks-donetsk.com/']

    def parse(self, response):
        """
        Парсит главную страницу сайта для извлечения ссылок на все категории товаров.
        """
        all_categories = response.css('a.all-cat-menu-link::attr(href)').getall()
        for link in all_categories:
            yield response.follow(link, self.parse_category)

    def parse_category(self, response):
        """
        Парсит страницу каждой категории товаров для извлечения ссылок на все товары.
        """
        all_products = response.css('div.catalog_item_name a::attr(href)').getall()
        for link in all_products:
            yield response.follow(link, self.parse_product)

        # Проверяем, есть ли следующая страница и если есть - переходим на неё.
        next_page = response.css('a.pagination-item-arrow_right::attr(href)').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse_category)

    def parse_product(self, response):
        """
        Парсит каждый товар для извлечения его характеристик.
        """
        category = response.css('div.breadcrumbs-link:last-child a::text').get().strip()
        name = response.css('div.product-item h1::text').get().strip()
        price = response.css('div.product_info_price span::text').get().strip()
        link = response.url

        yield {
            'Category': category,
            'Name': name,
            'Price': price,
            'Link': link
        }

class FoksPipeline:
    def __init__(self):
        self.file = open('foks.csv', 'w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=['Category', 'Name', 'Price', 'Link'])
        self.writer.writeheader()

    def process_item(self, item, spider):
        self.writer.writerow(item)
        return item

    def close_spider(self, spider):
        self.file.close()