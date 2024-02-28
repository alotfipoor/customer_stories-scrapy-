import scrapy
from scrapy_splash import SplashRequest

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    start_urls = ['https://aws.amazon.com/quicksight/customers/']

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
        # Extract stories
        stories = response.css('div.lb-none-v-margin')
        for story in stories:
            title = story.css('h2::text').get()
            # content = ' '.join(story.css('p::text').getall())
            content = ' '.join(story.css('div.lb-col *::text').getall())
            content = ' '.join(content.split())


            yield {'company': title, 'utl': 'https://aws.amazon.com/quicksight/customers/', 'title':'', 'content': content}