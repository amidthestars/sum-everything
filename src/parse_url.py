# TODO: Write unit tests
import nltk
import requests
import urllib.request
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

    if False:
        links = soup.find_all('p', attrs={'class': 'css-axufdj evys1bk0'})
    else:
        links = soup.find_all('p')

        print("*** ALL LINKS ***")
        print(links)

        # Collect class names (classes: dict of [class names](keys) & [text content](vals) )
        classes = {}
        for e in links:
            if e.has_attr("class"):
                txt = e.getText()
                name = str(e["class"])
                if name not in classes:
                    classes[name] = txt
                else:
                    classes[name] += ' ' + txt
            else:
                txt = e.getText()
                if "classless" not in classes:
                    classes["classless"] = txt
                else:
                    classes["classless"] += ' ' + txt

        # for each class get number of sentences
        numSentences = {}
        mostSentences = -1
        likelyArticleClass = ''
        for className in classes.keys():
            # Holds number of sentences as well as list of sentences in case they're used
            numSentences[className] = [0, []]
            sentences = nltk.tokenize.sent_tokenize(classes[className])
            numSentences[className][0] += len(sentences)
            numSentences[className][1] = sentences

            if numSentences[className][0] > mostSentences:
                mostSentences = numSentences[className][0]
                likelyArticleClass = className

        # print(numSentences[likelyArticleClass][1])
        article = ''
        for sent in numSentences[likelyArticleClass][1]:
            if len(article + sent) <= 5000:
                if len(article) == 0:
                    article = article + sent
                else:
                    article = article + " " + sent
            else:
                # print(sent)
                # print()
                sentences = nltk.tokenize.sent_tokenize(sent)
                # print(sentences)
                for s in sentences:
                    tmp = article + " " + s
                    if len(tmp) <= 5000:
                        article = tmp
                    else:
                        break
                break

        print("** ARTICLE **\n", article)
        print(len(article))

        message = {'article': article}
        return message
