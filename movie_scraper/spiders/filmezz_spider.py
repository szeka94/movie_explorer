import scrapy
from movie_scraper.items import MovieItem
import urllib
from PIL import Image
import pytesseract
import io
import requests


class FilmezzSpider(scrapy.Spider):
    """Scraper for exploring filmezz.eu site"""

    ROOT_URL = 'http://filmezz.eu'
    name = 'filmezz_eu'  # basename of the spider
    start_urls = [
        'http://filmezz.eu/kereses.php'
    ]

    def parse(self, response):
        index = 0
        headline = response.css('div.container section#filmek h1.headline span::text')[0]
        text = headline.extract()
        num_of_movies = int(text.split('(')[1].replace(' db)', ''))
        for _ in range(0, num_of_movies, 24):
            url = '{root_url}/kereses.php?p={page_num}'.format(root_url=self.ROOT_URL,
                                                               page_num=index)
            index += 1
            yield scrapy.Request(url, callback=self.parse_search_page)

    def parse_search_page(self, response):
        """Starting point for the scraper url: http://filmezz.eu/kereses.php"""
        container = response.css('div.container section#filmek')
        for movie_cover in container.css('ul li'):
            url_param = movie_cover.css('a::attr(href)').extract_first()
            yield scrapy.Request(url='{}/{}'.format(self.ROOT_URL, url_param),
                                 callback=self.parse_movie_page)

    def parse_movie_page(self, response):
        """This is method gets called for each moviepage"""
        container = response.css('div.container.movie-page section.col-md-9')
        item = MovieItem(vendor_name=self.name,
                         vendor_url=response.url)
        item['image_path'] = container.css('img::attr(src)').extract_first(default='n/a')
        item['vendor_id'] = response.url.split('?n=')[-1]
        desc = container.css('div.description')
        titles = container.css('div.title')
        if titles:
            titles = titles[0]
            item['name'] = titles.css('h1::text').extract_first(default='n/a')
            item['name_en'] = titles.css('h2::text').extract_first(default='n/a')
            item['description'] = desc[0].css('div.text::text').extract_first(default='n/a')
            item['categories'] = desc.css('ul.list-inline.category li a::text').extract()
        aside = response.css('aside div.sidebar-article.details')
        if aside:
            aside = aside[0]
            director, actors = aside.css('ul.list-unstyled')
            item['director'] = director.css('li a::text').extract_first(default='n/a')
            item['actors'] = actors.css('li a::text').extract()
        else:
            item['director'] = 'n/a'
            item['actors'] = []
        link_container = response.css("""div.container
                                         section.content-box
                                         ul.list-unstyled.table-horizontal.url-list""")
        if not link_container:
            # if cannot scrape links, continue
            return
        else:
            link_container = link_container[0]
        links = [data.css('div') for data in link_container.css('li')[1:] if data.css('div')]
        collected_links, is_series = self._collect_links(links)
        item['is_series'] = is_series
        item['links'] = collected_links
        yield item

    def _collect_links(self, links):
        is_series = None
        collected_links = dict()
        for link in links:
            lang = link.css('ul li::attr(title)').extract_first()
            link_host_container = [data.strip() for data in link[0].css('::text').extract()
                                   if data.strip()]
            episode = link[2].css('::text').extract_first().strip()
            if is_series is None:
                is_series = episode != ''
            host_name = link_host_container[0].strip() if link_host_container else 'n/a'
            link_url = link[-1].css('a::attr(href)').extract_first(default='n/a')
            site_link = urllib.parse.unquote(link_url.split('/')[-1])
            try:
                movie_url = self._get_movie_url(site_link)
            except (ValueError, NotImplementedError) as e:
                print('ERROR: {}'.format(e))
            if is_series:
                same_episode = collected_links.get(episode, {})
                link_list = same_episode.get(host_name, [])
                link_list.append((movie_url, lang))
                same_episode[host_name] = link_list
                collected_links[episode] = same_episode
            else:
                link_list = collected_links.get(host_name, [])
                link_list.append((movie_url, lang))
                collected_links[host_name] = link_list
        return collected_links, is_series

    def _get_movie_url(self, site_link):
        session = requests.session()
        resp_site = session.get(site_link, allow_redirects=False)
        if resp_site.status_code in [301, 302]:
            # Redirect to the movie page
            # url can be accessed from the headers
            movie_url = resp_site.headers['location']
        elif 'captchaimg.php' in resp_site.text:
            # Solve the captha
            session.headers.pop('Accept-Encoding')
            resp_img = session.get('http://filmezz.eu/captchaimg.php')
            im = Image.open(io.BytesIO(resp_img.content))
            text = pytesseract.image_to_string(im, lang='eng', config='--psm 7')
            text = text.strip() \
                       .replace(':', '') \
                       .replace('O', '0')
            result = sum([int(num) for num in text.split('+')])
            form_data = {'captcha': result}
            resp = session.post(site_link, data=form_data, allow_redirects=False)
            movie_url = resp.url
        else:
            raise NotImplementedError('This error shouldn\'t happen')
        return movie_url
