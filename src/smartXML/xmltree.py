from __future__ import annotations
from pathlib import Path
from enum import Enum

from .element import ElementBase, Element, CData, Doctype, TextOnlyComment


class BadXMLFormat(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TokenType(Enum):
    comment = 1
    full_tag_name = 2
    closing = 3
    content = 4
    c_data = 5
    doctype = 6


class Token:
    def __init__(self, token_type: TokenType, data: str, line_number: int):
        self.token_type = token_type
        self.data = data
        self.line_number = line_number

    def __repr__(self):
        return f"{self.token_type.name}: {self.data}"


def _divide_to_tokens(file_content):
    tokens = []

    last_char = ""
    last_index = 0
    line_number = 1

    index = 0
    length = len(file_content)
    while index < length:
        char = file_content[index]

        if char == ">":
            if last_char == "<":
                tokens.append(
                    Token(
                        TokenType.full_tag_name,
                        file_content[last_index + 1 : index].strip(),
                        line_number,
                    )
                )
            else:
                tokens.append(
                    Token(
                        TokenType.closing,
                        file_content[last_index + 1 : index].strip(),
                        line_number,
                    )
                )
            last_char = char
            last_index = index
        elif char == "<":
            if last_char == "<":
                raise BadXMLFormat(f"Malformed element in line {line_number}")
            if last_char == ">":
                text = file_content[last_index + 1 : index - 1].strip()
                if text:
                    tokens.append(
                        Token(
                            TokenType.content,
                            file_content[last_index + 1 : index].strip(),
                            line_number,
                        )
                    )
            last_char = char
            last_index = index
        elif char == "\n":
            line_number += 1
        elif char == "!":
            if file_content[index + 1] == "-":
                # !--
                comment_end_index = file_content.find("-->", index)
                if comment_end_index == -1:
                    raise BadXMLFormat(f"Malformed comment in line {line_number}")

                comment = file_content[index + 3 : comment_end_index]
                tokens.append(Token(TokenType.comment, comment, line_number))

                last_char = ""
                last_index = comment_end_index + 3
                index = comment_end_index + 3
            elif file_content[index + 1] == "[":
                # ![CDATA[
                cdata_end = file_content.find("]]>", index)
                if cdata_end == -1:
                    raise BadXMLFormat(f"Malformed CDATA section in line {line_number}")
                cdata_content = file_content[index + 8 : cdata_end]
                tokens.append(Token(TokenType.c_data, cdata_content, line_number))
                last_index = cdata_end + 2
                last_char = ">"
                index = last_index + 1
                continue
            elif file_content[index + 1] == "D":
                # !DOCTYPE
                start = file_content.find("[", index)
                if start == -1:
                    raise BadXMLFormat(f"Malformed DOCTYPE declaration in line {line_number}")
                doctype = file_content[index:start]
                tokens.append(Token(TokenType.doctype, doctype, line_number))

                last_char = ""
                last_index = start + 1
                index = start + 1
                continue

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


def _parse_element(text: str) -> Element:
    index = 0
    text = text.strip()
    length = len(text)

    def find_next_word():
        nonlocal index
        while text[index].isspace():
            index += 1
        start = index
        while index < length and not text[index].isspace() and text[index] != "=":
            index += 1

        return text[start:index]

    def find_next_assignment_sign():
        nonlocal index
        while text[index].isspace():
            index += 1
        if text[index] != "=":
            raise BadXMLFormat(f'Expected "=" in element definition: "{text}"')
        index += 1

    def find_next_string():
        nonlocal index
        while text[index].isspace():
            index += 1
        if text[index] != '"':
            raise BadXMLFormat(f'Expected "=" in element definition: "{text}"')
        index += 1

        start = index
        while text[index] != '"':
            index += 1

        word = text[start:index]
        index += 1

        return word

    name = find_next_word()
    if not name[0].isalpha():
        raise BadXMLFormat(f'Element name must start with a letter in element definition: "{text}"')

    attributes: dict[str, str] = {}

    while index < length:
        key = find_next_word()
        find_next_assignment_sign()
        value = find_next_string()

        if not key or not key[0].isalpha():
            raise BadXMLFormat(f'Could not parse attribute name in element definition: "{text}"')
        attributes[key] = value

    element = Element(name)
    element.attributes = attributes
    return element


def _read_elements(text: str) -> list[Element]:
    ready_nodes = {}  # depth -> list of elements
    incomplete_nodes = []
    depth = 0

    tokens = _divide_to_tokens(text)

    for token in tokens:
        token_type = token.token_type
        data = token.data
        line_number = token.line_number

        if token_type == TokenType.full_tag_name:
            # this token is anything that is between < and >
            if data.endswith("/"):
                element = _parse_element(data[:-1])
                element._is_empty = True
                _add_ready_token(ready_nodes, element, depth + 1)

            elif data.startswith("/"):
                data = data[1:].strip()
                element = incomplete_nodes.pop()

                if element.name != data:
                    raise BadXMLFormat(
                        f"Mismatched XML tags, opening: {element.name}, closing: {data}, in line {line_number}"
                    )
                _add_ready_token(ready_nodes, element, depth)
                depth -= 1

            else:
                if incomplete_nodes and isinstance(incomplete_nodes[-1], Doctype):
                    element = Element(data)
                    _add_ready_token(ready_nodes, element, depth + 1)
                else:
                    element = _parse_element(data)
                    incomplete_nodes.append(element)
                    depth += 1

        elif token_type == TokenType.comment:
            if data.find("!--") != -1:
                raise BadXMLFormat(f"Nested comments are not allowed in line {line_number}")

            try:
                elements_in_comment = _read_elements(data)
                for comment in elements_in_comment:
                    comment.comment_out()
                    _add_ready_token(ready_nodes, comment, depth + 1)
            except Exception:
                # The content of the comment can not be parsed, so handle this as plain text
                _add_ready_token(ready_nodes, TextOnlyComment(data), depth + 1)

        elif token_type == TokenType.closing:
            element = incomplete_nodes.pop()
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

    if incomplete_nodes:
        unclosed = incomplete_nodes[-1]
        raise BadXMLFormat(f"Unclosed tag: {unclosed.name}")

    if ready_nodes != {1: ready_nodes.get(1)}:
        raise BadXMLFormat("xml contains more than one outer element")

    return ready_nodes[1]


class SmartXML:
    def __init__(self, data: Path = None):
        self._file_name = data
        self._declaration = ""
        self._tree = None
        self._doctype = None
        if self._file_name:
            self.read(self._file_name)

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

        self._file_name = file_name
        file_content = self._file_name.read_text()
        self._read_xml(file_content)

    def _read_xml(self, text: str):
        text = self._parse_declaration(text)
        elements = _read_elements(text)

        if len(elements) == 1:
            self._tree = elements[0]
        elif len(elements) == 2 and isinstance(elements[0], Doctype) and isinstance(elements[1], Element):
            self._doctype = elements[0]
            self._tree = elements[1]
        else:
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
