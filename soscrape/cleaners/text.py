import re


def clean_text(excerpt):
    excerpt = re.sub("\s+", " ", excerpt)
    excerpt = re.sub("^\s+", "", excerpt)
    excerpt = re.sub("[\n\r]", "", excerpt)
    return excerpt
