class Node:
    """
    Simple object to encapsulate the concept of a Node
    """
    def __init__(self, node_id, ip=None, port=None):
        """
        Create a Node instance.

        Args:
            node_id (int): A value between 0 and 2^160
            ip (string): Optional IP address where this Node lives
            port (int): Optional port for this Node (set when IP is set)
        """
        assert len(node_id) == 20, "node_id must be exactly 20 bytes long"
        self.id = node_id  
        self.ip = ip  
        self.port = port
        self.long_id = int(node_id.hex(), 16)

    def same_home_as(self, node):
        return self.ip == node.ip and self.port == node.port

    def distance_to(self, node):
        return self.long_id ^ node.long_id

    def __iter__(self):
        return iter([self.id, self.ip, self.port])

    def __repr__(self):
        return repr([self.long_id, self.ip, self.port])

    def __str__(self):
        return "%s:%s" % (self.ip, str(self.port))