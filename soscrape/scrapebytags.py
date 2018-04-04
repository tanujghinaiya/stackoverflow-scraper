import itertools
import os

from soscrape.scrapers.tag_search_scraper import TagSearchScraper
from soscrape.utils.tasks_handler import TasksHandler

keywords = ['streaming', 'watch', 'console', 'video', 'mixer', 'recording', 'tuning', 'record', 'audio',
            'workspace', 'deploy', 'mobile', 'device', 'route', 'edge', 'handshake', 'event', 'slack',
            'homepage', 'app', 'login', 'checkout', 'https', 'cookies', 'chat', 'session', 'debug', 'config',
            'sdk', 'api', 'mac', 'mozilla', 'plugin', 'css', 'server', 'domain', 'authentication', 'client',
            'logging', 'python', 'go']


def scrape_tags_by_doublets_and_triplets(tags, n_workers=64):
    """
    All the preprocessing that is needed is done here

    pass a list of lists to the scrape_by_tag_sets function with the second parameter as the path to save the results to
    and n_workers as the third path
    """
    doublets = list(itertools.combinations(tags, 2))
    triplets = list(itertools.combinations(tags, 3))

    scrape_by_tag_sets(doublets, '/tmp/doublets', n_workers)
    scrape_by_tag_sets(triplets, '/tmp/triplets', n_workers)


def scrape_by_tag_sets(tags_sets, path, n_workers):
    """
    scrapes a list of list/set/tuple of tags and saves the results to the path with n parallel processes
    :param tags_sets: list of tags (list/set/tuple)
    :param path: path to save the questions to
    """
    if not os.path.exists(path):
        os.makedirs(path)

    th = TasksHandler.map(scrapers_iter(tags_sets, path), n_tasks=len(tags_sets), n_workers=n_workers, requests_handler=True)


def scrapers_iter(tags_sets, path):
    for tags_set in tags_sets:
        p = os.path.join(path, '{}.json'.format('_'.join(tags_set)))
        yield TagSearchScraper(tags_set, save_to=p)


if __name__ == '__main__':
    # Pass all the tags you need to get the questions from stack overflow
    scrape_tags_by_doublets_and_triplets(keywords)

