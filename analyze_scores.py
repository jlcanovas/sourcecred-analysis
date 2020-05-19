import json 
import matplotlib.pyplot as plt
import numpy as np

import networkx as nx
import collections

"""

This code reads in raw cred scores from the `cred.json` file output 
by a SourceCred instance, and puts the basic node and edge data into
a NetworkX object that can be used for graph analysis. A couple of functions 
are provided to perform basic operations on that object, including 
creating subgraphs of neighboring nodes. More on the way...

This code is based on (largely copy/pasted from) @author: Michael Zargham's repo: 
https://github.com/sourcecred/research

Proper attributions/license stuff coming!

"""

AddressType = collections.namedtuple("AddressType", ("prefix", "type"))


def _type_prefix_match(address_types, address):
    """For a given address, find the type matching the address.

    Takes an object containing an array of {prefix, type} pairs, and
    an address. Returns the first type whose corresponding prefix
    was a prefix of the given address.
    """
    for address_type in address_types:
        prefix = address_type.prefix
        if address[: len(prefix)] == prefix:
            return address_type.type
    raise ValueError("No matching prefix for {}".format(address))

def node_type(address):
    """Return a string that identifies the "type" of a SourceCred node.

    For any anticipated SourceCred node (i.e., it was supplied by one of the two
    standard SourceCred plugins, i.e., sourcecred/git and sourcecred/github),
    this method returns a string which identifies the most specific declared
    node_type that matches the given node.

    The SourceCred type system is still pretty ad-hoc,
    (see: https://github.com/sourcecred/sourcecred/issues/710), so this system is
    likely to change in the future.
    """
    NODE_PREFIX_TO_TYPE = [
        AddressType(prefix=["sourcecred", "github", "REPO"], type="github/repo"),
        AddressType(
            prefix=["sourcecred", "github", "USERLIKE", "USER"], type="github/user"
        ),
        AddressType(
            prefix=["sourcecred", "github", "USERLIKE", "BOT"], type="github/bot"
        ),
        AddressType(prefix=["sourcecred", "github", "PULL"], type="github/pull"),
        AddressType(prefix=["sourcecred", "github", "ISSUE"], type="github/issue"),
        AddressType(prefix=["sourcecred", "github", "REVIEW"], type="github/review"),
        AddressType(prefix=["sourcecred", "github", "COMMENT"], type="github/comment"),
        AddressType(prefix=["sourcecred", "git", "COMMIT"], type="git/commit"),
        AddressType(prefix=["sourcecred", "github", "REPO"], type="github/repo"),
        AddressType(prefix=["sourcecred", "discourse", "like"], type="discourse/like"),
        AddressType(prefix=["sourcecred", "discourse", "topic"], type="discourse/topic"),
        AddressType(prefix=["sourcecred", "discourse", "post"], type="discourse/post"),
        AddressType(prefix=["sourcecred", "discourse", "user"], type="discourse/user"),


    ]
    return _type_prefix_match(NODE_PREFIX_TO_TYPE, address)

