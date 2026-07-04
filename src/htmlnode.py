from enum import Enum

class HTMLNode():
    def __init__(self, tag = None, value = None, children = [], props = {}):
        self.tag =  tag 
        self.value = value
        self.children = children
        self.props = props

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        s = ""
        if len(self.props) == 0:
            return s

        for prop in self.props.keys():
            s += f" {prop}=\"{self.props[prop]}\""

        return s
            
class LeafNode(HTMLNode):
    def __init__(self, tag, value, props = {}):
        super().__init__(tag, value, [], props)

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.props})"

    def to_html(self):
        prop_txt = self.props_to_html()
        if self.tag != "":
            return f"<{self.tag}{prop_txt}>{self.value}</{self.tag}>"
        else:
            return f"{self.value}"

class ParentNode(HTMLNode):
    def __init__(self, tag, children, props = {}):
        super().__init__(tag, "", children, props)

    def to_html(self):
        if self.tag == "":
            raise ValueError("Tag is missing")
        if len(self.children) == 0:
            raise ValueError("Children is missing")

        prop_txt = self.props_to_html()
        child_txt = ""
        for child in self.children:
            child_txt += child.to_html()

        return f"<{self.tag}{prop_txt}>{child_txt}</{self.tag}>"

