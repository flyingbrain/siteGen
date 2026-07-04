import re

from enum import Enum
from htmlnode import HTMLNode, ParentNode, LeafNode 

class BlockType(Enum):
    PARAGRAPH = "paragraph"
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    OLIST = "ordered_list"
    ULIST = "unordered_list"

class TextType(Enum):
    LINK = "link"
    BOLD = "bold"
    TEXT = "text"
    ITALIC = "italic" 
    CODE =  "code"
    IMAGE =  "image"

class TextNode():
    def __init__(self, text, text_type, url = ""):
        self.text = text
        self.text_type = TextType(text_type)
        self.url = url

    def __eq__(self, node):
        return node.text == self.text and self.text_type == node.text_type and self.url == node.url

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    match text_node.text_type:
        case TextType.TEXT:
            return LeafNode("", text_node.text)
        case TextType.BOLD:
            return LeafNode("b", text_node.text)
        case TextType.ITALIC:
            return LeafNode("i", text_node.text)
        case TextType.CODE:
            return LeafNode("code", text_node.text)
        case TextType.LINK:
            return LeafNode("a", text_node.text, {"href": text_node.url})
        case TextType.IMAGE: return LeafNode("img", "", {"src": text_node.url, "alt": text_node.text})

def split_nodes_delimiter(old_nodes: list[TextNode], delimiter: str, text_type: TextType) -> list[TextNode]:
    result = []

    for node in old_nodes:
        if node.text != "":
            if text_type == TextType.LINK:
                splited = re.split(r"\[(.*?)\]\((.*?)\)", node.text)
            elif text_type == TextType.IMAGE:
                splited = re.split(r"\!\[(.*?)\]\((.*?)\)", node.text)
            else:
                splited = node.text.split(delimiter)
                if len(splited) % 2 == 0:
                    raise ValueError("Delimiter isn't closed")

            if text_type == TextType.LINK or text_type == TextType.IMAGE:
                for n in enumerate(splited): 
                    if n[1] == "":
                        continue
                    if re.match(r"http", n[1]) or re.match(r"/\w*", n[1]): 
                        if len(result) != 0:
                            result.pop()
                        result.append(TextNode(splited[n[0]-1], text_type, n[1]))
                    else:
                        result.append(TextNode(n[1], node.text_type, node.url))
            else:
                for n in enumerate(splited): 
                    if n[0] % 2 != 0: 
                        result.append(TextNode(n[1], text_type))
                    else:
                        result.append(TextNode(n[1], node.text_type, node.url))
    return result

def text_to_textnodes(text: str) -> list[TextNode]:
    nodes = [TextNode(text, TextType.TEXT)]
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, " ", TextType.IMAGE)
    nodes = split_nodes_delimiter(nodes, " ", TextType.LINK)

    return nodes

def markdown_to_blocks(text):
    blocks = text.split("\n\n")
    for block in enumerate(blocks):
        blocks[block[0]] = block[1].strip("\n")
    return blocks

def block_to_block_type(block: str) -> BlockType:
    lines = block.split("\n")

    if block.startswith(("# ", "## ", "### ", "#### ", "##### ", "###### ")):
        return BlockType.HEADING
    if len(lines) > 1 and lines[0].startswith("```") and lines[-1].startswith("```"):
        return BlockType.CODE
    if block.startswith(">"):
        for line in lines:
            if not line.startswith(">"):
                return BlockType.PARAGRAPH
        return BlockType.QUOTE
    if block.startswith("- "):
        for line in lines:
            if not line.startswith("- "):
                return BlockType.PARAGRAPH
        return BlockType.ULIST
    if block.startswith("1. "):
        i = 1
        for line in lines:
            if not line.startswith(f"{i}. "):
                return BlockType.PARAGRAPH
            i += 1
        return BlockType.OLIST
    return BlockType.PARAGRAPH

def markdown_to_html_node(text):
    parent = ParentNode("div", [])
    blocks = markdown_to_blocks(text)

    for block in blocks:
        child = None
        h_nodes = []
        t_nodes = []

        match block_to_block_type(block):
            case BlockType.CODE:
                child = ParentNode("pre", [LeafNode("code", block.replace("```", "").replace("\n", "", 1))])
            case BlockType.HEADING:
                tag = "h" + str(block.count("#"))
                t_nodes = text_to_textnodes(block.replace("#", "").replace("\n", " ").strip())
            case BlockType.QUOTE:
                tag = "blockquote"
                t_nodes = text_to_textnodes(block.replace(">", "").replace("\n", " ").strip())
            case BlockType.OLIST:
                child = list_to_node(block, "ol")
            case BlockType.ULIST:
                child = list_to_node(block, "ul")
            case BlockType.PARAGRAPH:
                tag = "p"
                t_nodes = text_to_textnodes(block.replace("\n", " "))

        for t_node in t_nodes:
            h_nodes.append(text_node_to_html_node(t_node))

        if len(h_nodes) != 0:
            child = ParentNode(tag, h_nodes)

        if child != None:
            parent.children.append(child) 
    
    return parent

def list_to_node(block, tag):
    h = []
    child = ParentNode(tag, [])
    if tag == "ul":
        items = block.split("-")
    else:
        items = re.split(r"\d.", block)

    for item in items:
        h = []
        t = text_to_textnodes(item.replace("\n", " ").strip())
        for t_node in t:
            h.append(text_node_to_html_node(t_node))

        if len(h) > 0:
            child.children.append(ParentNode("li", h)) 

    return child 

def extract_title(text):
    parts = text.split("\n")
    for part in parts:  
        if re.match(r"^# ", part):
            return part.replace("#", "").strip()
