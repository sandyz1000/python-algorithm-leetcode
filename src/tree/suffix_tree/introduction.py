"""
Pattern Searching | Set 8 (Suffix Tree Introduction)
Given a text txt[0..n-1] and a pattern pat[0..m-1], write a function search(char pat[], char txt[])
that prints all occurrences of pat[] in txt[]. You may assume that n > m.

==Preprocess Pattern or Preoprocess Text?==
We have discussed the following algorithms in the previous posts:

-> KMP Algorithm
-> Rabin Karp Algorithm
-> Finite Automata based Algorithm
-> Boyer Moore Algorithm

All of the above algorithms preprocess the pattern to make the pattern searching faster. The best
time complexity that we could get by preprocessing pattern is O(n) where n is length of the text.
In this post, we will discuss an approach that preprocesses the text. A suffix tree is built of
the text. After preprocessing text (building suffix tree of text), we can search any pattern in
O(m) time where m is length of the pattern.
Imagine you have stored complete work of William Shakespeare and preprocessed it. You can search
any string in the complete work in time just proportional to length of the pattern. This is
really a great improvement because length of pattern is generally much smaller than text.
Preprocessing of text may become costly if the text changes frequently. It is good for fixed text
or less frequently changing text though.

A Suffix Tree for a given text is a compressed trie for all suffixes of the given text. We have
discussed Standard Trie. Let us understand Compressed Trie with the following array of words.

{bear, bell, bid, bull, buy, sell, stock, stop}

Following is standard trie for the above input set of words.

                       __()__
                     /        \
                   _b_        _s_
                 /  |  \     /   \
               e    i   u   e    t
             /  \   |  / \  |    |
            a   l   d l  y  l    o
            |   |     |     |   / \
            r   l     l     l  c   p
                               |
                               k

Following is the compressed trie. Compress Trie is obtained from standard trie by joining chains
of single nodes. The nodes of a compressed trie can be stored by storing index ranges at the nodes.

                      __()__
                     /      \
                  __b__     _s_
                /   |  \   /   \
               e   id  u  ell  to
             /  \     / \     /  \
            ar  ll   ll  y   ck   p


How to build a Suffix Tree for a given text?
As discussed above, Suffix Tree is compressed trie of all suffixes, so following are very abstract
steps to build a suffix tree from given text.
1) Generate all suffixes of given text.
2) Consider all suffixes as individual words and build a compressed trie.

http://www.geeksforgeeks.org/pattern-searching-set-8-suffix-tree-introduction/

Let us consider an example text "banana\0" where '\0' is string termination character.
Following are all suffixes of "banana\0"
- - - - - - - - - - - - - - - - - - - - - - - - - - -
banana\0
anana\0
nana\0
ana\0
na\0
a\0
\0
- - - - - - - - - - - - - - - - - - - - - - - - - - -

If we consider all of the above suffixes as individual words and build a trie, we get following.

    --- DIAGRAM - GOES -- HERE ---

If we join chains of single nodes, we get the following compressed trie, which is the Suffix Tree
for given text "banana\0"

    --- DIAGRAM - GOES -- HERE ---

Please note that above steps are just to manually create a Suffix Tree. We will be discussing
actual algorithm and implementation in a separate post.

==How to search a pattern in the built suffix tree?==

We have discussed above how to build a Suffix Tree which is needed as a preprocessing step in
pattern searching. Following are abstract steps to search a pattern in the built Suffix Tree.

1) Starting from the first character of the pattern and root of Suffix Tree, do following for
    every character.
    a) For the current character of pattern, if there is an edge from the current node of suffix
    tree, follow the edge.
    b) If there is no edge, print "pattern doesn't exist in text" and return.

2) If all characters of pattern have been processed, i.e., there is a path from root for characters
of the given pattern, then print "Pattern found".

Let us consider the example pattern as "nan" to see the searching process.
Following diagram shows the path followed for searching "nan" or "nana".

    --- DIAGRAM - GOES -- HERE ---

How does this work?
Every pattern that is present in text (or we can say every substring of text) must be a prefix
of one of all possible suffixes. The statement seems complicated, but it is a simple statement, we
just need to take an example to check validity of it.

----------------------------------------------------------------
Applications of Suffix Tree
----------------------------------------------------------------

Suffix tree can be used for a wide range of problems. Following are some famous problems where
Suffix Trees provide optimal time complexity solution.

1) Pattern Searching
2) Finding the longest repeated substring
3) Finding the longest common substring
4) Finding the longest palindrome in a string

There are many more applications. See this for more details.

Ukkonen's Suffix Tree Construction is discussed in following articles:
Ukkonen's Suffix Tree Construction - Part 1
Ukkonen's Suffix Tree Construction - Part 2
Ukkonen's Suffix Tree Construction - Part 3
Ukkonen's Suffix Tree Construction - Part 4
Ukkonen's Suffix Tree Construction - Part 5
Ukkonen's Suffix Tree Construction - Part 6

"""

