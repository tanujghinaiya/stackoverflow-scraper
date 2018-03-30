from enum import Enum
from bs4 import BeautifulSoup

from soscrape.cleaners.text import clean_text
from soscrape.scrapers.question_scraper import QuestionScraper
from soscrape.session import get_session

STACK_OVERFLOW_BASE_URL = "https://stackoverflow.com"


class TagSearchSort(Enum):
    NEWEST = "newest"
    FREQUENT = "frequent"
    VOTES = "votes"
    ACTIVE = "active"


class TagSearchScraper:
    URL = "{}/questions/tagged".format(STACK_OVERFLOW_BASE_URL)

    def __init__(self, tags, max_pages=-1, sort=TagSearchSort.NEWEST, page_size=50, session=None):
        if isinstance(tags, str):
            tags = (tags,)

        if not isinstance(tags, (list, tuple)):
            raise TypeError("expected type string, list or tuple for tags")

        if sort not in TagSearchSort:
            raise TypeError("expected one of {}".format(TagSearchSort))

        self.tags = tags
        self.n_pages = -1
        self.max_pages = max_pages
        self.sort = sort
        self.page_size = page_size

        self.session = session or get_session()

    def get_questions(self):
        current_page = 1
        questions = []

        while self.n_pages == -1 or current_page <= self.n_pages:
            if self.max_pages is not -1 and current_page > self.max_pages:
                break

            questions.extend(self.scrape_page(current_page))
            current_page += 1

        print("Found {} questions".format(len(questions)))

        return questions

    def scrape_page(self, page=1, limit=None):
        print("scraping page {} from {}...".format(page, self.url))
        params = dict(
            page=page,
            sort=self.sort,
            pageSize=self.page_size
        )

        res = self.session.get(self.url, params=params)
        soup = BeautifulSoup(res.content, "lxml")

        if self.n_pages == -1:
            self.n_pages = self.get_no_of_pages(soup)

        question_summaries = soup.find_all("div", {"class": "question-summary"}, limit=limit)

        return map(self.parse_question_from_question_summary, question_summaries)

    @staticmethod
    def get_no_of_pages(page_soup):
        page_link = page_soup.find("div", {"class": "pager"}).find_all("a")
        n_pages = int(page_link[-2].find("span", {"class": "page-numbers"}).text)
        print("found {} pages".format(n_pages))
        return n_pages

    @staticmethod
    def parse_question_from_question_summary(page_soup):
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
            question=QuestionScraper(url).scrape()
        )

    @property
    def url(self):
        return "{}/{}".format(TagSearchScraper.URL, "+".join(self.tags))


if __name__ == '__main__':
    # for i in range(200):
    #     print(i)
    t = ("audio", "speech")
    # t = "java"
    s = TagSearchScraper(t)
    q = s.get_questions()

    print(q)
    print("done")
