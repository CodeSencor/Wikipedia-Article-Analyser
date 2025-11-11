from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from momonga import ArticleRepository

repository = ArticleRepository(client = MongoClient("mongodb://localhost:27017/"))
vectorizer = TfidfVectorizer(analyzer=lambda x: x)

# Preparing input list
test_links = [
    "/wiki/Blast_furnace",
    "/wiki/International_Union_of_Pure_and_Applied_Chemistry",
    "/wiki/Diamondoid",
    "/wiki/Water",
    "/wiki/BTV_(Bulgaria)"
]
test_documents = [article['curated_content'] for article in repository.curated_articles(test_links)]

# Preparing db list
curated_articles = sorted(list(repository.curated_articles(list(repository.stored_curated_links() - set(test_links)))), key=lambda x: x['link'])
curated_links = [article['link'] for article in curated_articles]
curated_documents = [article['curated_content'] for article in curated_articles]

# Computing db and query matrices
db_matrix = vectorizer.fit_transform(curated_documents)
query_matrix = vectorizer.transform(test_documents)

# Computing similarities between matrices
similarities = cosine_similarity(query_matrix, db_matrix)

# Flatten the similarities array to 1D list by taking the max similarity of db document to any document in query
# Key assumption #1: the user is unbiased in interest levels towards documents in the query
# Key assumption #2: the user is willing to read the most familiar articles to any of the read articles
similarities = np.max(similarities, axis=0)

# Killer threshold to discard duplicates
similarities[similarities > 0.995] = 0
top_indices = np.argsort(similarities)[-5:][::-1]

print("For your query:")
for link in test_links:
    print(link)

print("We recommend:")
for idx in top_indices:
    print(f"Article {curated_links[idx]} with similarity {similarities[idx]}")