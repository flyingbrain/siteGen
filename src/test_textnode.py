import unittest
from textnode import * 

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_markdown_to_blocks(self):
        md = """
This is **bolded** paragraph

This is another paragraph with _italic_ text and `code` here
This is the same paragraph on a new line

- This is a list
- with items
"""
        blocks = markdown_to_blocks(md)
        self.assertEqual(
            blocks,
            [
                "This is **bolded** paragraph",
                "This is another paragraph with _italic_ text and `code` here\nThis is the same paragraph on a new line",
                "- This is a list\n- with items",
            ],
        )

    def test_text_to_node(self):
        text = 'This is **text** with an _italic_ word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)'

        result =  [
            TextNode("This is ", TextType.TEXT),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.TEXT),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.TEXT),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.TEXT),
            TextNode("obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.TEXT),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]

        nodes = text_to_textnodes(text)
        self.assertEqual(nodes, result)

    def test_split_images_links(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        node = TextNode(text, TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.IMAGE)
        self.assertEqual(len(new_nodes), 4)
        self.assertEqual(new_nodes[1].text, "rick roll")
        self.assertEqual(new_nodes[1].url, "https://i.imgur.com/aKaOqIh.gif")
        self.assertEqual(new_nodes[1].text_type, TextType.IMAGE)

        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        node = TextNode(text, TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.LINK)
        self.assertEqual(len(new_nodes), 4)
        self.assertEqual(new_nodes[1].text, "to boot dev")
        self.assertEqual(new_nodes[1].url, "https://www.boot.dev")
        self.assertEqual(new_nodes[1].text_type, TextType.LINK)

    def test_split_nodes(self):
        node = TextNode("This *is* a *text* node", TextType.TEXT)
        node2 = TextNode("*This is* a text *node*", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node, node2], "*", TextType.BOLD)

        self.assertEqual(len(new_nodes), 10)
        self.assertEqual(new_nodes[1].text, "is")
        self.assertEqual(new_nodes[1].text_type, TextType.BOLD)

    def test_split_nodes_raise(self):
        with self.assertRaises(ValueError):
            node = TextNode("This *is a *text* node", TextType.TEXT)
            new_nodes = split_nodes_delimiter([node], "*", TextType.BOLD)

    def test_type(self):
        with self.assertRaises(ValueError):
            TextNode("This is a text node", "error")

    def test_url(self):
        node = TextNode("This is a text node", "bold", None)
        node2 = TextNode("This is a text node", "bold", "test")

        self.assertNotEqual(node, node2)

    def test_text(self):
        node = TextNode("This is a text node", TextType.TEXT)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "")
        self.assertEqual(html_node.value, "This is a text node")

    def test_b(self):
        node = TextNode("This is a text node", TextType.BOLD)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "b")
        self.assertEqual(html_node.value, "This is a text node")

    def test_i(self):
        node = TextNode("This is a text node", TextType.ITALIC)
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "i")
        self.assertEqual(html_node.value, "This is a text node")

    def test_img(self):
        node = TextNode("This is a text node", TextType.IMAGE, "test.com")
        html_node = text_node_to_html_node(node)
        self.assertEqual(html_node.tag, "img")
        self.assertEqual(html_node.value, "")
        self.assertEqual(html_node.props, {"src": "test.com", "alt": "This is a text node"})

    def test_block_to_block_types(self):
        block = "# heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)
        block = "```\ncode\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)
        block = "> quote\n> more quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)
        block = "- list\n- items"
        self.assertEqual(block_to_block_type(block), BlockType.ULIST)
        block = "1. list\n2. items"
        self.assertEqual(block_to_block_type(block), BlockType.OLIST)
        block = "paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_title(self):
        text = """
# Pupa lupa

## no supose to be here

test test test"""

        title = extract_title(text)

        self.assertEqual(title, "Pupa lupa")

    def test_paragraphs(self):
        md = """
# Header

## Header **bolded**

> quote

- list
- items **bolded** 

1. list
2. items

This is **bolded** paragraph
text in a p
tag here

This is another paragraph with _italic_ text and `code` here

"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><h1>Header</h1><h2>Header <b>bolded</b></h2><blockquote>quote</blockquote><ul><li>list</li><li>items <b>bolded</b></li></ul><ol><li>list</li><li>items</li></ol><p>This is <b>bolded</b> paragraph text in a p tag here</p><p>This is another paragraph with <i>italic</i> text and <code>code</code> here</p></div>",
        )

    def test_codeblock(self):
        md = """
```
This is text that _should_ remain
the **same** even with inline stuff
```
"""

        node = markdown_to_html_node(md)
        html = node.to_html()
        self.assertEqual(
            html,
            "<div><pre><code>This is text that _should_ remain\nthe **same** even with inline stuff\n</code></pre></div>",
        )

if __name__ == "__main__":
    unittest.main()
