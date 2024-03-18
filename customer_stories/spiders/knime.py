import scrapy
from scrapy_splash import SplashRequest

class KnimeSpider(scrapy.Spider):
    name = 'knime'
    start_urls = ['https://www.knime.com/customers']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, endpoint='execute',
                                args={'lua_source': self.load_more_lua})  

    load_more_lua = """
    function main(splash, args)
        splash:go(args.url)
        splash:wait(2)
        for _ = 1, 5 do 
            local load_more_button = splash:evaljs('document.querySelector("#gatsby-focus-wrapper > div > div.px-6.md\\\\:px-14.mb-12.md\\\\:mb-24 > div > div.text-center.mt-10.md\\\\:mt-12.lg\\\\:mt-20 > button")')
            if load_more_button then
                load_more_button:scroll_to()
                load_more_button:mouse_click()
                splash:wait(2)
            end
        end
        splash:wait(2)
        return {html = splash:html()}
    end
    """

    lua_script = """
        function main(splash, args)
            assert(splash:go(args.url))
            splash:wait(2)
            return {html = splash:html()}
        end
        """
    
    def parse(self, response):
        links = response.css('div.border.py-1 a[target="_self"]::attr(href)').getall()
        
        for link in links:
            absolute_url = response.urljoin(link)
            yield SplashRequest(absolute_url, self.parse_customer_story, endpoint='execute',
                                args={'lua_source': self.lua_script})

    def parse_customer_story(self, response):
        try:
            title = response.css('title::text').get()
            content = ' '.join(response.css('div.px-6 *::text').getall())
            content = content[:content.rfind('\n')+1]
            img_alt = response.css('div.logo-dots-bg img::attr(alt)').get()
            url = response.url
            yield {'company': img_alt, 'url': url, 'title': title, 'content': content}

        except Exception as e:  
            self.log('Error on %s: %s - Details: %s' % (response.url, type(e), e)) 
