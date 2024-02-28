import scrapy
from scrapy_splash import SplashRequest

class TableauSpider(scrapy.Spider):
    name = 'tableau'
    start_urls = ['https://www.tableau.com/en-gb/solutions/customers']

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
        links = response.css('div.card.relative h3.card__title a::attr(href)').getall()
        for link in links:
            absolute_url = response.urljoin(link)
            yield SplashRequest(absolute_url, self.parse_customer_story, endpoint='execute', args={'lua_source': self.LUA_SCRIPT})
        
        yield SplashRequest(
            url=response.url,
            callback=self.parse,
            endpoint='execute',
            args={
                'timeout': 3,
                'lua_source': """
                function main(splash, args)
                    splash:go(args.url)
                    assert(splash:wait(1))
                    for i=1,10 do
                        assert(splash:wait(1))
                        splash:runjs('document.querySelector("ul.js-pager__items.pager li.pager__item a.link.link--expand").click()')
                        splash:runjs("window.scrollTo(0, document.body.scrollHeight);")
                        ssert(splash:wait((1)))
                    end
                    assert(splash:wait((2)))
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
            title = response.css('title::text').get()
            # content = response.css('section[id^="paragraph-id--"] > article > div > p*::text').getall()
            content = ' '.join(response.css('article > div > p *::text').getall())
            img_alt = response.css('div#main-content img::attr(alt)').get()
            url = response.url
            yield {'company': img_alt, 'url': url, 'title': title, 'content': content}
        except Exception as e:
            self.log('Error on %s: %s' % (response.url, e))