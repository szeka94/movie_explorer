from datetime import datetime
import json

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class CleaningPipeline(object):
    """Cleans and prepares the data"""

    JSON_FIELDS = [
        'actors',
        'categories',
        'links',
    ]

    def process_item(self, item, spider):
        return item

    def clean_item(self, item):
        LIST_FIELDS = [
            'actors',
            'categories'
        ]
        for key, value in item.items():
            if key in LIST_FIELDS:
                item[key] = [self._clean_unicode(data) for data in value]
            else:
                item[key] = self._clean_unicode(value)
        return item

    @staticmethod
    def _clean_unicode(data):
        data = data.split()
        return data

    @classmethod
    def _json_format_fields(cls, item):
        for field in cls.JSON_FIELDS:
            data = item[field]
            item[field] = json.dumps(data)
        return item

    @staticmethod
    def _add_timestamp(item):
        item['timestamp'] = datetime.now()
        return item

    @staticmethod
    def _clean_links(links):
        pass
