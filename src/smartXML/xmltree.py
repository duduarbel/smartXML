from __future__ import annotations

import os
from pathlib import Path
from enum import Enum

from .element import ElementBase, Element, CData, Doctype, TextOnlyComment, PlaceHolder, ContentOnly


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
    def __init__(
        self,
        token_type: TokenType,
        data: str,
        line_number: int,
        start_index: int,
        end_index: int,
        indentation: str = "",
    ):
        self.token_type = token_type
        self.data = data
        self.line_number = line_number
        self.start_index = start_index
        self.end_index = end_index
        self.indentation = indentation

    def __repr__(self):
        indentation = self.indentation.replace(" ", "-")
        return f"{self.token_type.name}: {self.data} indexes: {self.start_index}-{self.end_index} indentation:'{indentation}'"


def _divide_to_tokens(file_content):
    tokens = []

    last_char: str = ""
    last_index: int = 0
    line_number: int = 1
    use_tabs_for_indentation: bool = False
    index_of_start_line: int = 0

    def create_indentation() -> str:
        if not use_tabs_for_indentation:
            return " " * (last_index - index_of_start_line)

        tab_width = 4
        total_width = 0
        indent = file_content[index_of_start_line:last_index]
        for char in indent:
            if char == "\t":
                total_width = total_width + tab_width
            else:
                total_width = total_width + 1

        num_tabs = total_width // tab_width
        num_spaces = total_width % tab_width

        return ("\t" * num_tabs) + (" " * num_spaces)

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
                        last_index,
                        index,
                        create_indentation(),
                    )
                )
            else:
                tokens.append(
                    Token(
                        TokenType.closing,
                        file_content[last_index + 1 : index].strip(),
                        line_number,
                        last_index,
                        index,
                    )
                )
            last_char = char
            last_index = index
        elif char == "<":
            if last_char == "<":
                raise BadXMLFormat(f"Malformed element in line {line_number}")
            elif last_char == ">":
                text = file_content[last_index + 1 : index]
                text = text.strip()
                if text:
                    tokens.append(Token(TokenType.content, text, line_number, last_index, last_index + 1 + len(text)))
            last_char = char
            last_index = index
        elif char == "\n":
            line_number += 1
            use_tabs_for_indentation = False
            index_of_start_line = index + 1
        elif char == "!":
            if file_content[index + 1] == "-":
                # !--
                comment_end_index = file_content.find("-->", index)
                if comment_end_index == -1:
                    raise BadXMLFormat(f"Malformed comment in line {line_number}")

                comment = file_content[index + 3 : comment_end_index]
                tokens.append(Token(TokenType.comment, comment, line_number, last_index, comment_end_index + 2))

                last_char = ""
                last_index = comment_end_index + 3
                index = comment_end_index + 2
            elif file_content[index + 1] == "[":
                # ![CDATA[
                cdata_end = file_content.find("]]>", index)
                if cdata_end == -1:
                    raise BadXMLFormat(f"Malformed CDATA section in line {line_number}")
                cdata_content = file_content[index + 8 : cdata_end]
                tokens.append(Token(TokenType.c_data, cdata_content, line_number, last_index, index))
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
                tokens.append(Token(TokenType.doctype, doctype, line_number, last_index, index))

                last_char = ""
                last_index = start + 1
                index = start + 1
                continue
        elif char == "\t":
            use_tabs_for_indentation = True
        index += 1

    return tokens


def _add_ready_token(
    incomplete_nodes, ready_nodes, element: ElementBase, depth: int, end_index: int, end_line_number: int
):
    if len(incomplete_nodes) == 0:
        ready_nodes.setdefault(depth, []).append(element)
    else:
        incomplete_nodes[-1]._sons.append(element)
        element._parent = incomplete_nodes[-1]

    element._format.end_index = end_index
    element._format.end_line_number = end_line_number


