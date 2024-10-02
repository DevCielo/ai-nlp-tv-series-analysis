import scrapy
from bs4 import BeautifulSoup

class BlogSpider(scrapy.Spider):
    name = "narutospider"
    start_urls = ['https://naruto.fandom.com/wiki/Special:BrowseData/Jutsu?limit=250&offset=0&_cat=Jutsu']

    def parse(self, response):
        # iterates over the object we are trying to call
        for href in response.css('.smw-columnlist-container')[0].css("a::attr(href)").extract():
            # go to the href page to extract information
            extracted_data = scrapy.Request("https://naruto.fandom.com" + href, callback=self.parse_jutsu)
            yield extracted_data
            
            # iterates over the pages in the blog
            for next_page in response.css('a.mw-nextlink'):
                yield response.follow(next_page, self.parse)
    
    def parse_jutsu(self, response):
        # grabs the jutsu name for  a span with the classname and gets the text, as only 1 name just grabs the first
        jutsu_name = response.css('span.mw-page-title-main::text').extract()[0]

        # cleans the name
        jutsu_name = jutsu_name.strip()

        # grabs the jutsu description (select div first as all of it is in the same div)
        div_selector = response.css('div.mw-parser-output')[0]
        div_html = div_selector.extract() # extracts the html of the selector

        soup = BeautifulSoup(div_html).find('div') # grabs the first div in the html
        
        jutsu_type=""

        # get aside section
        if soup.find('aside'):
            aside = soup.find('aside')

            # loop over each row to find all divs with a class of pi_data and only grab the one that has a h3 called classification
            for cell in aside.find_all('div', {'class': 'pi-data'}):
                if cell.find('h3'):
                    cell_name = cell.find('h3').text.strip()
                    # get the value of the preceding div
                    if cell_name == 'Classification':
                        jutsu_type = cell.find('div').text.strip()

        # get the description (first remove the aside)
        soup.find('aside').decompose()

        jutsu_description = soup.get_text()
        # no clear seperator so split at trivia and get everything before it
        jutsu_description.split('Trivia')[0].strip()

        return dict (
            jutsu_name = jutsu_name,
            jutsu_type = jutsu_type,
            jutsu_description = jutsu_description
        )

