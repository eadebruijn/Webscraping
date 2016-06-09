# Webscraping
Repository for webscrapers built in Python (using Scrapy). If you use this webscraper for commercial or academic purposes, please refer to it as <placeholder: ignore>

The code in most of the scrapers has not been optimized, nor does it follow PEP-8. Suggestions to improve readability and performance are appreciated.

To make the webscrapers work, follow the instructions on: http://doc.scrapy.org/en/latest/intro/install.html
Then using the command prompt, go the folder with the scrapy.cfg. I've included the following scrapers (You can find the files for each webscraper under OB\spiders):

-OBSpider (short for Officiele Bekendmakingen-Spider). Launch by typing scrapy crawl OB in the command prompt while being in the folder with the scrapy.cfg. This scraper downloads all pdf's for a given query. To alter the query, open the respective file and change the query to whatever you wish. 
-To do

Note that because of settings and pipelines, a csv-file with all the results will be posted after each initiated search. Furthermore, it will attempt to download files. 