def _parse_element(text: str, start_index: int, start_line_number: int) -> Element:
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
    element._format.start_index = start_index
    element._format.start_line_number = start_line_number
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
                element: ElementBase = _parse_element(data[:-1], token.start_index, line_number)
                element._is_empty = True
                element._format.indentation = token.indentation
                _add_ready_token(incomplete_nodes, ready_nodes, element, depth + 1, token.end_index, line_number)
                element._format.index_after_content = token.end_index + 1

            elif data.startswith("/"):
                data = data[1:].strip()
                element = incomplete_nodes.pop()

                if element.name != data:
                    raise BadXMLFormat(
                        f"Mismatched XML tags, opening: {element.name}, closing: {data}, in line {line_number}"
                    )
                _add_ready_token(incomplete_nodes, ready_nodes, element, depth, token.end_index, line_number)
                depth -= 1

            else:
                if incomplete_nodes and isinstance(incomplete_nodes[-1], Doctype):
                    element = Element(data)
                    _add_ready_token(incomplete_nodes, ready_nodes, element, depth + 1, token.end_index, line_number)
                else:
                    element = _parse_element(data, token.start_index, line_number)
                    element._format.end_index = token.end_index
                    element._format.indentation = token.indentation
                    element._format.index_after_content = token.end_index + 1

                    incomplete_nodes.append(element)
                    depth += 1

        elif token_type == TokenType.comment:
            if data.find("!--") != -1:
                raise BadXMLFormat(f"Nested comments are not allowed in line {line_number}")
            try:
                if data.strip()[0] != "<":
                    elements_in_comment = _read_elements("<" + data + ">")  # support the case of <!--TAG...-->
                else:
                    elements_in_comment = _read_elements(data)
                # if len(elements_in_comment) == 1:
                for comment in elements_in_comment:
                    # comment = elements_in_comment[0]
                    comment.comment_out()
                    comment._format.start_index = token.start_index
                    _add_ready_token(incomplete_nodes, ready_nodes, comment, depth + 1, token.end_index, line_number)
                continue
            except Exception:
                # The content of the comment can not be parsed, so handle this as plain text
                pass

            element = TextOnlyComment(data)
            element._format.start_index = token.start_index
            element._format.start_line_number = line_number

            _add_ready_token(
                incomplete_nodes,
                ready_nodes,
                element,
                depth + 1,
                element._format.start_index + len(data) + 6,
                line_number,
            )

        elif token_type == TokenType.closing:
            element = incomplete_nodes.pop()
            _add_ready_token(incomplete_nodes, ready_nodes, element, depth, token.end_index, line_number)
            depth -= 1

        elif token_type == TokenType.content:
            data = data.splitlines()
            for content in data:
                contentOnly = ContentOnly(content.strip())
                contentOnly._format.start_index = token.start_index + 1
                contentOnly._format.start_line_number = line_number
                contentOnly._format.indentation = token.indentation
                _add_ready_token(incomplete_nodes, ready_nodes, contentOnly, depth + 1, token.end_index, line_number)

        elif token_type == TokenType.doctype:
            element = Doctype(data)
            incomplete_nodes.append(element)
            depth += 1

        elif token_type == TokenType.c_data:
            element = CData(data)
            _add_ready_token(incomplete_nodes, ready_nodes, element, depth + 1, token.end_index, line_number)

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

    def write(self, file_name: Path = None, indentation: str = "\t", preserve_format: bool = False) -> str | None:
        """Write the XML tree back to the file.
        :param file_name: Path to the XML file, if None, overwrite the original file
        :param indentation: string used for indentation, default is tab character
        :return: XML string if file_name is None, else None
        :raises:
            ValueError: if file name is not specified
            TypeError: if file_name is not a pathlib.Path object
            FileNotFoundError: if file_name does not exist
        """
        if not file_name:
            file_name = self._file_name
        if not file_name:
            raise ValueError("File name is not specified")

        tmp_file = file_name.resolve().with_name(file_name.name + ".tmp")

        result = self.to_string(indentation=indentation, preserve_format=preserve_format)
        with open(tmp_file, "w", encoding="utf-8") as file:
            file.write(result)
        os.replace(tmp_file, file_name)

    def to_string(self, indentation: str = "\t", preserve_format: bool = False) -> str:
        """
        Convert the XML tree to a string.
        :param indentation: string used for indentation, default is tab character
        :return: XML string
        """
        result = ""
        if self._declaration:
            result = f"<?xml {self._declaration}?>\n"
        if self._doctype:
            result = result + self._doctype.to_string(indentation)

        if not preserve_format:
            result = result + self._tree.to_string(indentation)
            return result

        if self.tree._is_modified:
            return self._tree.to_string(0, indentation)

        modifications = []

        def collect_modification(element: ElementBase):
            if element._is_modified:
                if element._format.start_index == 0:  # new element
                    element_above = element._get_element_above()
                    if element_above != element._parent:
                        new_indentation = element_above._format.indentation
                        index_of_element = element_above._format.end_index + 1
                    else:
                        if len(element._parent._sons) > 0 and isinstance(element._parent._sons[0], ContentOnly):
                            index_of_element = element._parent._sons[0]._format.end_index
                        else:
                            index_of_element = element._parent._format.index_after_content

                        brother_below = element._get_lower_sibling()
                        if brother_below:
                            new_indentation = brother_below._format.indentation
                        else:
                            new_indentation = element._parent._format.indentation + indentation
                else:
                    new_indentation = element._format.indentation
                    index_of_element = element._format.start_index

                modifications.append((element, index_of_element, new_indentation))
            else:
                for son in element._sons:
                    collect_modification(son)

        def add_clean_indentation(input_string: str, _indentation: str):
            if "\t" not in _indentation and "\t" not in input_string:
                return _indentation + input_string
            input_string = _indentation + input_string
            stripped_l = input_string.lstrip()
            indent_part = input_string[: len(input_string) - len(stripped_l)]
            tab_width = 4

            visual_width = len(indent_part.expandtabs(tab_width))

            num_tabs = visual_width // tab_width
            remainder_spaces = visual_width % tab_width

            return ("\t" * num_tabs) + (" " * remainder_spaces) + stripped_l

        original_content = self._file_name.read_text()

        collect_modification(self._tree)
        if not modifications:
            return original_content

        index = 0
        for element, index_of_element, new_indentation in modifications:
            is_new_element: bool = True if element._format.start_index == element._format.end_index else False

            result = result + original_content[index:index_of_element]

            if isinstance(element, PlaceHolder):  # TODO - should be removed
                if is_new_element:
                    index = index_of_element
                else:
                    brother_below = element._get_lower_sibling()
                    index = brother_below._format.start_index  # TODO - wrong. what if no brother below?
                continue

            text = element._to_string(0, indentation)
            text_lines = text.splitlines()

            if is_new_element:
                for line in text_lines:
                    line = add_clean_indentation(line, new_indentation)
                    result = result + "\n" + line

                index = index_of_element
            else:
                if len(text_lines) == 1:
                    result = result + text_lines[0]
                else:
                    result = result + text_lines[0] + "\n"
                    for line in text_lines[1:-1]:
                        result = result + add_clean_indentation(line + "\n", new_indentation)
                    result = result + add_clean_indentation(text_lines[-1], new_indentation)

                index = element._format.end_index + 1

        result = result + original_content[index:]
        return result

    def find(
        self, name: str = "", only_one: bool = True, with_content: str = None, case_sensitive: bool = True
    ) -> Element | list[Element] | None:
        """
        Find element(s) by name or content or both
        :param name: name of the element to find, can be nested using |, e.g. "parent|child|subchild"
        :param only_one: stop at first find or return all found elements
        :param with_content: filter by content
        :param case_sensitive: whether the search is case-sensitive, default is True
        :return: the elements found,
                if found, return the elements that match the last name in the path,
                if not found, return None if only_one is True, else return empty list
        :raises:
            ValueError: if neither name nor with_content is provided

        """
        if not name and with_content is None:
            raise ValueError("At least one search criteria must be provided")
        return self._tree.find(name, only_one, with_content, case_sensitive)
