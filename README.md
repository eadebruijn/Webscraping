# Webscraping
Repository for webscrapers built in Python (using Scrapy). If you use this webscraper for commercial or academic purposes, please refer to it as <placeholder: ignore>

The code in most of the scrapers has not been optimized, nor does it follow PEP-8. Suggestions to improve readability and performance are appreciated.

To make the webscrapers work, first follow the instructions on: http://doc.scrapy.org/en/latest/intro/install.html
Then using the command prompt, use the 'scrapy startproject OB' command and go the folder with the scrapy.cfg. You can now copy-paste files from this repository to their respective places. Note that 2 files (XMLBOT and OBSpiderbot) belong in the spiders subfolder. If you chose any other projectname than OB, several lines of code need to be changed in the settings-file, where OB should be changed to the name you've given your folder. Opening these files is most easily done with programs such as Notepad++. 

I've included the following scrapers:

-OBSpider (short for Officiele Bekendmakingen-Spider). Launch by typing scrapy crawl OB in the command prompt while being in the folder with the scrapy.cfg. This scraper downloads all pdf's for a given query. To alter the query, open the respective file and change the query to whatever you wish. Not that the code for this bot is very unrefined. 
-XMLBOT. Launch by typing scrapy crawl XMLBOT. This bot searched officiele bekendmakingen for questions asked by MP's. It then returns the files in XML-format, as long as officielebekendmakingen.nl provides them. 

Note that because of settings and pipelines, a csv-file with all the results will be posted after each initiated search. Also, scrapy will save files to C:/filesfromscrapy
