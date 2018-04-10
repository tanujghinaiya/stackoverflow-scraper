from enum import Enum
from bs4 import BeautifulSoup

from soscrape.utils.session import get_session


class AnswerTab(Enum):
    ACTIVE = "active"
    OLDEST = "oldest"
    VOTES = "votes"


class QuestionScraper:
    def __init__(self, url, answer_tab=AnswerTab.ACTIVE, session=None, tag_blacklist=("pre",), tag_whitelist=("a",)):
        self.url = url
        self.answer_tab = answer_tab
        self.session = session
        self.tag_blacklist = tag_blacklist
        self.tag_whitelist = tag_whitelist

    def scrape(self, requests_handler=None):
        print("scraping question from {}".format(self.url))

        requests_handler = requests_handler or self.session or get_session()
        res = requests_handler.get(self.url, params=dict(answertab=self.answer_tab))
        soup = BeautifulSoup(res.content, "lxml")

        return dict(
            question=self.scrape_post(soup.find("div", {"class": "question"})),
            answers=[self.scrape_post(answer) for answer in soup.find_all("div", {"class": "answer"})]
        )

    def scrape_post(self, post_soup):
        soup = post_soup.find("div", {"class": "post-text"})
        soup = self.remove_blacklisted_tags(soup)
        return dict(
            body=soup.text,
            comments=self.scrape_comments(post_soup)
        )

    def remove_blacklisted_tags(self, soup):
        for tag in self.tag_blacklist:
            tag_soup = soup.find(tag)
            if tag_soup is not None:
                tag_soup.decompose()
        return soup

    def clean_tags(self, soup):
        for tag in self.tag_whitelist:
            for tag_soup in soup.select(tag):
                tag_soup.unwrap()

        return soup

    @staticmethod
    def scrape_comments(soup):
        return [comment_soup.text for comment_soup in soup.find_all("span", {"class": "comment-copy"})]

    @classmethod
    def from_question(cls, question):
        return QuestionScraper(question["url"])
