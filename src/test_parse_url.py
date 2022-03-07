import nltk
from parse_url import parse_url

nltk.download()

def test_bad_url():
    url = "abcdefg"
    result = parse_url(url)

    assert result == '0'

def test_unfinished_url():
    url = "http://badurl"
    result = parse_url(url)

    assert result == '0'

def test_good_url():
    url = "https://www.nbcnews.com/health/health-news/\
            long-covid-even-mild-covid-linked-damage-brain-months-infection-rcna18959"
    result = parse_url(url)

    result != '0'
