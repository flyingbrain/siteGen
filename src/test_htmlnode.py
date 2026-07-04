import unittest
from htmlnode import *

class TestHTMLNode(unittest.TestCase):
    def test_props(self):
        props = {
            "href": "https://www.google.com",
            "target": "_blank",
        }
        rez = ' href="https://www.google.com" target="_blank"' 

        node = HTMLNode("p", "this is a poop text", [], props)
        self.assertNotEqual(node, None)
        self.assertEqual(node.props_to_html(), rez)

    def test_leaf_to_html(self):
        node = LeafNode("p", "Hello, world!")
        self.assertEqual(node.to_html(), "<p>Hello, world!</p>")

        props = {
            "href": "https://www.google.com",
            "target": "_blank",
        }
        node = LeafNode("a", "Hello, world!", props)
        self.assertEqual(node.to_html(), '<a href="https://www.google.com" target="_blank">Hello, world!</a>')

    def test_to_html_without_children(self):
        with self.assertRaises(ValueError):
            parent_node = ParentNode("div", [])
            parent_node.to_html()

    def test_to_html_without_tag(self):
        with self.assertRaises(ValueError):
            child_node = LeafNode("span", "child")
            parent_node = ParentNode("", [child_node])
            parent_node.to_html()

    def test_to_html_with_children(self):
        child_node = LeafNode("span", "child")
        child_node2 = LeafNode("span", "child2")
        parent_node = ParentNode("div", [child_node, child_node2])
        self.assertEqual(parent_node.to_html(), "<div><span>child</span><span>child2</span></div>")

    def test_to_html_with_grandchildren(self):
        grandchild_node = LeafNode("b", "grandchild")
        child_node = ParentNode("span", [grandchild_node])
        parent_node = ParentNode("div", [child_node])
        self.assertEqual(
            parent_node.to_html(),
            "<div><span><b>grandchild</b></span></div>",
        )


if __name__ == "__main__":
    unittest.main()
