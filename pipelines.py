# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


from scrapy import signals
from scrapy.exporters import CsvItemExporter
from scrapy.pipelines.files import FilesPipeline
from scrapy.http import Request
from scrapy.exceptions import DropItem
from scrapy import log

class MyFilePipeline(FilesPipeline):

    #Name download version
    def file_path(self, request, response=None, info=None):
        media_guid = request.meta['filename']
        log.msg(media_guid, level=log.DEBUG)
        return ('%s' % media_guid)

    def get_media_requests(self, item, info):
        yield Request(item['file_urls'][0], meta=item)


class CSVPipeline(object):

  def __init__(self):
    self.files = {}

  @classmethod
  def from_crawler(cls, crawler):
    pipeline = cls()
    crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
    crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
    return pipeline

  def spider_opened(self, spider):
    file = open('%s_items.csv' % spider.name, 'w+b')
    self.files[spider] = file
    self.exporter = CsvItemExporter(file)
    self.exporter.fields_to_export = ["filename", "titel", "publicatie", "dossiernummer", "organisatie", "publicatiedatum", "publicatietype", "file_urls"]
    self.exporter.start_exporting()

  def spider_closed(self, spider):
    self.exporter.finish_exporting()
    file = self.files.pop(spider)
    file.close()

  def process_item(self, item, spider):
    self.exporter.export_item(item)
    return item