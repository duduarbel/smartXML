from __future__ import annotations
from typing import Union
import warnings


class IllegalOperation(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def _check_match(element: ElementBase, names: str) -> bool:
    if names and element.name != names:
        return False
    return True


class ElementBase:
    def __init__(self, name: str):
        self._name = name
        self._sons = []
        self._parent: "ElementBase|None" = None
        self.content = ""

    def is_comment(self) -> bool:
        """Check if the element is a comment."""
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

    def to_string(self, indentation: str = "\t") -> str:
        """
        Convert the XML tree to a string.
        :param indentation: string used for indentation, default is tab character
        :return: XML string
        """
        return self._to_string(0, indentation)

    def _to_string(self, index: int, indentation: str) -> str:
        pass

    def get_path(self) -> str:
        """Get the full path of the element
        returns: the path as a string from the root of the XML tree, separated by |.
        """
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

    def add_as_last_son_of(self, parent: "Element"):
        """Add this element as a son of the given parent element."""
        parent._sons.append(self)
        self._parent = parent

    def add_as_son_of(self, parent: "Element"):
        """Add this element as a son of the given parent element."""
        warnings.warn(
            "add_as_son_of() is deprecated and will be removed in version 1.1.0 . add_as_last_son_of instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        self.add_as_last_son_of(parent)

    def set_as_parent_of(self, son: "Element"):
        """Set this element as the parent of the given son element."""
        warnings.warn(
            "set_as_parent_of() is deprecated and will be removed in version 1.1.0 . add_before() or add_after() or add_as_last_son_of instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        self._sons.append(son)
        son._parent = self

    def remove(self):
        """Remove this element from its parent's sons."""
        self._parent._sons.remove(self)
        self._parent = None

    def _find_one_in_sons(
        self,
        names_list: list[str],
        with_content: str = None,
    ) -> ElementBase | None:
        if not names_list:
            return self
        for name in names_list:
            for son in self._sons:
                if _check_match(son, name):
                    found = son._find_one_in_sons(names_list[1:], with_content)
                    if found:
                        if with_content is None or found.content == with_content:
                            return found
        return None

    def _find_one(self, names: str, with_content: str) -> ElementBase | None:

        if _check_match(self, names):
            if with_content is None or self.content == with_content:
                return self

        names_list = names.split("|")

        if len(names_list) > 1:
            if self.name == names_list[0]:
                found = self._find_one_in_sons(names_list[1:], with_content)
                if found:
                    return found

        for son in self._sons:
            found = son._find_one(names, with_content)
            if found:
                return found
        return None

    def _find_all(self, names: str, with_content: str) -> list[Element]:
        results = []
        if _check_match(self, names=names):
            if with_content is None or self.content == with_content:
                results.extend([self])
                for son in self._sons:
                    results.extend(son._find_all(names, with_content))
                return results

        names_list = names.split("|")

        if _check_match(self, names_list[0]):
            if with_content is None or self.content == with_content:
                sons = []
                sons.extend(self._sons)
                match = []
                for index, name in enumerate(names_list[1:]):
                    for son in sons:
                        if son.name == name:
                            if index == len(names_list) - 2:
                                results.append(son)
                            else:
                                match.extend(son._sons)
                    sons.clear()
                    sons.extend(match)
                    match.clear()

        for son in self._sons:
            results.extend(son._find_all(names, with_content))

        return results


class TextOnlyComment(ElementBase):
    """A comment that only contains text, not other elements."""

    def __init__(self, text: str):
        super().__init__("")
        self._text = text

    def is_comment(self) -> bool:
        return True

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        return f"{indent}<!--{self._text}-->\n"


class CData(ElementBase):
    """A CDATA section that contains text."""

    def __init__(self, text: str):
        super().__init__("")
        self._text = text

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        return f"{indent}<![CDATA[{self._text}]]>\n"


class Doctype(ElementBase):
    """A DOCTYPE declaration."""

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
    """An XML element that can contain attributes, content, and child elements."""

    def __init__(self, name: str):
        super().__init__(name)
        self.attributes = {}
        self._is_empty = False  # whether the element is self-closing

    def uncomment(self):
        pass

    def comment_out(self):
        """Convert this element into a comment.
        raises IllegalOperation, if any parent or any descended is a comment
        """

        def find_comment_son(element: "Element") -> bool:
            if element.is_comment():
                return True
            for a_son in element._sons:
                if find_comment_son(a_son):
                    return True
            return False

        parent = self.parent
        while parent:
            if parent.is_comment():
                raise IllegalOperation("Cannot comment out an element whose parent is a comment")
            parent = parent.parent

        for son in self._sons:
            if find_comment_son(son):
                raise IllegalOperation("Cannot comment out an element whose descended is a comment")

        self.__class__ = Comment

    def _to_string(self, index: int, indentation: str, with_end_line=True) -> str:
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
                result = f"{indent}{opening_tag}{self.content}\n{children_str}{indent}{closing_tag}"
            else:
                result = f"{indent}{opening_tag}{self.content}{closing_tag}"

        if with_end_line:
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
            return self._find_one(name, with_content=with_content)
        else:
            return self._find_all(name, with_content=with_content)


class Comment(Element):
    """An XML comment that can contain other elements."""

    def __init__(self, name: str):
        super().__init__(name)

    def is_comment(self) -> bool:
        return True

    def uncomment(self):
        """Convert this comment back into a normal element."""
        self.__class__ = Element

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        if len(self._sons) == 0:
            return f"{indent}<!-- {super()._to_string(0, indentation, False)} -->\n"
        else:
            return f"{indent}<!--\n{super()._to_string(index +1, indentation, False)}\n{indent}-->\n"
