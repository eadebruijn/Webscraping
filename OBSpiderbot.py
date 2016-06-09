""""
This code is very unrefined.

Spiderbot made by Ewald de Bruijn to scrape officiele bekendmakingen
This bot requires various modules to be installed. See http://doc.scrapy.org/en/latest/intro/install.html
This code is freely distributable. Mistakes or obtuse coding may be present in the bot

for questions, contact e.a.debruijn @ fsw.eur.nl

This bot is constructed in such a way, that after installing the necessary modules and programs, you only need to alter query and max_pages below and it will function properly. 
Due to code under settings.py, the bot will automatically save a csv-file. 

Be sure to import the .csv in excel in such a way that the language is unicode (UTF-8). Else, umlauts etc. will not display properly. See: https://help.tune.com/marketing-console/how-to-import-a-unicode-csv-to-excel/
"""

#first imports the necessary modules
import scrapy
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.item import Item, Field
from scrapy.http import Request
import re

#then the items (columns) for the eventual .csv file are defined. "File_urls" and "files" are needed so scrapy downloads the files and saves it under a specific name, instead of a random name. They won't show in 
#the excel file that is automatically generated. The class below contains all the items that are gathered. It is also refered to as an item-dict below. 

class ThingsToGather(Item):
	filename = Field()
	titel = Field()
	publicatie = Field()
	dossiernummer = Field()
	organisatie = Field()
	publicatiedatum = Field()
	publicatietype = Field()
	file_urls = Field()
	files = Field()
	
#fill in your search query here.
query = "'gaswinning Groningen'"

	
class pagespider(Spider):
	name = "OB"
#max_page is put here to prevent endless loops; make it as large as you need. It will try and go up to that page
#even if there's nothing there. A number too high will just take way too much time and yield no results
	max_pages = 100

#the bot then starts loading all the websites. If max_pages is 3 for example, it will load the first three pages of the index (even if more pages exist)
	def start_requests(self):
		for i in range(self.max_pages):
			yield scrapy.Request(''.join("https://zoek.officielebekendmakingen.nl/zoeken/resultaat/?zkt=Uitgebreid&pst=ParlementaireDocumenten&vrt="+ query + "&zkd=InDeGeheleText&dpr=AnderePeriode&spd=19950101&epd=20151231&kmr=TweedeKamerderStatenGeneraal&sdt=KenmerkendeDatum&par=Agenda|Handeling|Kamerstuk|Aanhangsel+van+de+Handelingen|Kamervragen+zonder+antwoord&dst=Onopgemaakt|Opgemaakt|Opgemaakt+na+onopgemaakt&isp=true&pnr=1&rpp=10&_page=%d&sorttype=1&sortorder=4") % (i+1), callback = self.parse)


#when you use officielebekendmakingen to search for a keyword, it always shows a list of max 30 pages - which we ignore - , with each page containing 10 entries. These entries refer to documents.			
#for each pages of the index, the title of the entry is saved and a request is sent out to go to that page (called deeplink). 
	def parse(self, response):
		#for each entry in the list (of max 10 entries)
		for sel in response.xpath('//div[@class = "lijst"]/ul/li'):
			#gather the entry name and put it in our item-dict
			item = ThingsToGather()
			item["titel"] = ' '.join(sel.xpath('a/text()').extract())
			#gather the link to the page of the entry and send out a request, remembering the item-dict
			deeplink = ''.join(["https://zoek.officielebekendmakingen.nl/", ' '.join(sel.xpath('a/@href').extract())])
			request = scrapy.Request(deeplink, callback=self.get_page_info)
			request.meta['item'] = item
			yield request

#It then proceees to check out the link of the entry
#it loads some general info from the header. If this string is less than 5 characters, the site probably is a faulthy link (i.e. an error 404). If this is the case, then it drops the item. Else it continues
	def get_page_info(self, response):
		#for everything in the main content of the page
		for sel in response.xpath('//*[@id="Inhoud"]'):
			item = response.meta['item']
			#check whether the page is not faulthy by loading a part of the website that does not show with a 404-error. If it's not on the page, then it must be an error 404.
			if len(' '.join(sel.xpath('//div[contains(@class, "logo-nummer")]/div[contains(@class, "nummer")]/text()').extract())) < 5:
				print ("ERROR404: %S" % response.url)
			else:

