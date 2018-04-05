import json

from enum import Enum
from bs4 import BeautifulSoup

from soscrape.cleaners.text import clean_text
from soscrape.scrapers.question_scraper import QuestionScraper
from soscrape.utils.session import get_session
from soscrape.utils.request_handler import RequestsHandler

STACK_OVERFLOW_BASE_URL = "https://stackoverflow.com"


class TagSearchSort(Enum):
    NEWEST = "newest"
    FREQUENT = "frequent"
    VOTES = "votes"
    ACTIVE = "active"


class TagSearchScraper:
    URL = "{}/questions/tagged".format(STACK_OVERFLOW_BASE_URL)

    def __init__(self, tags, save_to=None, max_pages=-1, sort=TagSearchSort.NEWEST, page_size=50, session=None):
        if isinstance(tags, str):
            tags = (tags,)

        if not isinstance(tags, (list, tuple, set)):
            raise TypeError("expected type string, list or tuple for tags")

        if sort not in TagSearchSort:
            raise TypeError("expected one of {}".format(TagSearchSort))

        self.tags = tags
        self.n_pages = -1
        self.max_pages = max_pages
        self.sort = sort
        self.page_size = page_size
        self.session = session
        self.save_to = save_to

    def __call__(self, requests_handler=None):
        self.scrape_questions(requests_handler=requests_handler)

    def scrape_questions(self, requests_handler=None):
        current_page = 1
        scraped_content = []

        questions = dict(
            tags=self.tags,
            questions=scraped_content
        )

        requests_handler = requests_handler or self.session or get_session()

        try:
            while self.n_pages == -1 or current_page <= self.n_pages:
                if self.max_pages is not -1 and current_page > self.max_pages:
                    break

                question_summaries = self.scrape_page(requests_handler, current_page)

                for question_summary in question_summaries:
                    scraped_content.append(self.parse_question_from_question_summary(question_summary, requests_handler))
                    self.write_to_json(questions, self.save_to)

                current_page += 1
        finally:
            self.write_to_json(questions, self.save_to)

        print("Found {} questions".format(len(questions)))

        return questions

    def scrape_page(self, request_handler, page=1, limit=None):
        print("scraping page {} from {}...".format(page, self.url))
        params = dict(
            page=page,
            sort=self.sort,
            pageSize=self.page_size
        )

        res = request_handler.get(self.url, params=params)
        soup = BeautifulSoup(res.content, "lxml")

        if self.n_pages == -1:
            self.n_pages = self.get_no_of_pages(soup)

        question_summaries = soup.find_all("div", {"class": "question-summary"}, limit=limit)

        return question_summaries

    @staticmethod
    def get_no_of_pages(page_soup):
        page_link = page_soup.find("div", {"class": "pager"}).find_all("a")
        n_pages = int(page_link[-2].find("span", {"class": "page-numbers"}).text)
        print("found {} pages".format(n_pages))
        return n_pages

    @staticmethod
    def parse_question_from_question_summary(page_soup, request_handler):
        link = page_soup.find("a", {"class": "question-hyperlink"})
        url = "{}{}".format(STACK_OVERFLOW_BASE_URL, link.get("href"))

        excerpt = page_soup.find("div", {"class": "excerpt"}).text
        excerpt = clean_text(excerpt)

        return dict(
            url=url,
            title=link.text,
            excerpt=excerpt,
            tags=[
                dict(
                    url="{}{}".format(STACK_OVERFLOW_BASE_URL, tag.get("href")),
                    tag=tag.text
                )
                for tag in page_soup.find_all("a", {"class": "post-tag"})
            ],
            question=QuestionScraper(url).scrape(request_handler)
        )

    @property
    def url(self):
        return "{}/{}".format(TagSearchScraper.URL, "+".join(self.tags))

    @classmethod
    def from_tag_sets(cls, tag_sets):
        return [
            cls(tags) for tags in tag_sets
        ]

    def write_to_json(self, questions, file_path):
        if self.save_to is None:
            return
        with open(file_path, 'w') as f:
            json.dump(questions, f, indent=4)


if __name__ == '__main__':
    # for i in range(200):
    #     print(i)
    t = ("audio", "speech")
    # t = "java"
    s = TagSearchScraper(t, save_to='r.json', max_pages=1, page_size=10)
    r = RequestsHandler()
    q = s.scrape_questions(r)

    print(q)
    print("done")
