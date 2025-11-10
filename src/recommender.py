from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from momonga import ArticleRepository

repository = ArticleRepository()
vectorizer = TfidfVectorizer(analyzer=lambda x: x)

test_links = [
    "/wiki/Blast_furnace",
    "/wiki/International_Union_of_Pure_and_Applied_Chemistry",
    "/wiki/Diamondoid",
    "/wiki/Water",
    "/wiki/BTV_(Bulgaria)"
]
test_documents = [article['curated_content'] for article in repository.curated_articles(test_links)]

curated_articles = sorted(list(repository.curated_articles(list(repository.stored_curated_links() - set(test_links)))), key=lambda x: x['link'])
curated_links = [article['link'] for article in curated_articles]
curated_documents = [article['curated_content'] for article in curated_articles]

db_matrix = vectorizer.fit_transform(curated_documents)
query_matrix = vectorizer.transform(test_documents)

similarities = cosine_similarity(query_matrix, db_matrix)
similarities = np.max(similarities, axis=0)
similarities[similarities > 0.995] = 0
top_indices = np.argsort(similarities)[-5:][::-1]

print("For your query:")
for link in test_links:
    print(link)

print("We recommend:")
for idx in top_indices:
    print(f"Article {curated_links[idx]} with similarity {similarities[idx]}")