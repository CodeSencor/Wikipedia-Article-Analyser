from pymongo import MongoClient

from ReferredLink import ReferredLink


class ArticleRepository:
    def __init__(self):
        client = MongoClient("mongodb://localhost:27017/")
        db = client['articles']
        self.stored_articles_collection = db['stored_articles']
        self.explorable_links_collection = db['explorable_links']
        self.curated_articles_collection = db['curated_articles']

    def stored_links(self):
        return set(ReferredLink(article['link'], article['referrals']) for article in self.stored_articles_collection.find({}, {'link': 1, 'referrals': 1, '_id': 0}))

    def stored_articles(self):
        return self.stored_articles_collection.find({}, {"link": 1, "content": 1, "referrals": 1, "_id": 0})

    def store_article(self, link, content, referral):
        article = {
            'link': link,
            'content': content,
            'referrals': referral
        }
        return self.stored_articles_collection.insert_one(article)

    def stored_curated_links(self):
        return set(article['link'] for article in self.curated_articles_collection.find({}, {'link': 1, '_id': 0}))

    def curated_articles(self, links = None):
        if links is None:
            return self.curated_articles_collection.find({}, {"link": 1, "curated_content": 1, "_id": 0})
        else:
            return self.curated_articles_collection.find({"link": {"$in": links}}, {"link": 1, "curated_content": 1, "_id": 0})
    def store_curated(self, link, curated_content):
        article = {
            'link': link,
            'curated_content' : curated_content
        }
        return self.curated_articles_collection.insert_one(article)

    def store_curated_serial(self, curated_links):
        return self.curated_articles_collection.insert_many(curated_links)

    def add_explorable_links(self, referred_links: set[ReferredLink]):
        parsed_links = [{'link': link.link, 'referrals': [link.referral]} for link in referred_links]
        return self.explorable_links_collection.insert_many(parsed_links)

    def explorable_links(self):
        return list(ReferredLink(article['link'], article['referrals']) for article in self.explorable_links_collection.find({}, {'link': 1, 'referrals': 1, '_id': 0}))

    def remove_explorable_link(self, link):
        referrals = self.explorable_links_collection.find({'link': link}, {'referrals': 1, '_id': 0})[0]['referrals']
        self.stored_articles_collection.update_one(
            {"link": link},
            {"$addToSet": {"referrals": {"$each": referrals}}}
        )
        return self.explorable_links_collection.delete_one({'link': link})

    def update_stored_referrals(self, referred_links: set[ReferredLink], referral):
        extracted = [referred_link.link for referred_link in referred_links]
        if extracted:
            return self.stored_articles_collection.update_many(
            {"link": {"$in": extracted}},
            {"$addToSet": {"referrals": referral}}
            )
        return None

    def update_explorable_referrals(self, referred_links: set[ReferredLink], referral):
        extracted = [referred_link.link for referred_link in referred_links]
        if extracted:
            return self.explorable_links_collection.update_many(
            {"link": {"$in": extracted}},
            {"$addToSet": {"referrals": referral}}
            )
        return None
