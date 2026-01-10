from __future__ import annotations

from typing import Union
import warnings
import re


class IllegalOperation(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def _check_name_match(element: ElementBase, names: str, case_sensitive: bool) -> bool:
    if names:
        if case_sensitive:
            if element.name != names:
                return False
        else:
            if element.name.casefold() != names.casefold():
                return False
    return True


def _check_content_match(element: ElementBase, with_content: str, case_sensitive: bool) -> bool:
    if with_content is None:
        return True
    if case_sensitive:
        if element.content == with_content:
            return True
    elif element.content.casefold() == with_content.casefold():
        return True

    return False


class ElementBase:
    def __init__(self, name: str):
        self._name = name
        self._sons = []
        self._parent: "ElementBase|None" = None
        self._content = ""
        self._orig_start_index: int = 0
        self._orig_end_index: int = 0
        self._orig_start_line_number: int = 0
        self._orig_end_line_number: int = 0
        self._is_modified: bool = False

    @property
    def content(self) -> str:
        """Get the content of the element."""
        return self._content

    @content.setter
    def content(self, new_content: str):
        """Set the content of the element."""
        self._content = str(new_content)
        self._is_modified = True

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
        _XML_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.:-]*$")
        if not bool(_XML_NAME_RE.match(new_name)):
            raise ValueError(f"Invalid tag name '{new_name}'")

        self._name = new_name
        self._is_modified = True

    def __repr__(self):
        return f"{self.name}"

    def is_comment(self) -> bool:
        """Check if the element is a comment."""
        return False

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
        self._is_modified = True
        # TODO - update _orig_start_index and _orig_end_index acourding to siblin? of parent if no siblinbs?

    def add_after(self, sibling: "Element"):
        """Add this element after the given sibling element."""
        parent = sibling._parent
        if parent is None:
            raise ValueError(f"Element {sibling.name} has no parent")
        index = parent._sons.index(sibling)
        parent._sons.insert(index + 1, self)
        self._parent = parent
        self._is_modified = True

    def add_as_last_son_of(self, parent: "Element"):
        """Add this element as a son of the given parent element."""
        parent._sons.append(self)
        self._parent = parent
        self._is_modified = True
        if parent._is_empty:
            parent._is_empty = False
            parent._is_modified = True

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
        self._is_modified = True

    def remove(self):
        """Remove this element from its parent's sons."""
        self._parent._sons.remove(self)
        self._parent = None
        self._is_modified = True

    def _get_index_in_parent(self):
        index = 0
        for son in self._parent._sons:
            if son == self:
                return index
            index += 1

        return -1

    def _get_element_above(self):
        index = self._get_index_in_parent()
        if index > 0:
            return self._parent._sons[index - 1]
        else:
            return self.parent

    def _get_element_below(self):
        index = self._get_index_in_parent()
        if index < len(self._parent._sons) - 1:
            return self._parent._sons[index + 1]
        else:
            return self._parent

    def _find_one_in_sons(
        self, names_list: list[str], with_content: str = None, case_sensitive: bool = True
    ) -> ElementBase | None:
        if not names_list:
            return self
        for name in names_list:
            for son in self._sons:
                if _check_name_match(son, name, case_sensitive):
                    found = son._find_one_in_sons(names_list[1:], with_content, case_sensitive)
                    if found:
                        if _check_content_match(found, with_content, case_sensitive):
                            return found
        return None

    def _find_one(self, names: str, with_content: str, case_sensitive: bool) -> ElementBase | None:

        if _check_name_match(self, names, case_sensitive):
            if _check_content_match(self, with_content, case_sensitive):
                return self

        names_list = names.split("|")

        if len(names_list) > 1:
            if _check_name_match(self, names_list[0], case_sensitive):
                found = self._find_one_in_sons(names_list[1:], with_content, case_sensitive)
                if found:
                    return found

        for son in self._sons:
            found = son._find_one(names, with_content, case_sensitive)
            if found:
                return found
        return None

    def _find_all(self, names: str, with_content: str, case_sensitive: bool) -> list[Element]:
        results = []
        if _check_name_match(self, names=names, case_sensitive=case_sensitive):
            if _check_content_match(self, with_content, case_sensitive):
                results.extend([self])
                for son in self._sons:
                    results.extend(son._find_all(names, with_content, case_sensitive))
                return results

        names_list = names.split("|")

        if _check_name_match(self, names_list[0], case_sensitive):
            if _check_content_match(self, with_content, case_sensitive):
                sons = []
                sons.extend(self._sons)
                match = []
                for index, name in enumerate(names_list[1:]):
                    for son in sons:
                        if _check_name_match(son, name, case_sensitive):
                            if index == len(names_list) - 2:
                                results.append(son)
                            else:
                                match.extend(son._sons)
                    sons.clear()
                    sons.extend(match)
                    match.clear()

        for son in self._sons:
            results.extend(son._find_all(names, with_content, case_sensitive))

        return results


