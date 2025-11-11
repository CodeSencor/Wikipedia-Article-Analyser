from graph_tool.all import Graph, graph_draw, sfdp_layout
from pymongo import MongoClient

from momonga import (ArticleRepository)

repository = ArticleRepository(client = MongoClient("mongodb://localhost:27017/"))
links_w_referrals = repository.stored_links()
g = Graph(directed=True)

edges = []
for link in links_w_referrals:
    for referral in link.referrals:
        if type(referral) is list:
            continue
        edges.append((link.link, referral))

vmap = g.add_edge_list(edges, hashed=True, hash_type="string")
g.vertex_properties["name"] = vmap

pos = sfdp_layout(g)

graph_draw(g, pos=pos, vertex_text=vmap, vertex_font_size=9, output_size=(1200, 1200), vertex_size=5, edge_pen_width=1)
# repository.debug()

