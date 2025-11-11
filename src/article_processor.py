import bs4
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet, stopwords
from nltk.tokenize import word_tokenize
from re import match

from pymongo import MongoClient

from momonga import ArticleRepository

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger_eng')

def get_wordnet_pos(treebank_tag):

    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def curate_content(content, lemmatizer: WordNetLemmatizer):
    soup = bs4.BeautifulSoup(content, 'html.parser')

    for tag in soup.find_all(class_="reference"):
        tag.decompose()

    parsed = ' '.join(p.get_text(separator=' ', strip=True) for p in soup.find('div', {'id': 'mw-content-text'}).select('p'))
    tokens = word_tokenize(parsed.lower(), language='english')
    cleaned = [word for word in tokens if match(r'^[a-zA-Z0-9]+$', word) and word not in set(stopwords.words('english'))]
    tagged = nltk.pos_tag(cleaned)
    lemmatized = [lemmatizer.lemmatize(token, get_wordnet_pos(tag)) for token, tag in tagged]

    return lemmatized

repository = ArticleRepository(client = MongoClient("mongodb://localhost:27017/"))
lemmatizer = WordNetLemmatizer()

curated_links = repository.stored_curated_links()
stored_size = len(repository.stored_links())

to_upload = []
for k, article in enumerate(repository.stored_articles()):
    if article['link'] in curated_links:
        print(f"({k+1} of {stored_size}) {article['link']} already in the curated db, skipping...")
        continue
    print(f"({k+1} of {stored_size}) processing {article['link']}")
    curated_content = curate_content(article['content'], lemmatizer)
    to_upload.append({'link': article['link'], 'curated_content': curated_content})

if len(to_upload):
    print("Uploading curated articles to the db...")
    repository.store_curated_serial(to_upload)
else:
    print("Nothing to upload.")
print("Finished.")