class TextOnlyComment(ElementBase):
    """A comment that only contains text, not other elements."""

    def __init__(self, text: str):
        super().__init__("")
        self._text = text

    @property
    def text(self) -> str:
        """Get the content of the element."""
        return self._text

    @text.setter
    def text(self, text: str):
        """Set the content of the element."""
        self._text = text
        self._is_modified = True

    def is_comment(self) -> bool:
        return True

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        return f"{indent}<!--{self._text}-->\n"

    def __repr__(self):
        return f"{self.name} text: {self._text}"


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
        if self.parent.is_comment():
            raise IllegalOperation("Cannot comment out an element whose parent is a comment")

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
        self._is_modified = True

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

            if "\n" in self.content:
                content = f"\n{indentation * (index + 1)}" + self.content.replace(
                    "\n", f"\n{indentation * (index + 1)}"
                )
                if children_str:
                    result = f"{indent}{opening_tag}{content}\n{children_str}{indent}{closing_tag}"
                else:
                    result = f"{indent}{opening_tag}{content}\n{indent}{closing_tag}"
            else:
                if children_str:
                    result = f"{indent}{opening_tag}{self.content}\n{children_str}{indent}{closing_tag}"
                else:
                    result = f"{indent}{opening_tag}{self.content}{closing_tag}"

        if with_end_line:
            result += "\n"
        return result

    def find(
        self, name: str = None, only_one: bool = True, with_content: str = None, case_sensitive: bool = True
    ) -> Union["Element", list["Element"], None]:
        """
        Find element(s) by name or content or both
        :param name: name of the element to find, can be nested using |, e.g. "parent|child|subchild"
        :param only_one: stop at first find or return all found elements
        :param with_content: filter by content
        :param case_sensitive: whether the search is case-sensitive, default is True
        :return: the elements found,
                if found, return the elements that match the last name in the path,
                if not found, return None if only_one is True, else return empty list
        """
        if only_one:
            return self._find_one(name, with_content=with_content, case_sensitive=case_sensitive)
        else:
            return self._find_all(name, with_content=with_content, case_sensitive=case_sensitive)


class Comment(Element):
    """An XML comment that can contain other elements."""

    def __init__(self, name: str):
        super().__init__(name)

    def is_comment(self) -> bool:
        return True

    def uncomment(self):
        """Convert this comment back into a normal element."""
        if self.parent.is_comment():
            raise IllegalOperation("Cannot uncomment an element whose parent is a comment")
        self.__class__ = Element
        self._is_modified = True

    def _to_string(self, index: int, indentation: str) -> str:
        indent = indentation * index
        if len(self._sons) == 0:
            return f"{indent}<!-- {super()._to_string(0, indentation, False)} -->\n"
        else:
            return f"{indent}<!--\n{super()._to_string(index +1, indentation, False)}\n{indent}-->\n"
