from pathlib import Path
from enum import Enum
import re
from typing import Any

from .element import ElementBase, Element, Comment, CData, Doctype, TextOnlyComment


class BadXMLFormat(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TokenType(Enum):
    comment_start = 1
    full = 2
    closing = 3
    content = 4
    c_data = 5
    doctype = 6


def _divide_to_tokens(file_content):
    tokens = []

    last_char = ""
    last_index = 0

    index = 0
    while index < len(file_content):
        char = file_content[index]

        if char == "!" and index < len(file_content) + 10:
            # check fot CDATA:
            if file_content[index : index + 8] == "![CDATA[" and last_char == "<":
                cdata_end = file_content.find("]]>", index)
                if cdata_end == -1:
                    raise BadXMLFormat("Malformed CDATA section")
                cdata_content = file_content[index + 8 : cdata_end]
                tokens.append((TokenType.c_data, cdata_content))
                last_index = cdata_end + 2
                last_char = ">"
                index = last_index + 1
                continue
            elif file_content[index : index + 8] == "!DOCTYPE":
                start = file_content.find("[", index)
                if start == -1:
                    raise BadXMLFormat("Malformed DOCTYPE declaration")
                doctype = file_content[index:start]
                tokens.append((TokenType.doctype, doctype))

                last_char = ""
                last_index = start + 1
                index = start + 1
                continue

        if char == ">":
            if last_char == "<":
                tokens.append((TokenType.full, file_content[last_index + 1 : index].strip()))
            else:
                tokens.append((TokenType.closing, file_content[last_index + 1 : index].strip()))
            last_char = char
            last_index = index
        elif char == "<":
            if last_char == "<":
                # this is a case of opening a comment of type <!-- TAG>...</TAG --> (or bad format)
                tokens.append((TokenType.comment_start, file_content[last_index + 1 : index].strip()))
            if last_char == ">":
                text = file_content[last_index + 1 : index - 1].strip()
                if text:
                    tokens.append((TokenType.content, file_content[last_index + 1 : index].strip()))
            last_char = char
            last_index = index
        index += 1

    return tokens


def _add_ready_token(ready_nodes, element: ElementBase, depth: int):
    if depth in ready_nodes:
        ready_nodes[depth].append(element)
    else:
        ready_nodes[depth] = [element]

    if depth + 1 in ready_nodes:
        element._sons = ready_nodes[depth + 1]
        del ready_nodes[depth + 1]
        for son in element._sons:
            son._parent = element


def _parse_element(data: str) -> Element:
    if data[0] == "!":
        return Element(data)
    tag_name_match = re.match(r"(\S+)\s*(.*)", data)

    if not tag_name_match:
        raise BadXMLFormat(f'Could not parse tag name and attributes from line: "{data}"')
    name = tag_name_match.group(1)
    if not name[0].isalpha():
        raise BadXMLFormat(f"Tag {name} can not starts with a number")
    attributes_string = tag_name_match.group(2).strip()
    attributes = {}

    for match in re.compile(r"(\S+)\s*=\s*([^\s=]+|\"[^\"]*\"|\'[^\']*\')").finditer(attributes_string):
        attr_name, attr_value = match.groups()
        attributes[attr_name] = attr_value.strip().strip('"')

    element = Element(name)
    element.attributes = attributes
    return element


class SmartXML:
    def __init__(self, data: Path = None):
        self._file_name = data
        self._declaration = ""
        self._tree = None
        self._doctype = None
        if data:
            self._tree, self._doctype = self._read(self._file_name)

    @property
    def tree(self) -> ElementBase:
        """Get the root element of the XML tree."""
        return self._tree

    @property
    def declaration(self) -> str:
        """Get the XML declaration."""
        return self._declaration

    def _parse_declaration(self, file_content: str):
        start = file_content.find("<?xml")
        end = file_content.find("?>", start)
        if (start >= 0 and end == -1) or (start == -1 and end > 0):
            raise BadXMLFormat("Malformed XML declaration")
        if start > 0:
            raise BadXMLFormat("XML declaration must be at the beginning of the file")
        if start >= 0 and end >= 0:
            declaration = file_content[start + 5 : end].strip()
            self._declaration = declaration
            file_content = file_content[end + 2 :]

        return file_content

    def read(self, file_name: Path) -> None:
        """
        Read and parse the XML file into an element tree.
        :param file_name: Path to the XML file
        :raises:
            TypeError: if file_name is not a pathlib.Path object
            FileNotFoundError: if file_name does not exist
            BadXMLFormat: if the XML format is invalid
        """
        if not isinstance(file_name, Path):
            raise TypeError("file_name must be a pathlib.Path object")
        if not file_name.exists():
            raise FileNotFoundError(f"File {file_name} does not exist")

        self._tree, self._doctype = self._read(file_name)

    def _read(self, file_name: Path) -> tuple[Any, None] | tuple[Any, Any]:
        self._file_name = file_name
        ready_nodes = {}  # depth -> list of elements
        incomplete_nodes = []
        depth = 0

        count_comment_start = 0
        count_comment_end = 0

        file_content = self._file_name.read_text()
        file_content = self._parse_declaration(file_content)

        tokens = _divide_to_tokens(file_content)

        for token in tokens:
            token_type = token[0]
            data = token[1]

            if token_type == TokenType.full:
                if data.endswith("/"):
                    data = data[:-1].strip()
                    element = _parse_element(data)
                    element._is_empty = True
                    if incomplete_nodes[-1].name == "!--":
                        element.comment_out()
                    _add_ready_token(ready_nodes, element, depth + 1)

                elif data.startswith("/"):
                    data = data[1:].strip()
                    element = incomplete_nodes.pop()
                    if data.endswith("--"):
                        # this is a case of closing a comment of type <!-- TAG>...</TAG -->
                        data = data[:-2].strip()
                        count_comment_end += 1

                    if element.name != data:
                        raise BadXMLFormat(f"Mismatched XML tags, opening: {element.name}, closing: {data}")
                    _add_ready_token(ready_nodes, element, depth)
                    depth -= 1

                elif data.startswith("!--"):
                    if incomplete_nodes and isinstance(incomplete_nodes[-1], Comment):
                        raise BadXMLFormat("Nested comments are not allowed")

                    if data.endswith("--"):
                        element = TextOnlyComment(data[3:-2].strip())
                        _add_ready_token(ready_nodes, element, depth + 1)
                    else:
                        # this is a case of opening a comment of type <!-- TAG>...</TAG -->
                        count_comment_start += 1
                        name = data[3:].strip()
                        incomplete_nodes.append(Comment(name))
                        depth += 1

                else:
                    element = _parse_element(data)
                    if incomplete_nodes and incomplete_nodes[-1].name == "!--":
                        element.comment_out()
                    parent_is_doctype = incomplete_nodes and isinstance(incomplete_nodes[-1], Doctype)
                    if parent_is_doctype:
                        _add_ready_token(ready_nodes, element, depth + 1)
                    else:
                        incomplete_nodes.append(element)
                        depth += 1

            elif token_type == TokenType.comment_start:
                if incomplete_nodes and isinstance(incomplete_nodes[-1], Comment):
                    raise BadXMLFormat("Nested comments are not allowed")
                count_comment_start += 1
                if data != "!--":
                    raise BadXMLFormat("Malformed comment closure")
                element = Comment(data)  # This is a placeholder, indicating future soms are in a comment
                incomplete_nodes.append(element)

            elif token_type == TokenType.closing:
                element = incomplete_nodes.pop()
                if data == "--":
                    count_comment_end += 1
                if isinstance(element, Doctype):
                    _add_ready_token(ready_nodes, element, depth)
                    depth -= 1

            elif token_type == TokenType.content:
                incomplete_nodes[-1].content = data

            elif token_type == TokenType.doctype:
                element = Doctype(data)
                incomplete_nodes.append(element)
                depth += 1

            elif token_type == TokenType.c_data:
                element = CData(data)
                _add_ready_token(ready_nodes, element, depth + 1)

        if count_comment_start != count_comment_end:
            raise BadXMLFormat("Mismatched comment tags")

        if len(ready_nodes.get(1, [])) == 1:
            return ready_nodes[1][0], None
        if (
            len(ready_nodes.get(1, [])) == 2
            and isinstance(ready_nodes[1][0], Doctype)
            and isinstance(ready_nodes[1][1], Element)
        ):
            return ready_nodes[1][1], ready_nodes[1][0]
        raise BadXMLFormat("xml contains more than one outer element")

    def write(self, file_name: Path = None, indentation: str = "\t") -> str | None:
        """Write the XML tree back to the file.
        :param file_name: Path to the XML file, if None, overwrite the original file
        :param indentation: string used for indentation, default is tab character
        :return: XML string if file_name is None, else None
        :raises:
            ValueError: if file name is not specified
            TypeError: if file_name is not a pathlib.Path object
            FileNotFoundError: if file_name does not exist
        """

        if file_name:
            self._file_name = file_name
        if not self._file_name:
            raise ValueError("File name is not specified")

        with open(self._file_name, "w") as file:
            if self._declaration:
                file.write(f"<?xml {self._declaration}?>\n")
            file.write(self.to_string(indentation))

    def to_string(self, indentation: str = "\t") -> str:
        """
        Convert the XML tree to a string.
        :param indentation: string used for indentation, default is tab character
        :return: XML string
        """
        result = self._doctype.to_string(indentation) if self._doctype else ""
        return result + self._tree.to_string(indentation)

    def find(
        self,
        name: str = "",
        only_one: bool = True,
        with_content: str = None,
    ) -> Element | list[Element] | None:
        """
        Find element(s) by name or content or both
        :param name: name of the element to find, can be nested using |, e.g. "parent|child|subchild"
        :param only_one: stop at first find or return all found elements
        :param with_content: filter by content
        :return: the elements found,
                if found, return the elements that match the last name in the path,
                if not found, return None if only_one is True, else return empty list
        :raises:
            ValueError: if neither name nor with_content is provided

        """
        if not name and with_content is None:
            raise ValueError("At least one search criteria must be provided")
        return self._tree.find(name, only_one, with_content)
