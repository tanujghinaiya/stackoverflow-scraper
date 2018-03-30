import argparse


def init_app():
    parser = argparse.ArgumentParser(description="Scrape questions and answers from stackoverflow using tags")

    parser.add_argument("--tags", type=list, dest="The tags to be scraped from stack overflow")
    parser.add_argument("--n_pages", type=int, dest="number of pages to be scraped")
    parser.add_argument("--page_size", type=int, dest="size of each page to be scraped")


if __name__ == '__main__':
    init_app()
