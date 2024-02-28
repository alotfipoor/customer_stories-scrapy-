import scrapy
from scrapy_splash import SplashRequest
from urllib.parse import urlparse

class DashSpider(scrapy.Spider):
    name = 'dash'
    start_urls = ['https://plotly.com/user-stories/']

    LUA_SCRIPT = """
    function main(splash, args)
        splash:go(args.url)
        return {html = splash:html()}
    end
    """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': self.LUA_SCRIPT})

    def parse(self, response):
        # Extract customer story links
        links = response.css('div.css-t10rx1 a::attr(href)').getall()
        for link in links:
            absolute_url = response.urljoin(link)
            yield SplashRequest(absolute_url, self.parse_customer_story, endpoint='execute', args={'lua_source': self.LUA_SCRIPT})
        
        yield SplashRequest(
            url=response.url,
            callback=self.parse,
            endpoint='execute',
            args={
                'timeout': 1,
                'lua_source': """
                function main(splash, args)
                    splash:go(args.url)
                    assert(splash:wait(1))
                    return {
                        html = splash:html(),
                        url = splash:url(),
                    }
                end
                """,
                'url': response.url,
        }
        )    

    def parse_customer_story(self, response):
        try:            
            parsed_url = urlparse(response.url)
            img_alt = parsed_url.path.rstrip('/').split('/')[-1]
            title = response.css('title::text').get()
            content = ' '.join(response.css('p *::text').getall())
            url = response.url
            yield {'company': img_alt, 'url': url, 'title': title, 'content': content}
        except Exception as e:
            self.log('Error on %s: %s' % (response.url, e))