from typing import Union

from ._elements_utils import (
    _find_one,
    _find_all,
)


class ElementBase:
    def __init__(self, name: str):
        self._name = name
        self._sons = []
        self._parent = None

    def is_comment(self) -> bool:
        return False

    @property
    def parent(self):
        """Get the parent of the element."""
        return self._parent
    @property
    def name(self) -> str:
        """Get the name of the element."""
        return self._name

    @name.setter
    def name(self, new_name: str):
        """Set the name of the element."""
        if not new_name or new_name[0].isdigit():
            raise ValueError(f"Invalid tag name '{new_name}'")
        self._name = new_name

    def to_string(self, indentation: str) -> str:
        """Convert the element and its sons to a string representation of XML."""
        return self._to_string(0, indentation)

    def _to_string(self, index: int, indentation: str) -> str:
        pass

    def get_path(self) -> str:
        """Get the full path of the element in the XML tree, separated by |."""
        elements = []
        current = self
        while current is not None:
            elements.append(current._name)
            current = current._parent
        return "|".join(reversed(elements))

    def add_before(self, sibling: "Element"):
        """Add this element before the given sibling element."""
        parent = sibling._parent
        if parent is None:
            raise ValueError(f"Element {sibling.name} has no parent")
        index = parent._sons.index(sibling)
        parent._sons.insert(index, self)
        self._parent = parent

    def add_after(self, sibling: "Element"):
        """Add this element after the given sibling element."""
        parent = sibling._parent
        if parent is None:
            raise ValueError(f"Element {sibling.name} has no parent")
        index = parent._sons.index(sibling)
        parent._sons.insert(index + 1, self)
        self._parent = parent

    def add_as_son_of(self, parent: "Element"):
        """Add this element as a son of the given parent element."""
        parent._sons.append(self)
        self._parent = parent

    def set_as_parent_of(self, son: "Element"):
        """Set this element as the parent of the given son element."""
        self._sons.append(son)
        son._parent = self

    def remove(self):
        """Remove this element from its parent's sons."""
        self._parent._sons.remove(self)
        self._parent = None


class TextOnlyComment(ElementBase):
    def __init__(self, text: str):
        super().__init__("")
        self._text = text

    def is_comment(self) -> bool:
        return True

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        return f"{indent}<!-- {self._text} -->\n"


class CData(ElementBase):
    def __init__(self, text: str):
        super().__init__("")
        self._text = text

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        return f"{indent}<![CDATA[{self._text}]]>\n"


class Doctype(ElementBase):
    def __init__(self, text: str):
        super().__init__("")
        self._text = text

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        sons_indent = indentation * (index + 1)
        children_str = ""
        for son in self._sons:
            if isinstance(son, TextOnlyComment):
                children_str = children_str + son._to_string(index + 1, indentation)
            else:
                children_str = children_str + sons_indent + "<" + son.name + ">\n"
        if children_str:
            return f"{indent}<{self._text}[\n{children_str}{indent}]>\n"
        else:
            return f"{indent}<![CDATA[{self._text}]]>\n"


class Element(ElementBase):
    def __init__(self, name: str):
        super().__init__(name)
        self.content = ""
        self.attributes = {}
        self._is_empty = False  # whether the element is self-closing

    def comment_out(self):
        self.__class__ = Comment

    def _to_string(self, index: int, indentation: str, with_endl=True) -> str:
        indent = indentation * index

        attributes_str = " ".join(
            f'{key}="{value}"' for key, value in self.attributes.items()  # f-string formats the pair as key="value"
        )

        attributes_part = f" {attributes_str}" if attributes_str else ""

        if self._is_empty:
            result = f"{indent}<{self.name}{attributes_part}/>"
        else:
            opening_tag = f"<{self.name}{attributes_part}>"
            closing_tag = f"</{self.name}>"

            children_str = "".join(son._to_string(index + 1, indentation) for son in self._sons)

            if children_str:
                result = f"{indent}{opening_tag}" f"{self.content}" f"{"\n"}" f"{children_str}{indent}{closing_tag}"
            else:
                result = f"{indent}{opening_tag}{self.content}{closing_tag}"

        if with_endl:
            result += "\n"
        return result

    def find(
        self,
        name: str = None,
        only_one: bool = True,
        with_content: str = None,
    ) -> Union["Element", list["Element"], None]:
        """
        Find element(s) by name or content or both
        :param name: name of the element to find, can be nested using |, e.g. "parent|child|subchild"
        :param only_one: stop at first find or return all found elements
        :param with_content: filter by content
        :return: the elements found,
                if found, return the elements that match the last name in the path,
                if not found, return None if only_one is True, else return empty list
        """
        if only_one:
            return _find_one(self, name, with_content=with_content)
        else:
            return _find_all(self, name, with_content=with_content)


class Comment(Element):
    def __init__(self, name: str):
        super().__init__(name)

    def is_comment(self) -> bool:
        return True

    def uncomment(self):
        self.__class__ = Element

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        if len(self._sons) == 0:
            return f"{indent}<!-- {super()._to_string(0, indentation, False)} -->\n"
        else:
            return f"{indent}<!--\n{super()._to_string(index +1, indentation, False)}\n{indent}-->\n"