#it then indexes various data on the site. This data is only present for 'bijlagen' and not for other types of documents
				item["publicatie"] = sel.xpath('//span[contains(@property, "http://standaarden.overheid.nl/oep/meta/publicationName")]/text()').extract()
				item["dossiernummer"] = sel.xpath('//span[contains(@property, "http://standaarden.overheid.nl/oep/meta/dossiernummer")]/text()').extract()
				item["filename"] = ' '.join(sel.xpath('//*[@id="downloadPdfHyperLink"]/@href').extract())
				item["organisatie"] = sel.xpath('//span[contains(@property, "http://purl.org/dc/terms/creator")]/text()').extract()		
				item['publicatiedatum'] = sel.xpath('//span[contains(@property, "http://purl.org/dc/terms/available")]/text()').extract()
				item["publicatietype"] = sel.xpath('//span[contains(@property, "http://purl.org/dc/terms/type")]/text()').extract()
				item = self.__normalise_item(item, response.url)
				
#if the string is less than 5, then the page does not contain technical information on the entry. It then needs to be
#retrieved from the technical information link. If it's the proper link (the else clause), you're done and the bot proceeds to download the files
#normalize (see below) has to occur before len, since it won't calculate then length if it's not 'normalized'

				if len(item['publicatiedatum']) < 5:
					tech_inf_link = ''.join(["https://zoek.officielebekendmakingen.nl/", ' '.join(sel.xpath('//*[@id="technischeInfoHyperlink"]/@href').extract())])
					request = scrapy.Request(tech_inf_link, callback=self.get_date_info)
					request.meta['item'] = item
					yield request 
				else:
#downloads files			
					item["file_urls"] = 'https://zoek.officielebekendmakingen.nl' + ' '.join(sel.xpath('//*[@id="downloadPdfHyperLink"]/@href').extract())
					item['file_urls'] = [ '' + item['file_urls'] ]
					yield item

#if the entry was not a 'bijlage', the technical information link is loaded and the data from the netry is indexed. 
	def get_date_info (self, response):
		for sel in response.xpath('//*[@id="Inhoud"]'):
			item = response.meta['item']
			item["publicatie"] = sel.xpath('//span[contains(@property, "http://standaarden.overheid.nl/oep/meta/publicationName")]/text()').extract()
			item["dossiernummer"] = sel.xpath('//span[contains(@property, "http://standaarden.overheid.nl/oep/meta/dossiernummer")]/text()').extract()
			item["filename"] = ' '.join(sel.xpath('//*[@id="downloadPdfHyperLink"]/@href').extract())
			item["organisatie"] = sel.xpath('//span[contains(@property, "http://purl.org/dc/terms/creator")]/text()').extract()
			item['publicatiedatum'] = sel.xpath('//span[contains(@property, "http://purl.org/dc/terms/available")]/text()').extract()
			item["publicatietype"] = sel.xpath('//span[contains(@property, "http://purl.org/dc/terms/type")]/text()').extract()	
			item = self.__normalise_item(item, response.url)
#downloads files via pipeline; pipeline requires a file_urls item in the itemdict. Changing the name causes an error. 
			item["file_urls"] = 'https://zoek.officielebekendmakingen.nl' + ' '.join(sel.xpath('//*[@id="downloadPdfHyperLink"]/@href').extract())
			if item["file_urls"] == 'https://zoek.officielebekendmakingen.nl':
				item["file_urls"] = response.url
			item['file_urls'] = [ '' + item['file_urls'] ]
			return item
		
# commands below are intended to clean up strings. Everything is sent to __normalise_item to clean unwanted characters (strip) and double spaces (split and " ".join)

	def __normalise_item(self, item, base_url):
		for key, value in vars(item).values()[0].iteritems():
			item[key] = self.__normalise(item[key])
		
		item ['dossiernummer']= item['dossiernummer'].replace(';', '-')
		item ['titel']= item['titel'].replace(';', '& ')
		return item
		
	def __normalise(self, value):
		value = value if type(value) is not list else ' '.join(value)
		value = value.strip()
		value = " ".join(value.split())
		return value
