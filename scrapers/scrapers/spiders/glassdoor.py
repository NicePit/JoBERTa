# -*- coding: utf-8 -*-
import scrapy

JOB_TITLE = "python+developer"


class GlassdoorSpider(scrapy.Spider):
    name = 'glassdoor'
    allowed_domains = ['glassdoor.com']
    start_urls = [f"https://www.glassdoor.com/Job/jobs.htm?suggestCount=0&suggestChosen=false&clickSource="
                  f"searchBtn&typedKeyword={JOB_TITLE}&sc.keyword={JOB_TITLE}&locT=C&locId=2421090&jobType="
                  ]

    def parse(self, response):
        print(self.start_urls[0])
        jobs_count = response.css("#MainColSummary .jobsCount::text").get().replace("\xa0", " ")
        current_page_jobs = response.css(".jobContainer")
        print(f"Found {jobs_count}")

        for job in current_page_jobs:
            job_relative_url = job.css(".jobHeader a::attr(href)").extract_first()
            job_url = response.urljoin(job_relative_url)
            published = job.css(".jobLabel.nowrap").xpath("string()").extract_first().strip()
            yield scrapy.Request(job_url, self.parse_details, meta={'published': published})

    def parse_details(self, response):
        published = response.meta.get('published')
        title = response.css("div.css-17x2pwl.e11nt52q5").xpath("string()").extract_first()
        yield {"title": title,
               "published": published,
               "url": response.url}
