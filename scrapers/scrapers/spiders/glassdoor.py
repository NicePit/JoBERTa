# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

from ..items import ScrapersItem

JOB_TITLES = ["data+scientist"]


#
# JOB_TITLES = ["data+scientist", 'data+engineer', 'researcher', 'machine+learning+engineer', 'deep+learning',
#               'python+developer']


class GlassdoorSpider(scrapy.Spider):
    name = 'glassdoor'
    allowed_domains = ['glassdoor.com']
    start_urls = [f"https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource="
                  f"searchBtn&typedKeyword={JOB_TITLE}&sc.keyword={JOB_TITLE}&locT=C&locId=2421090&jobType=" for
                  JOB_TITLE in JOB_TITLES
                  ]
    overall_pages = None
    current_page = 1

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)

    def parse(self, response):

        overall_pages = response.css(".cell.middle.hideMob.padVertSm").xpath("text()").extract()[0].split()[-1]
        self.overall_pages = int(overall_pages)
        jobs_count = response.css("#MainColSummary .jobsCount::text").get().replace("\xa0", " ")
        current_page_jobs = response.css(".jobContainer")
        print(f"\n\nFound {jobs_count} for current position on {overall_pages} pages\n\n")

        for job in current_page_jobs:
            easy_apply = True if len(job.css(".easyApply")) > 0 else False
            published = job.css(".jobLabel.nowrap").xpath("string()").extract_first().strip()
            job_relative_url = job.css(".jobHeader a::attr(href)").extract_first()
            job_url = response.urljoin(job_relative_url)
            yield scrapy.Request(job_url, self.parse_details, meta={'published': published, "easy_apply": easy_apply})

        self.current_page += 1
        page_url = self.start_urls[0] + f"p={self.current_page}"
        yield scrapy.Request(page_url, self.parse_pagination)

    def parse_details(self, response):
        items = ScrapersItem()
        published = response.meta.get('published')
        title = response.css("div.css-17x2pwl.e11nt52q5").xpath("string()").extract_first()
        job_description_1 = ' '.join(response.css("#JobDescriptionContainer .desc").xpath("string()").extract())
        job_description_2 = ' '.join(response.css("#JobDescriptionContainer .desc li").xpath("string()").extract())
        job_description = job_description_1 + ' ' + job_description_2
        rating = response.css(".css-1pmc6te.e11nt52q3").xpath("text()").extract_first()
        company_name = response.css(".css-16nw49e.e11nt52q1").xpath("text()").extract_first()
        items['rating'] = rating
        items['title'] = title
        items['published'] = published,
        items['easy_apply'] = response.meta.get("easy_apply"),
        items['url'] = response.url,
        items['description'] = job_description
        items['company_name'] = company_name

        # This is very slow part because of selenium. Can be commented out for faster scraping
        self.driver.get(response.url)
        self.driver.find_element_by_css_selector(".css-1iqg1r5.e1eh6fgm0").click()
        company_size = self.driver.find_elements_by_css_selector("#InfoFields .css-vugejy.es5l5kg0 span")[1].text
        items['company_size'] = company_size

        yield items

    def parse_pagination(self, response):
        print(f"\n\nParsing page #{self.current_page}\n\n")
        current_page_jobs = response.css(".jobContainer")
        for job in current_page_jobs:
            easy_apply = True if len(job.css(".easyApply")) > 0 else False
            published = job.css(".jobLabel.nowrap").xpath("string()").extract_first().strip()
            job_relative_url = job.css(".jobHeader a::attr(href)").extract_first()
            job_url = response.urljoin(job_relative_url)
            yield scrapy.Request(job_url, self.parse_details, meta={'published': published, "easy_apply": easy_apply})
        while self.current_page <= self.overall_pages:
            self.current_page += 1
            page_url = self.start_urls[0] + f"&p={self.current_page}"
            yield scrapy.Request(page_url, self.parse_pagination)
