from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
import heapq
from collections import Counter


@dataclass
class Node:
    cnt: int
    char: Optional[str]
    left: Optional[Node] = None
    right: Optional[Node] = None

    def __lt__(self, other: Node):
        return self.cnt < other.cnt

class HuffmanCoding:
    """
    Static Huffman Coding
    """

    def __init__(self):
        self.root = None
        self.encode_dict = {}
        self.decode_dict = {}

    def encode(self, raw_datas: str) -> str:
        if raw_datas == "":
            raise ValueError("cannot encode empty string")
        nodes: list[Node] = [Node(v, k) for k, v in Counter(raw_datas).items()]
        heapq.heapify(nodes)
        if len(nodes) == 1:
            self.root = heapq.heappop(nodes)
            self._rec(self.root, "0")
            return len(raw_datas) * "0"

        while len(nodes) >= 2:
            min_node1 = heapq.heappop(nodes)
            min_node2 = heapq.heappop(nodes)
            parent_node = Node(min_node1.cnt + min_node2.cnt, None, min_node1, min_node2)
            heapq.heappush(nodes, parent_node)
        self.root = heapq.heappop(nodes)
        self._rec(self.root, "")
        res = "".join([self.encode_dict[c] for c in raw_datas])
        return res

    def _rec(self, node: Node, s) -> None:
        if node.char:  # leaf
            self.encode_dict[node.char] = s
            self.decode_dict[s] = node.char
            return
        self._rec(node.left, s + "0")
        self._rec(node.right, s + "1")

    def decode(self, data) -> str:
        result = ""
        cur = ""
        for bit in data:
            cur += bit
            if cur in self.decode_dict:
                result += self.decode_dict[cur]
                cur = ""
        return result

def main():
    input_str = "DAEBCBACBBBC"
    hc = HuffmanCoding()
    encoded_str = hc.encode(input_str)
    print(f"{input_str=}")
    print(hc.encode_dict)
    print(f"{encoded_str=}")
    decoded_str = hc.decode(encoded_str)
    total_bitlength_iffixed = len(set(input_str)).bit_length() * len(input_str)
    rate = len(encoded_str) / total_bitlength_iffixed  # 固定長のbit列で文字を表現した場合とハフマン符号化した場合のbit長の比
    print(f"{rate=}")
    assert input_str == decoded_str


if __name__ == "__main__":
    main()