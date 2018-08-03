import scrapy
from movie_scraper.items import Item


class FilmezzSpider(scrapy.Spider):
    """
        Scraper for exploring filmezz.eu site
    """
    ROOT_URL = 'http://filmezz.eu'
    name = 'filmezz_eu'  # basename of the spider
    start_urls = [
        'http://filmezz.eu/kereses.php'
    ]

    def parse(self, response):
        """Starting point for the scraper url: http://filmezz.eu/kereses.php"""
        container = response.css('div.container section#filmek')[0]
        for movie_cover in container.css('ul li'):
            url_param = movie_cover.css('a::attr(href)').extract_first()
            yield scrapy.Request(url='{}/{}'.format(self.ROOT_URL, url_param),
                                 callback=self.parse_movie_page)

    def parse_movie_page(self, response):
        """This is method gets called for each moviepage"""
        container = response.css('div.container.movie-page section.col-md-9')
        item = Item(vendor_name=self.name,
                    vendor_url=response.url)
        desc = container.css('div.description')
        if desc:
            titles = container.css('div.title')[0]
            item['name'] = titles.css('h1::text').extract_first(default='N/A')
            item['name_en'] = titles.css('h2::text').extract_first(default='N/A')
            item['description'] = desc[0].css('div.text::text').extract_first(default='N/A')
            item['categories'] = desc.css('ul.list-inline.category li a::text').extract()
        else:
            item['name'] = 'N/A'
            item['name_en'] = 'N/A'
            item['description'] = 'N/A'
            item['categories'] = []
        aside = response.css('aside div.sidebar-article.details')
        if aside:
            aside = aside[0]
            director, actors = aside.css('ul.list-unstyled')
            item['director'] = director.css('li a::text').extract_first(default='N/A')
            item['actors'] = actors.css('li a::text').extract()
        else:
            item['director'] = 'N/A'
            item['actors'] = []
        link_container = response.css("""div.container
                                         section.content-box
                                         ul.list-unstyled.table-horizontal.url-list""")[0]
        links = self._collect_links(link_container)


        yield item

    @staticmethod
    def _collect_links(link_container):
        import ipdb; ipdb.set_trace()
