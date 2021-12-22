import scrapy


def transform_for_win(string):
    intab = "\/:*?<>|"
    outtab  = "-"*len(intab)
    trantab = str.maketrans(intab, outtab)
    return string.translate(trantab)

    
class ForbesBusinessSpider(scrapy.Spider):
    name = 'forbes_business'
    allowed_domains = ['forbes.com/business']
    start_urls = ['http://forbes.com/business/']

    def parse(self, response):
        # add dont_filter=True to make the sencond callback function functions
        # get articles at the top
        for link in response.css('a.headlink::attr(href)'):
            yield response.follow(link.get(), callback=self.parse_article, dont_filter=True)
        # get articles at the middle
        for link in response.css('a.chansec-special-feature__title-wrapper::attr(href)'):
            yield response.follow(link.get(), callback=self.parse_article, dont_filter=True)
        # get articles from More from Business
        for link in response.css('a.stream-item__title::attr(href)'):
            yield response.follow(link.get(), callback=self.parse_article, dont_filter=True)
        
    def parse_article(self, response):
        text = response.css('div.article-body.fs-article.fs-responsive-text.current-article').css('p *::text').getall()
        header = response.css('div.header-content-container').css('h1.fs-headline.speakable-headline.font-base.font-size::text').get()
        # some articles have different structures.
        if not header:
            text = response.css('div.video__description-text::text').get()
            header = response.css('h1.video__title-text::text').get()
        yield {
            'header': header,
            'word': text
        }
        # for windows system, filenames have limitations.
        if header:
            header = transform_for_win(header)
        filename = "forbes/outputs/" + header + ".txt"
        with open(filename, 'w+', encoding="utf-8") as f:
            f.writelines([p for p in text if "[+]" not in p])
        self.log(f'Saved file {filename}')