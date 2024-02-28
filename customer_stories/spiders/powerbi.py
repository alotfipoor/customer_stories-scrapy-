import scrapy
from scrapy_splash import SplashRequest

class PowerBISpider(scrapy.Spider):
    name = 'powerbi'
    start_urls = ["https://customers.microsoft.com/en-us/search?sq=power%20bi&ff=story_product_categories%26%3EPower%20BI%26%26story_organization_size%26%3ESmall%20%281%20-%2049%20employees%29&p=5&so=story_publish_date%20desc"]

    LUA_SCRIPT = """
    function main(splash, args)
        splash:go(args.url)
        assert(splash:wait(1))
        return {
            html = splash:html(),
            }
    end
    """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute', args={'lua_source': self.LUA_SCRIPT})

    def parse(self, response):
        # Extract customer story links
        # links = response.css('a.search-result::attr(href)').getall()
        # for link in links:
            # absolute_url = response.urljoin(link)
            # yield SplashRequest(absolute_url, self.parse_customer_story, endpoint='execute', args={'lua_source': self.LUA_SCRIPT})

        # Save the whole website as an HTML file
        with open('website.html', 'wb') as f:
            f.write(response.body)

    def parse_customer_story(self, response):
        title = response.css('title::text').get()
        # content = response.css('section[id^="paragraph-id--"] > article > div > p*::text').getall()
        # content = ' '.join(response.css('article > div > p *::text').getall())
        # img_alt = response.css('div#main-content img::attr(alt)').get()
        # url = response.url
        yield {'title': title}
        # yield {'company': img_alt, 'url': url, 'title': title, 'content': content}
