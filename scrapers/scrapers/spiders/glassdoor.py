# -*- coding: utf-8 -*-
import scrapy

JOB_TITLE = "data+scientist"


class GlassdoorSpider(scrapy.Spider):
    name = 'glassdoor'
    allowed_domains = ['glassdoor.com']
    start_urls = [f"https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource="
                  f"searchBtn&typedKeyword={JOB_TITLE}&sc.keyword={JOB_TITLE}&locT=C&locId=2421090&jobType="
                  ]
    overall_pages = None
    current_page = 1

    def parse(self, response):

        overall_pages = response.css(".cell.middle.hideMob.padVertSm").xpath("text()").extract()[0].split()[-1]
        self.overall_pages = int(overall_pages)
        jobs_count = response.css("#MainColSummary .jobsCount::text").get().replace("\xa0", " ")
        current_page_jobs = response.css(".jobContainer")
        print(f"\n\nFound {jobs_count} {JOB_TITLE} on {overall_pages} pages\n\n")

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
        published = response.meta.get('published')
        title = response.css("div.css-17x2pwl.e11nt52q5").xpath("string()").extract_first()
        job_description = ' '.join(response.css('.desc.css-58vpdc.ecgq1xb3').xpath("text()").extract())
        yield {"title": title,
               "published": published,
               "easy_apply": response.meta.get("easy_apply"),
               "url": response.url,
               'description': job_description}

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
            page_url = self.start_urls[0] + f"p={self.current_page}"
            yield scrapy.Request(page_url, self.parse_pagination)
