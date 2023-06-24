
import scrapy
from scrapy_splash import SplashRequest
from scrapy import Spider

class AritziaSpider(Spider):

    name = "aritzia"

    start_urls = [
        'https://www.aritzia.com/en/clothing',
    ]
    url_counter = 0
    def parse(self, response):
        self.url_counter += 1
        product_urls = response.xpath('//a[@class="relative db js-plp-hash "]/@href').getall()

        for url in product_urls:
            yield SplashRequest(url, callback=self.parse_item, meta={'url': url})

        load_more_buttons = response.xpath('//div[@class="js-load-more__button mb3"]/a/@href')
        for button in load_more_buttons:
            yield SplashRequest(
                url=response.urljoin(button.get()),
                callback=self.parse_item,
                endpoint='render.html',
                args={'wait': 5},
            )
    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse,
                endpoint='render.html',
                args={'wait': 5},
            )

    def parse(self, response):
        self.url_counter += 1
        product_urls = response.xpath('//a[@class="relative db js-plp-hash "]/@href')

        for url in product_urls:
            yield SplashRequest(url.get(), callback=self.parse_item, meta={'url': url.get()}) # Convert to string

        load_more_buttons = response.xpath('//div[@class="js-load-more__button mb3"]/a/@href')
        if load_more_buttons:
            yield SplashRequest(
                url=response.urljoin(load_more_buttons[0].get()),
                callback=self.parse,
                endpoint='render.html',
                args={'wait': 5},
            )

    def parse_item(self, response):

        product_name = [name.get().replace('\n', '') for name in
                        response.xpath('//div[@class="w-60"]/h1/text()')]

        product_category = response.xpath('//a[@class="overflow-visible"]/text()')[1].get().replace('\n', '').replace(
            '\xa0', '')

        brand = [brand.get().replace('\n', '') for brand in
                 response.xpath('//div[@class="js-product-detail__product-brand flex"]/a//text()')]

        price = [price.get().replace('\n', '') for price in
                 response.xpath('//div[@class="product-price"]/span/span/text()')]

        image_url = response.xpath(
            '//div[@class="w-100 w-50-ns flex flex-column-ns overflow-auto js-product-detail__images-container"]/a/@href').getall()

        titles_and_urls = response.xpath(
            '//li[@class="ar-variations__swatch mb2 relative fn1 "]/a[@title]/@title | //li[@class="ar-variations__swatch mb2 relative fn1 "]/a/@href').getall()

        product_description = response.xpath(
            '//div[@class="ar-product-information__product-info-notes f0 cf pb2"]/descendant-or-self::*/text()')
        
        product_description = ' '.join(product_description.getall()).strip().replace('\n', '')


        details = [detail.get().replace(' ', '').replace('\n', '') for detail in
                   response.xpath('//div[@class="js-product-accordion__content"]/ul/li/text()')]

        size_fit = [size.get().replace('\n', '').replace(' ', '').replace('/', '').replace('\ "', ' ') for size in
                    response.xpath('//ul[@class="js-pdp-sizefit__list"]/li/text()')]

        reviews = response.xpath('//div[@class="TTreviewBody"]/text()').getall()
        if not reviews:
            reviews = "None"
        

        yield {
            'Product URL': response.url,
            'Product Name': product_name,
            'Product Category': product_category,
            'Brand': brand,
            'Price': price,
            'Image URL': image_url,
            'Product Colors & URL': titles_and_urls,
            'Product Description': product_description,
            'Details': details,
            'Size & Fit': size_fit,
            'Reviews': reviews
        }

        self.logger.info(f"Extracted data from {self.url_counter} URLs")


