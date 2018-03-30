from enum import Enum
from bs4 import BeautifulSoup

from soscrape.session import get_session


class AnswerTab(Enum):
    ACTIVE = "active"
    OLDEST = "oldest"
    VOTES = "votes"


class QuestionScraper:
    def __init__(self, url, answer_tab=AnswerTab.ACTIVE, session=None):
        self.url = url
        self.answer_tab = answer_tab
        self.session = session or get_session()

    def scrape(self):
        print("scraping question from {}".format(self.url))
        res = self.session.get(self.url, params=dict(answertab=self.answer_tab))
        soup = BeautifulSoup(res.content, "lxml")

        return dict(
            question=self.scrape_post(soup.find("div", {"class": "question"})),
            answers=[self.scrape_post(answer) for answer in soup.find_all("div", {"class": "answer"})]
        )

    @staticmethod
    def scrape_post(post_soup):
        return dict(
            body=post_soup.find("div", {"class": "post-text"}).text,
            comments=QuestionScraper.scrape_comments(post_soup)
        )

    @staticmethod
    def scrape_comments(soup):
        return [comment_soup.text for comment_soup in soup.find_all("span", {"class": "comment-copy"})]

    @classmethod
    def from_question(cls, question):
        return QuestionScraper(question["url"])
