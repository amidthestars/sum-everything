# TODO: Write unit tests
import nltk
import requests
from bs4 import BeautifulSoup

def parse_url(url):
    adStuff = ['Advertisement', "Supported by"]
    try:
        page = requests.get(url)
    except Exception as e:
        print(e)
        # Return if error in getting to link
        return "0"

    # Check whether punkt is downloaded for sentence parsing
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print(LookupError)
        nltk.download('punkt')

    soup = BeautifulSoup(page.text, "html.parser")

    links = soup.find_all('p', attrs={'class': 'css-axufdj evys1bk0'})

    article = ''

    for e in links:
        m = e.getText()

        if m in adStuff:
            continue

        # If less, then add it
        if len(article + m) <= 5000:
            article = article + m
        else:
            sentences = nltk.tokenize.sent_tokenize(m)
            for sent in sentences:
                if len(article + ' ' + sent) <= 5000:
                    article = article + ' ' + sent
                else:
                    break

            break

    message = {'article': article}
    return message