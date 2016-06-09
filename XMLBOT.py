# -*- coding: utf-8 -*-
"""
THIS PROGRAM FINDS - GIVEN A SPECIFIC QUERY - ALL KAMERVRAGEN IN XML-FORMAT

This bot requires various modules to be installed. See http://doc.scrapy.org/en/latest/intro/install.html
This code is freely distributable. Mistakes or obtuse coding may be present in the bot

for questions, contact e.a.debruijn @ fsw.eur.nl

This bot is constructed in such a way, that after installing the necessary modules and programs, you only need to alter query and max_pages below and it will function properly. 
Due to code under settings.py, the bot will automatically save a csv-file. 

Be sure to import the .csv in excel in such a way that the language is unicode (UTF-8). Else, umlauts etc. will not display properly. See: https://help.tune.com/marketing-console/how-to-import-a-unicode-csv-to-excel/
"""
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from scrapy.http import Request
import re
import urlparse

class ThingsToGather(Item):
	titel = Field()
	publicatiedatum_vragen = Field()
	urlsite = Field()
	file_urls = Field()
	files = Field()
	filename = Field()
	
query = 'ENTER A QUERY HERE'

class pagespider(Spider):
	name = "XMLBOT"
	max_pages = 100
	
	def start_requests(self):
		for i in range(self.max_pages):
			yield scrapy.Request(''.join("https://zoek.officielebekendmakingen.nl/zoeken/resultaat/?zkt=Uitgebreid&pst=ParlementaireDocumenten&vrt="+ query + "&zkd=InDeGeheleText&dpr=Alle&spd=20160422&epd=20160422&kmr=EersteKamerderStatenGeneraal|TweedeKamerderStatenGeneraal|VerenigdeVergaderingderStatenGeneraal&sdt=KenmerkendeDatum&par=Kamervragen+zonder+antwoord&dst=Opgemaakt|Opgemaakt+na+onopgemaakt&isp=true&pnr=1&rpp=10&_page=%s&sorttype=1&sortorder=4") % (i), callback = self.parse)

	def parse(self, response):
		for sel in response.xpath('//div[@class = "lijst"]/ul/li'):
			deeplink = ''.join(["https://zoek.officielebekendmakingen.nl/", ' '.join(sel.xpath('a/@href').extract())])
			request = scrapy.Request(deeplink, callback=self.get_page_info)
			yield request
		
	def get_page_info(self, response):
		item = ThingsToGather()
		item['urlsite'] = urlparse.urljoin("https://zoek.officielebekendmakingen.nl/", ''.join(response.xpath('//*[@id="permaHyperlink"]/@href').extract()))
		if item['urlsite'] == "https://zoek.officielebekendmakingen.nl/": 
			item['urlsite'] = response.url
		tech_inf_link = ''.join(["https://zoek.officielebekendmakingen.nl/", ' '.join(response.xpath('//*[@id="technischeInfoHyperlink"]/@href').extract())])
		item["file_urls"] = 'https://zoek.officielebekendmakingen.nl/' + ' '.join(response.xpath('//*[@id="downloadXmlHyperLink"]/@href').extract())
		if item["file_urls"] == 'https://zoek.officielebekendmakingen.nl':
			item["file_urls"] = response.url
		item['file_urls'] = [ '' + item['file_urls'] ]
		request = scrapy.Request(tech_inf_link, callback=self.get_tech_info, dont_filter = True)
		request.meta['item'] = item
		yield request
		
	def get_tech_info(self, response):
		item = response.meta['item']
		item['titel'] = response.xpath('//span[contains(@property, "http://purl.org/dc/terms/title")]/text()').extract()
		item['publicatiedatum_vragen'] = response.xpath('//span[contains(@property, "http://purl.org/dc/terms/available")]/text()').extract()
		item['filename'] = ' '.join(response.xpath('//*[@id="downloadXmlHyperLink"]/@href').extract())
		yield item