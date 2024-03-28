import scrapy
from scrapy_splash import SplashRequest

class LookerSpider(scrapy.Spider):
    name = 'looker'
    # allowed_domains = ['cloud.google.com']

    LUA_SCRIPT = """
    function main(splash, args)
        assert(splash:go(args.url))
      while not splash:select('div.cloud-card__footer') do
        splash:wait(0.1)
        print('waiting...')
      end
      return {html = splash:html()}
    end
    """
    def start_requests(self):
        start_urls = 'https://cloud.google.com/customers'
        yield SplashRequest(start_urls, self.parse, endpoint='execute', args={'wait': 0.5, 
                                                                              'lua_source': self.LUA_SCRIPT,
                                                                              'url' : 'https://cloud.google.com/customers'
                                                                              },
                            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'})

    def parse(self, response):
        links = response.css('#cloud-site > div > section:nth-child(7) > div > cloudx-gallery > div.cloud-card__container.cloud-card__container--3up > div:nth-child(2) > div.cloud-card__footer > a::attr(href)').getall()
        # links = response.css('div.cloud-card__footer a::attr(href)').getall()
        print('@@@@@@@@@@@@')
        print(links)
    #     for link in links:
    #         absolute_url = response.urljoin(link)
    #         yield SplashRequest(absolute_url, self.parse_customer_story, endpoint='execute', args={'lua_source': self.LUA_SCRIPT})

    # def parse_customer_story(self, response):
    #     title = response.css('title::text').get()
    #     # content = response.css('section[id^="paragraph-id--"] > article > div > p*::text').getall()
    #     # content = ' '.join(response.css('article > div > p *::text').getall())
    #     # img_alt = response.css('div#main-content img::attr(alt)').get()
    #     # url = response.url
    #     yield {'title': title}
    #     # yield {'company': img_alt, 'url': url, 'title': title, 'content': content}