def edge_type(address):
    """Return a string that identifies the "type" of a SourceCred edge.

    For any anticipated SourceCred edge (i.e., it was supplied by one of the two
    standard SourceCred plugins, i.e., sourcecred/git and sourcecred/github),
    this method returns a string which identifies the most specific declared
    edge_type that matches the given node.

    The SourceCred type system is still pretty ad-hoc,
    (see: https://github.com/sourcecred/sourcecred/issues/710), so this system is
    likely to change in the future.
    """
    EDGE_PREFIX_TO_TYPE = [
        AddressType(
            prefix=["sourcecred", "github", "HAS_PARENT"], type="github/hasParent"
        ),
        AddressType(
            prefix=["sourcecred", "github", "REFERENCES"], type="github/references"
        ),
        AddressType(
            prefix=["sourcecred", "github", "MENTIONS_AUTHOR"],
            type="github/mentionsAuthor",
        ),
        AddressType(prefix=["sourcecred", "github", "AUTHORS"], type="github/authors"),
        AddressType(prefix=["sourcecred", "github", "PULL"], type="github/pull"),
        AddressType(prefix=["sourcecred", "github", "ISSUE"], type="github/issue"),
        AddressType(prefix=["sourcecred", "github", "REVIEW"], type="github/review"),
        AddressType(prefix=["sourcecred", "github", "COMMENT"], type="github/comment"),
        AddressType(
            prefix=["sourcecred", "github", "MERGED_AS"], type="github/mergedAs"
        ),
        AddressType(
            prefix=["sourcecred", "github", "REACTS", "HOORAY"],
            type="github/reactsHooray",
        ),
        AddressType(
            prefix=["sourcecred", "github", "REACTS", "THUMBS_UP"],
            type="github/reactsThumbsUp",
        ),
        AddressType(
            prefix=["sourcecred", "github", "REACTS", "HEART"],
            type="github/reactsHeart",
        ),
        AddressType(
            prefix=["sourcecred", "github", "REACTS", "ROCKET"],
            type="github/reactsRocket",
        ),
        AddressType(prefix=["sourcecred", "git", "HAS_PARENT"], type="git/hasParent"),
        AddressType(prefix=["sourcecred", "discourse", "replyTo"], type="discourse/post is reply to"),
        AddressType(prefix=["sourcecred", "discourse", "authors", "topic"], type="discourse/authors topic"),
        AddressType(prefix=["sourcecred", "discourse", "authors", "post"], type="discourse/authors post"),
        AddressType(prefix=["sourcecred", "discourse", "topic", "topicContainsPost"], type="discourse/contains post"),
        AddressType(prefix=["sourcecred", "discourse", "likes"], type="discourse/likes"),
        AddressType(prefix=["sourcecred", "discourse", "createsLike"], type="discourse/creates like"),
        AddressType(prefix=["sourcecred", "discourse", "references", "post"], type="discourse/references post"),
        AddressType(prefix=["sourcecred", "discourse", "references", "topic"], type="discourse/references topic"),
        AddressType(prefix=["sourcecred", "discourse", "references", "user"], type="discourse/mentions"),
        AddressType(prefix=["sourcecred", "discourse", "topicContainsPost"], type="discourse/contains post"),
    


    ]
    return _type_prefix_match(EDGE_PREFIX_TO_TYPE, address)


def json_to_graph(json):
    """Convert a serialized SourceCred graph to a MultiDiGraph.

    Takes in a Python dict representing a SourceCred graph json.
    Returns a networkx MultiDiGraph, with node and edge type identifiers
    added as an additional property.
    """
    [compat, data] = json
    # assert compat["type"] == "sourcecred/graph", compat
    # assert compat["version"] == "0.4.0", compat

    def nodePropertyDict(address):
        return {"address": tuple(address), "type": node_type(address)}

    def edgePropertyDict(address):
        return {"address": tuple(address), "type": edge_type(address)}

	# nodes = data["weightedGraphJSON"][1]["graphJSON"][1]["nodes"] #data["nodes"]
    # nodes = data["weightedGraphJSON"][1]["graphJSON"][1]["nodes"] #["sortedNodeAddresses"]
    nodes = data["weightedGraphJSON"][1]["graphJSON"][1]["sortedNodeAddresses"]
    edges = data["weightedGraphJSON"][1]["graphJSON"][1]["edges"]  #data["edges"]
    # nodes = data["nodes"]
    # edges = data["edges"]
    g = nx.MultiDiGraph()
    for (i, n) in enumerate(nodes):
        g.add_node(i, **nodePropertyDict(n))
    for e in edges:
        g.add_edge(e["srcIndex"], e["dstIndex"], **edgePropertyDict(e["address"]))
    return g


def neighbor_subgraph(g, node):
    """Create subgraph of neighboring nodes

    Takes in a node, finds it neighbors and creates a subgraph with them
    """
    # get neighbors of node
    neighbors = nx.all_neighbors(g,node)  

    # create list of nodes in subgraph
    neighbor_nodes = [node]
    for n in neighbors:
        neighbor_nodes.append(n)

    neighbor_subgraph = g.subgraph(neighbor_nodes)  
    return neighbor_subgraph



# ---------- Load raw cred data --------

# with open('cred.json') as f: 
#      cred = json.load(f) 

# The 'cred_maker.json' below is simply a renamed cred.json
# generated when an instance is run
with open('cred_maker.json') as f: 	
     cred = json.load(f) 

# Convert JSON data to graph object with node and edge data
g = json_to_graph(cred)


# Create subgraph of a node (here node 8000)
sub_g = neighbor_subgraph(g,8000)


# Print node data to screen
for node in sub_g:

	print(nodes[node])

# Draw subgraph
nx.draw_networkx(sub_g)
# nx.draw(sub_g)
plt.show()









