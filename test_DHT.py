from random import shuffle
import random

from kbucket import KBucket
from node import Node
import hashlib
from struct import pack

import io,sys




def mknode(node_id=None, ip_addy=None, port=None, intid=None):
    """
    Make a node. Created a random id if not specified.
    """
    if intid is not None:
        node_id = intid.to_bytes(20, byteorder='big', signed=False)    
    else:
        node_id = random.getrandbits(160).to_bytes(20, 'big')
    return Node(node_id)


class TestKBucket:
    def test_split(self, mknode):
        bucket = KBucket(0, 10, 5)
        # print("Initial bucket setup:")
        bucket.add_node(mknode(intid=5))
        bucket.add_node(mknode(intid=6))
        # print("Starting bucket split:")
        one, two = bucket.split()
        
        # print("Final state after split:")
        # print(f"Bucket 'one': {one}, Nodes: {one.nodes}")
        # print(f"Bucket 'two': {two}, Nodes: {two.nodes}")
        assert len(one) == 1
        assert one.range == (0, 5)
        assert len(two) == 1
        assert two.range == (6, 10)
        print("test_split passed.")

    def test_split_no_overlap(self):
        left, right = KBucket(0, 2 ** 160, 20).split()
        assert (right.range[0] - left.range[1]) == 1
        print("test_split_no_overlap passed.")

    def test_add_node(self, mknode):
        bucket = KBucket(0, 10, 2)
        assert bucket.add_node(mknode()) is True
        assert bucket.add_node(mknode()) is True
        assert bucket.add_node(mknode()) is False
        assert len(bucket) == 2
        print("test_add_node for full bucket passed.")

        bucket = KBucket(0, 10, 3)
        nodes = [mknode(), mknode(), mknode()]
        for node in nodes:
            bucket.add_node(node)
        for index, node in enumerate(bucket.get_nodes()):
            assert node == nodes[index]
        print("test_add_node for double addition passed.")

    def test_remove_node(self, mknode):
        k = 3
        bucket = KBucket(0, 10, k)
        nodes = [mknode() for _ in range(10)]
        for node in nodes:
            bucket.add_node(node)

        replacement_nodes = bucket.replacement_nodes
        assert list(bucket.nodes.values()) == nodes[:k]
        assert list(replacement_nodes.values()) == nodes[k:]

        bucket.remove_node(nodes.pop())
        assert list(bucket.nodes.values()) == nodes[:k]
        assert list(replacement_nodes.values()) == nodes[k:]

        bucket.remove_node(nodes.pop(0))
        assert list(bucket.nodes.values()) == nodes[:k-1] + nodes[-1:]
        assert list(replacement_nodes.values()) == nodes[k-1:-1]

        shuffle(nodes)
        for node in nodes:
            bucket.remove_node(node)
        assert not bucket
        assert not replacement_nodes
        print("test_remove_node passed.")

    def test_in_range(self, mknode):
        bucket = KBucket(0, 10, 10)
        assert bucket.has_in_range(mknode(intid=5)) is True
        assert bucket.has_in_range(mknode(intid=11)) is False
        assert bucket.has_in_range(mknode(intid=10)) is True
        assert bucket.has_in_range(mknode(intid=0)) is True
        print("test_in_range passed.")

    def test_replacement_factor(self, mknode):
        k = 3
        factor = 2
        bucket = KBucket(0, 10, k, replacementNodeFactor=factor)
        nodes = [mknode() for _ in range(10)]
        for node in nodes:
            bucket.add_node(node)

        replacement_nodes = bucket.replacement_nodes
        assert len(list(replacement_nodes.values())) == k * factor
        assert list(replacement_nodes.values()) == nodes[k + 1:]
        assert nodes[k] not in list(replacement_nodes.values())
        print("test_replacement_factor passed.")
        
    def test_insert_node(self):
        bucket = KBucket(0, 255, 2)
        node1 = mknode(intid=1)
        node2 = mknode(intid=255)
        node_out_of_range = mknode(intid=256)
        
        assert bucket.insertNode(node1.id) is True, "Should be able to insert node within range"
        assert bucket.insertNode(node2.id) is True, "Should be able to insert node within range"
        assert bucket.insertNode(node_out_of_range.id) is False, "Should not insert node out of range"
        print("test_insert_node passed.")

    
    def test_print_bucket_contents(self):
        bucket = KBucket(0, 255, 10)
        nodes = [mknode(intid=1), mknode(intid=2), mknode(intid=3)]
        
        for node in nodes:
            bucket.insertNode(node.id)
        
        # 捕获print输出
        capturedOutput = io.StringIO()
        sys.stdout = capturedOutput
        bucket.printBucketContents()
        sys.stdout = sys.__stdout__
        
        # 检查输出
        output = capturedOutput.getvalue()
        assert str(nodes[0].long_id) in output, "Node 1 ID should be printed"
        assert str(nodes[1].long_id) in output, "Node 2 ID should be printed"
        assert str(nodes[2].long_id) in output, "Node 3 ID should be printed"
        print("test_print_bucket_contents passed.")

class TestNode:
    def test_long_id(self):
        rid = hashlib.sha1(str(random.getrandbits(255)).encode()).digest()
        node = Node(rid)
        assert node.long_id == int.from_bytes(rid, 'big'), "test_long_id failed"
        print("test_long_id passed.")

    def test_distance_calculation(self):
        ridone = hashlib.sha1(str(random.getrandbits(255)).encode()).digest()
        ridtwo = hashlib.sha1(str(random.getrandbits(255)).encode()).digest()

        shouldbe = int.from_bytes(ridone, 'big') ^ int.from_bytes(ridtwo, 'big')
        none = Node(ridone)
        ntwo = Node(ridtwo)
        assert none.distance_to(ntwo) == shouldbe, "test_distance_calculation failed"
        print("test_distance_calculation passed.")
        
def run_tests():
    test = TestKBucket()
    
    # test kbucket
    test.test_split(mknode)
    test.test_split_no_overlap()
    test.test_add_node(mknode)
    test.test_remove_node(mknode)
    test.test_insert_node()
    test.test_print_bucket_contents()
    
    # test node
    test_node = TestNode()
    test_node.test_long_id()
    test_node.test_distance_calculation()

if __name__ == "__main__":
    run_tests()