# A Python program to implement Ukkonen's Suffix Tree Construction

MAX_CHAR = 256


class SuffixTreeNode:
    def __init__(self, start, end, root=None):
        self.children = [None] * MAX_CHAR

        # pointer to other node via suffix link
        self.suffixLink = root

        # (start, end) interval specifies the edge, by which the node is connected to its parent
        # node. Each edge will connect two nodes,  one parent and one child, and (start,
        # end) interval of a given edge  will be stored in the child node. Lets say there are two
        #  nods A and B connected by an edge with indices (5, 8) then this indices (5, 8) will be
        #  stored in node B.
        self.start = start
        self.end = end

        # for leaf nodes, it stores the index of suffix for the path  from root to leaf

        # suffixIndex will be set to -1 by default and actual suffix index will be set later
        # for leaves at the end of all phases
        self.suffixIndex = -1


class Pointer:
    def __init__(self, value):
        self.value = value


class SuffixTree:
    def __init__(self, text, root=None):

        self.text = text  # Input string
        self.root = root  # Pointer to root node

        # lastNewNode will point to newly created internal node, waiting for it's suffix link to
        # be set, which might get a new suffix link (other than root) in next extension of same
        # phase. lastNewNode will be set to NULL when last newly created internal node (if there
        # is any) got it's suffix link reset to new internal node created in next extension of
        # same phase.

        self.activeNode = None

        # activeEdge is represented as input string character index (not the character itself)
        self.activeEdge = -1
        self.activeLength = 0
        self.leaf_end = Pointer(-1)
        # remainingSuffixCount tells how many suffixes yet to be added in tree
        self.remainingSuffixCount = 0
        self.size = -1  # Length of input string

    def edge_length(self, n):
        if n == self.root:
            return 0
        return n.end.value - n.start + 1

    def walk_down(self, currNode):
        """
        activePoint change for walk down (APCFWD) using Skip/Count Trick (Trick 1). If active
        Length is greater than current edge length, set next  internal node as activeNode and
        adjust activeEdge and activeLength accordingly to represent same activePoint
        """

        if self.activeLength >= self.edge_length(currNode):
            self.activeEdge += self.edge_length(currNode)
            self.activeLength -= self.edge_length(currNode)
            self.activeNode = currNode
            return 1
        return 0

    def extend_suffix_tree(self, pos):
        # Extension Rule 1, this takes care of extending all leaves created so far in tree
        self.leaf_end.value = pos

        # Increment remainingSuffixCount indicating that a new suffix added to the list of
        # suffixes yet to be added in tree
        self.remainingSuffixCount += 1

        # set last_new_node to NULL while starting a new phase, indicating there is no internal
        # node waiting for it's suffix link reset in current phase
        last_new_node = None

        # Add all suffixes (yet to be added) one by one in tree
        while self.remainingSuffixCount > 0:

            if self.activeLength == 0:
                self.activeEdge = pos  # APCFALZ

            # There is no outgoing edge starting with activeEdge from activeNode
            if self.activeNode.children[ord(self.text[self.activeEdge])] is None:
                # Extension Rule 2 (A new leaf edge gets created)
                self.activeNode.children[ord(self.text[self.activeEdge])] = \
                    SuffixTreeNode(pos, self.leaf_end, self.root)

                # A new leaf edge is created in above line starting from  an existng node
                # (the current activeNode), and if there is any internal node waiting for it's
                # suffix link get reset, point the suffix link from that last internal node to
                # current activeNode. Then set last_new_node to NULL indicating no more node waiting
                # for suffix link reset.

                if last_new_node is not None:
                    last_new_node.suffixLink = self.activeNode
                    last_new_node = None

            # There is an outgoing edge starting with activeEdge from activeNode
            else:
                # Get the nextt node at the end of edge starting with activeEdge
                nextt = self.activeNode.children[ord(self.text[self.activeEdge])]
                if self.walk_down(nextt):
                    # Start from nextt node (the new activeNode)
                    continue

                # Extension Rule 3 (current character being processed is already on the edge)
                if self.text[nextt.start + self.activeLength] == self.text[pos]:
                    # If a newly created node waiting for it's suffix link to be set, then set
                    # suffix link of that waiting node to curent active node

                    if last_new_node is not None and self.activeNode != self.root:
                        last_new_node.suffixLink = self.activeNode
                        last_new_node = None

                    # APCFER3
                    self.activeLength += 1
                    # STOP all further processing in this phase and move on to nextt phase*/
                    break

                # We will be here when activePoint is in middle of the edge being traversed and
                # current character being processed is not on the edge (we fall off the tree).
                # In this case, we add a new internal node and a new leaf edge going out of that
                # new node. This is Extension Rule 2, where a new leaf edge and a new internal
                # node get created
                split_end = Pointer(0)
                split_end.value = nextt.start + self.activeLength - 1

                # New internal node
                split = SuffixTreeNode(nextt.start, split_end, self.root)
                self.activeNode.children[ord(self.text[self.activeEdge])] = split

                # New leaf coming out of new internal node)
                split.children[ord(self.text[pos])] = SuffixTreeNode(pos, self.leaf_end)
                nextt.start += self.activeLength
                split.children[ord(self.text[nextt.start])] = nextt

                # We got a new internal node here. If there is any internal node created in last
                # extensions of same phase which is still waiting for it's suffix link reset,
                # do it now.
                if last_new_node is not None:
                    # suffixLink of last_new_node points to current newly created internal node
                    last_new_node.suffixLink = split

                # Make the current newly created internal node waiting for it's suffix link reset
                # (which is pointing to root at present). If we come across any other internal
                # node (existing or newly created) in nextt extension of same phase, when a new
                # leaf edge gets added (i.e. when Extension Rule 2 applies is any of the nextt
                # extension of same phase) at that point, suffixLink of this node will point to
                # that internal node.
                last_new_node = split

            # One suffix got added in tree, decrement the count of suffixes yet to be added.
            self.remainingSuffixCount -= 1

            if self.activeNode == self.root and self.activeLength > 0:  # APCFER2C1
                self.activeLength -= 1
                self.activeEdge = pos - self.remainingSuffixCount + 1

            elif self.activeNode != self.root:  # APCFER2C2
                self.activeNode = self.activeNode.suffixLink

    def printt(self, i, j):
        k = i
        while k <= j and self.text[k] != '#':
            print("%c" % self.text[k], end="")
            k += 1

        if k <= j:
            print("#", end="")

    def set_suffix_index_by_dfs(self, n, label_height):
        """
        Print the suffix tree as well along with setting suffix index So tree will be printed
        in DFS manner Each edge along with it's suffix index will be printed
        """
        if n is None:
            return

        if n.start != -1:  # A non-root node
            # Print the label on edge from parent to current node
            # self.printt(n.start, n.end.value)
            pass

        leaf = 1
        for i in range(MAX_CHAR):
            if n.children[i] is not None:
                if leaf == 1 and n.start != -1:
                    # print(" [%d]" % n.suffixIndex)
                    pass

                # Current node is not a leaf as it has outgoing edges from it.
                leaf = 0
                self.set_suffix_index_by_dfs(n.children[i],
                                             label_height + self.edge_length(n.children[i]))

        if leaf == 1:
            for i in range(n.start, n.end.value + 1):
                if self.text[i] == '#':  # Trim unwanted characters
                    n.end = Pointer(i)

            n.suffixIndex = self.size - label_height
            # print(" [%d]" % n.suffixIndex)

    def build_suffix_tree(self):
        """
        Build the suffix tree and print the edge labels along with suffixIndex. suffixIndex for
        leaf edges will be >= 0 and for non-leaf edges will be -1

        """
        self.size = len(self.text)
        root_end = Pointer(-1)

        # Root is a special node with start and end indices as -1, as it has no parent from where
        #  an edge comes to root
        self.root = SuffixTreeNode(-1, root_end, self.root)

        self.activeNode = self.root  # First activeNode will be root
        for i in range(self.size):
            self.extend_suffix_tree(i)

        label_height = 0
        self.set_suffix_index_by_dfs(self.root, label_height)

    def traverse_edge(self, m_string, idx, start, end):
        k = start
        # Traverse the edge with character by character matching
        while k <= end and idx < len(m_string):
            if self.text[k] != m_string[idx]:
                return -1  # mo match
            idx += 1
            k += 1

        if idx >= len(m_string):
            return 1  # match

        return 0  # more characters yet to match

    def do_traversal(self, n, m_string, idx):
        if n is None:
            return -1  # no match

        res = -1

        # If node n is not root node, then traverse edge from node n's parent to node n.
        if n.start != -1:
            res = self.traverse_edge(m_string, idx, n.start, n.end.value)
            if res != 0:
                return res  # match (res = 1) or no match (res = -1)

        # Get the character index to search
        idx = idx + self.edge_length(n)

        # If there is an edge from node n going out  with current character str[idx],
        # traverse that edge

        if n.children[ord(m_string[idx])] is not None:
            return self.do_traversal(n.children[ord(m_string[idx])], m_string, idx)
        else:
            return -1  # no match

    def check_for_substring(self, m_string):
        res = self.do_traversal(self.root, m_string, 0)
        if res == 1:
            print("Pattern <%s> is a Substring" % m_string)
        else:
            print("Pattern <%s> is NOT a Substring" % m_string)


if __name__ == "__main__":
    suffix = SuffixTree("abcabxabcd")
    suffix.build_suffix_tree()