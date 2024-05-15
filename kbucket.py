import heapq
import time
import operator
import asyncio

from itertools import chain
from collections import OrderedDict
from utils import shared_prefix, bytes_to_bit_string, node_id_to_long_id
from node import Node

class KBucket:
    def __init__(self, rangeLower, rangeUpper, ksize=3, replacementNodeFactor=5):
        self.range = (rangeLower, rangeUpper)
        self.nodes = OrderedDict()
        self.replacement_nodes = OrderedDict()
        self.touch_last_updated()
        self.ksize = ksize
        self.max_replacement_nodes = self.ksize * replacementNodeFactor

    def touch_last_updated(self):
        self.last_updated = time.monotonic()

    def get_nodes(self):
        return list(self.nodes.values())

    def split(self):
        midpoint = (self.range[0] + self.range[1]) // 2
        one = KBucket(self.range[0], midpoint, self.ksize)
        two = KBucket(midpoint + 1, self.range[1], self.ksize)
        # print(f"Splitting bucket with range {self.range} at midpoint {midpoint}")

        nodes = chain(self.nodes.values(), self.replacement_nodes.values())
        for node in nodes:
            bucket = one if node.long_id <= midpoint else two
            # print(f"Assigning node {node} with long_id {node.long_id} to bucket with range {bucket.range}")
            bucket.add_node(node)

        # print(f"Bucket 'one' after split: Nodes: {[node for node in one.nodes.values()]}")
        # print(f"Bucket 'two' after split: Nodes: {[node for node in two.nodes.values()]}")
        
        return one, two

    def remove_node(self, node):
        if node.id in self.replacement_nodes:
            del self.replacement_nodes[node.id]

        if node.id in self.nodes:
            del self.nodes[node.id]

            if self.replacement_nodes:
                newnode_id, newnode = self.replacement_nodes.popitem()
                self.nodes[newnode_id] = newnode

    def has_in_range(self, node):
        return self.range[0] <= node.long_id <= self.range[1]

    def is_new_node(self, node):
        return node.id not in self.nodes

    def add_node(self, node):
        """
        Add a C{Node} to the C{KBucket}.  Return True if successful,
        False if the bucket is full.
        
        If the bucket is full, keep track of node in a replacement list,
        per section 4.1 of the paper.
        """
        if node.id in self.nodes:
            del self.nodes[node.id]
            self.nodes[node.id] = node
        elif len(self) < self.ksize:
            self.nodes[node.id] = node
        else:
            if node.id in self.replacement_nodes:
                del self.replacement_nodes[node.id]
            self.replacement_nodes[node.id] = node
            while len(self.replacement_nodes) > self.max_replacement_nodes:
                self.replacement_nodes.popitem(last=False)
            return False
        return True

    def depth(self):
        vals = self.nodes.values()
        sprefix = shared_prefix([bytes_to_bit_string(n.id) for n in vals])
        return len(sprefix)

    def head(self):
        return list(self.nodes.values())[0]

    def __getitem__(self, node_id):
        return self.nodes.get(node_id, None)

    def __len__(self):
        return len(self.nodes)

    def printBucketContents(self):
        if self.nodes:
            print("Node IDs in the bucket:")
            for node_id in self.nodes:
                print(node_id)
        else:
            print("No nodes in the bucket.")
            
    def insertNode(self, nodeId):
        long_id = node_id_to_long_id(nodeId)
        node = Node(nodeId, long_id)
        if self.has_in_range(node):
            if self.is_new_node(node):
                return self.add_node(node)
            else:
                self.nodes[nodeId] = node
                return True
        else:
            return False  # NodeId 不在当前桶的范围内