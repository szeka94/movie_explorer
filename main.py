from scrapy import cmdline
cmdline.execute("scrapy crawl filmezz_eu --loglevel=INFO -o result.json".split())
