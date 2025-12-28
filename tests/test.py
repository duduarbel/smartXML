import textwrap
from readme_example import test_readme_example

from smartXML.xmltree import SmartXML, BadXMLFormat, _read_elements, _parse_element
from smartXML.element import Element, TextOnlyComment, IllegalOperation
from pathlib import Path
import pytest
import random


test_file_name = "./files/test.tmp.xml"

def _test_tree_integrity(xml_tree: SmartXML):

    def node_tree_integrity(xml: SmartXML, element: Element, name: str):
        for son in element._sons:
            assert (
                son._parent == element
            ), f"Element {son.name} has incorrect parent {son._parent.name if son._parent else 'None'}, expected {element.name}"
            full_name = name + "|" + son.name
            assert full_name == son.get_path()
            found = xml.find(full_name, False)
            assert len(found) >= 1
            assert son in found, f"Element {son.name} not found in path {full_name}"
            node_tree_integrity(xml, son, full_name)

    node_tree_integrity(xml_tree, xml_tree.tree, xml_tree.tree.name)


def __create_file(content: str) -> Path:
    f = open(test_file_name, "w")
    f.write(content)
    f.close()

    return Path(test_file_name)



def test_trimming():
    src = textwrap.dedent(
        """\


        <  root  >


            <  user    id   =   "42"   >

                <
                name >D u d u< / name
                >
                <x>12</x>                <
                /user>
        </ root >

        """
    )
    dst = textwrap.dedent(
        """\
        <root>
        \t<user id="42">
        \t\t<name>D u d u</name>
        \t\t<x>12</x>
        \t</user>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()

    result = file_name.read_text()

    assert result == dst
    _test_tree_integrity(xml)



def test_read_comment1():
    src = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!-- <name0>Dudu</name0> -->
        \t</user>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()

    result = file_name.read_text()

    assert result == src
    _test_tree_integrity(xml)



def test_read_comment2():
    src = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!-- <name0>Dudu</name0> -->
        \t</user>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()

    result = file_name.read_text()

    assert result == src
    _test_tree_integrity(xml)



def test_read_comment3():
    src = textwrap.dedent(
        """\
        <root>
        \t<!-- This is a comment -->
        \t<user id="42"><xxx/><yyy></yyy>
        \t\t<!-- <name0>Dudu</name0> -->
        \t\t<!-- <x>12</x><y>13</y><z into="33"/> -->
        \t\t<!--
        \t\t\t<x1>12</x1>
        \t\t\t<y1>13</y1>
        \t\t\t<z1 into="33"/>
        \t\t-->
        \t\t<name3>Dudu</name3>
        \t</user>
        </root>
        """
    )

    dst = textwrap.dedent(
        """\
        <root>
        \t<!-- This is a comment -->
        \t<user id="42">
        \t\t<xxx/>
        \t\t<yyy></yyy>
        \t\t<!-- <name0>Dudu</name0> -->
        \t\t<!-- <x>12</x> -->
        \t\t<!-- <y>13</y> -->
        \t\t<!-- <z into="33"/> -->
        \t\t<!-- <x1>12</x1> -->
        \t\t<!-- <y1>13</y1> -->
        \t\t<!-- <z1 into="33"/> -->
        \t\t<name3>Dudu</name3>
        \t</user>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()

    result = file_name.read_text()

    assert result == dst
    _test_tree_integrity(xml)



def test_read_comment4():
    src = textwrap.dedent(
        """\
        <root>
        \t<!--TAG>xxx
        \t</TAG  -->
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()

    result = file_name.read_text()
    assert result == src


def test_simple_find_and_get_path():
    file_name = __create_file("<A><B><C><D><D1></D1><D2/><X/></D></C></B><X/></A>")
    xml = SmartXML(file_name)

    element = xml.find("D1")
    path = element.get_path()
    assert path == "A|B|C|D|D1"

    element = xml.find("D2")
    path = element.get_path()
    assert path == "A|B|C|D|D2"

    element = xml.find("C")
    path = element.get_path()
    assert path == "A|B|C"

    element = xml.find("Dccc")
    assert element is None

    element = xml.find("ABC")
    assert element is None

    element = xml.find("X")
    path = element.get_path()
    assert path == "A|B|C|D|X"

    elements = xml.find("X", False)
    assert isinstance(elements, list)
    assert len(elements) == 2
    assert elements[0].get_path() == "A|B|C|D|X"
    assert elements[1].get_path() == "A|X"

    elements = xml.find("Dccc", False)
    assert isinstance(elements, list)
    assert len(elements) == 0

    elements = xml.find("D1", False)
    assert isinstance(elements, list)
    assert len(elements) == 1
    assert elements[0].name == "D1"
    _test_tree_integrity(xml)



def test_complex_find_and_get_path():
    src = textwrap.dedent(
        """\
        <root>
            <A id="1">
                <B/>
                <B>
                    <C id="1">
                        <D>
                        </D>
                    </C>
                </B>
                <A id="2">
                    <B>
                        <C id="2">
                        </C>
                    </B>
                </A>
            </A>
            <X>
                <A id="3">
                    <B>
                        <C id="3">
                            <D>
                            </D>
                        </C>
                    </B>
                </A>
            </X>
            <A id="4">
                <B>
                </B>
            </A>
        </root>

        """
    )
    file_name = __create_file(src)
    xml = SmartXML(file_name)

    ac = xml.find("A|C")
    assert ac is None

    ad = xml.find("A|D")
    assert ad is None

    all_c = xml.find("C", False)
    assert len(all_c) == 3

    all_cd = xml.find("C|D", False)
    assert len(all_cd) == 2

    all_a = xml.find("A", False)
    assert len(all_a) == 4
    abc = xml.find("A|B|C")
    assert abc.attributes["id"] == "1"

    all_abc = xml.find("A|B|C", False)
    assert len(all_abc) == 3

    for index, c in enumerate(all_abc):
        assert c.attributes["id"] == f"{index+1}"

    a = xml.find("A")
    bc = a.find("C|D", False)
    assert len(bc) == 1

    all_a = xml.find("root|A", False)
    assert len(all_a) == 2

    x = a.find("X")
    assert x is None
    _test_tree_integrity(xml)



def test_parent_son():
    src = textwrap.dedent(
        """\
        <root>
            <A>
                <B><C/></B>
                <A>
                    <B><B/></B>
                </A>
            </A>
        </root>

        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    root = xml.find("root")
    assert root.get_path() == "root"

    a = root._sons[0]
    assert a.name == "A"
    assert a._parent == root

    b = a._sons[0]
    assert b.name == "B"
    assert b._parent == a
    c = b._sons[0]
    assert c.name == "C"
    assert c._parent == b
    _test_tree_integrity(xml)



def test_one_line_comment():
    src = textwrap.dedent(
        """\
        <root>
        \t<tag1>Dudu</tag1>
        \t<tag2>Dudu</tag2>
        </root>
        """
    )
    dst1 = textwrap.dedent(
        """\
        <root>
        \t<!-- <tag1>Dudu</tag1> -->
        \t<!-- <tag2>Dudu</tag2> -->
        </root>
        """
    )

    dst2 = textwrap.dedent(
        """\
        <root>
        \t<!-- <tag1>Dudu</tag1> -->
        \t<tag2>Dudu</tag2>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag1 = xml.find("tag1")
    tag1.comment_out()

    tag2 = xml.find("tag2")
    tag2.comment_out()

    xml.write()
    result = file_name.read_text()

    assert result == dst1

    # again
    tag2.comment_out()
    tag2.comment_out()
    tag2.comment_out()

    xml.write()
    result = file_name.read_text()

    assert result == dst1

    tag2.uncomment()

    xml.write()
    result = file_name.read_text()

    assert result == dst2

    tag1.uncomment()

    xml.write()
    result = file_name.read_text()

    assert result == src
    _test_tree_integrity(xml)



def test_nested_comment_1():
    src = textwrap.dedent(
        """\
        <root>
        <!-- 
            <tag2>
                <!-- nested comment -->
            </tag2>
        -->
        </root>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Nested comments are not allowed in line 2"
    assert badXMLFormat.type is BadXMLFormat


def test_nested_comment_2():
    src = textwrap.dedent(
        """\
        <root>
        <!-- 
            <tag2>
                <!-- <tag111><tag33/></tag111> -->
            </tag2>
        -->
        </root>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Nested comments are not allowed in line 2"
    assert badXMLFormat.type is BadXMLFormat



def test_nested_comment_3():
    src = textwrap.dedent(
        """\
        <root>
        <!-- tag2><!-- <tag111><tag33/></tag111> --></tag2 -->
        </root>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Nested comments are not allowed in line 2"
    assert badXMLFormat.type is BadXMLFormat



def test_nested_comment_sons():
    src = textwrap.dedent(
        """\
        <root>
            <tag1> 
                <tag2>
                    <tag3>
                        <tag4/>
                        <tag6/>
                        <tag7>
                            <!-- <lastTag/> -->
                        </tag7>
                    </tag3>
                </tag2>
            </tag1>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    with pytest.raises(IllegalOperation) as badXMLFormat:
        tag1.comment_out()
    assert str(badXMLFormat.value) == "Cannot comment out an element whose descended is a comment"
    assert badXMLFormat.type is IllegalOperation


def test_comment_1():
    src = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<tag1>Dudu</tag1>
        \t\t<tag2>Dudu</tag2>
        \t</user>
        </root>
        """
    )
    dst = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!-- <tag1>Dudu</tag1> -->
        \t\t<!-- <tag2>Dudu</tag2> -->
        \t</user>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag1 = xml.find("tag1")
    tag1.comment_out()
    tag1.comment_out()
    tag1.comment_out()

    tag2 = xml.find("tag2")
    tag2.comment_out()
    tag2.comment_out()
    tag2.comment_out()

    xml.write()
    result = file_name.read_text()
    assert result == dst

    tag1.uncomment()
    tag2.uncomment()

    xml.write()
    result = file_name.read_text()
    assert result == src
    _test_tree_integrity(xml)



def test_comment_2():
    src = textwrap.dedent(
        """\
        <root>
        \t<!--
        \t\t<tag1>tt1</tag1>
        \t\t<tag2>tt2</tag2>
        \t\t<tag3>tt3</tag3>
        \t-->
        </root>
        """
    )
    dst1 = textwrap.dedent(
        """\
        <root>
        \t<!-- <tag1>tt1</tag1> -->
        \t<!-- <tag2>tt2</tag2> -->
        \t<!-- <tag3>tt3</tag3> -->
        </root>
        """
    )
    dst2 = textwrap.dedent(
        """\
        <root>
        \t<tag1>tt1</tag1>
        \t<!-- <tag2>tt2</tag2> -->
        \t<!-- <tag3>tt3</tag3> -->
        </root>
        """
    )
    dst3 = textwrap.dedent(
        """\
        <root>
        \t<tag1>tt1</tag1>
        \t<tag2>tt2</tag2>
        \t<!-- <tag3>tt3</tag3> -->
        </root>
        """
    )

    file_name = __create_file(src)

    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    xml.write()
    result = file_name.read_text()
    assert result == dst1
    tag1.comment_out()
    xml.write()
    result = file_name.read_text()
    assert result == dst1

    tag1.uncomment()
    xml.write()
    result = file_name.read_text()
    assert result == dst2

    tag2 = xml.find("tag2")
    tag2.uncomment()
    xml.write()
    result = file_name.read_text()
    assert result == dst3
    _test_tree_integrity(xml)



def test_one_line_comment2():
    src = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!--<tag1>000</tag1>-->
        \t\t<!--<tag2>aaa</tag2><tag3>bbb</tag3>-->
        \t</user>
        </root>
        """
    )
    dst1 = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!-- <tag1>000</tag1> -->
        \t\t<tag2>aaa</tag2>
        \t\t<!-- <tag3>bbb</tag3> -->
        \t</user>
        </root>
        """
    )
    dst2 = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!-- <tag1>000</tag1> -->
        \t\t<!-- <tag2>aaa</tag2> -->
        \t\t<!-- <tag3>bbb</tag3> -->
        \t</user>
        </root>
        """
    )
    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag2 = xml.find("tag2")
    tag2.uncomment()
    xml.write()
    result = file_name.read_text()
    assert result == dst1
    _test_tree_integrity(xml)

    tag2.comment_out()
    xml.write()
    result = file_name.read_text()
    assert result == dst2
    _test_tree_integrity(xml)



def test_one_line_comment3():
    src = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!--
        \t\t\t<tag1>000</tag1>
        \t\t-->
        \t\t<!--<tag2>aaa</tag2><tag3>bbb</tag3>-->
        \t</user>
        </root>
        """
    )
    dst1 = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!-- <tag1>000</tag1> -->
        \t\t<tag2>aaa</tag2>
        \t\t<!-- <tag3>bbb</tag3> -->
        \t</user>
        </root>
        """
    )
    dst2 = textwrap.dedent(
        """\
        <root>
        \t<user>
        \t\t<!-- <tag1>000</tag1> -->
        \t\t<!-- <tag2>aaa</tag2> -->
        \t\t<!-- <tag3>bbb</tag3> -->
        \t</user>
        </root>
        """
    )
    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag2 = xml.find("tag2")
    tag2.uncomment()
    xml.write()
    result = file_name.read_text()
    assert result == dst1
    _test_tree_integrity(xml)

    tag2.comment_out()
    xml.write()
    result = file_name.read_text()
    assert result == dst2
    _test_tree_integrity(xml)



def test_one_line_comment4():
    src = textwrap.dedent(
        """\
        <root>
        \t\t<!--
        \t\t\t<tag1>000</tag1>
        \t\t-->
        \t\t<!--<tag2>aaa</tag2><tag3>bbb</tag3>-->
        </root>
        """
    )
    dst = textwrap.dedent(
        """\
        <root>
        \t<!-- <tag1>000</tag1> -->
        \t<!-- <tag2>aaa</tag2> -->
        \t<!-- <tag3>bbb</tag3> -->
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag2 = xml.find("tag2")
    tag2.uncomment()
    tag2.comment_out()
    xml.write()
    result = file_name.read_text()
    assert result == dst
    _test_tree_integrity(xml)



def test_one_line_comment5():
    src = textwrap.dedent(
        """\
        <root>
        \t\t<!--<tag2>aaa</tag2><tag3>bbb</tag3>-->
        \t\t<!--
        \t\t\t<tag1>000</tag1>
        \t\t-->
        </root>
        """
    )
    dst = textwrap.dedent(
        """\
        <root>
        \t<!-- <tag2>aaa</tag2> -->
        \t<!-- <tag3>bbb</tag3> -->
        \t<!-- <tag1>000</tag1> -->
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag1 = xml.find("tag1")
    tag3 = xml.find("tag3")
    tag3.uncomment()
    tag3.comment_out()
    tag1.uncomment()
    tag1.comment_out()
    xml.write()
    result = file_name.read_text()
    assert result == dst
    _test_tree_integrity(xml)



def test_comment6():
    src = textwrap.dedent(
        """\
        <root>
        \t\t\t<tag1 id="1">
        \t\t\t\t<tag2>bbb</tag2><tag3>ccc</tag3>
        \t\t\t<tag4/></tag1>
        </root>
        """
    )
    dst1 = textwrap.dedent(
        """\
        <root>
        \t<!--
        \t\t<tag1 id="1">
        \t\t\t<tag2>bbb</tag2>
        \t\t\t<tag3>ccc</tag3>
        \t\t\t<tag4/>
        \t\t</tag1>
        \t-->
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag1 = xml.find("tag1")
    tag1.comment_out()

    xml.write()
    result = file_name.read_text()
    assert result == dst1
    _test_tree_integrity(xml)




def test_comment_stress():
    src = textwrap.dedent(
        """\
        <root>
        \t<!-- <tag0>zfgrhbsddrfb</tag0> -->
        \t<!-- <tag1></tag1> -->
        \t<!-- <tag2/> -->
        \t<!-- <tag3/> -->
        \t<!-- <tag4/> -->
        </root>
        """
    )
    all_tags_are_commented = textwrap.dedent(
        """\
        <root>
        \t<!-- <tag0>zfgrhbsddrfb</tag0> -->
        \t<!-- <tag1></tag1> -->
        \t<!-- <tag2/> -->
        \t<!-- <tag3/> -->
        \t<!-- <tag4/> -->
        </root>
        """
    )
    no_tags_is_commented = textwrap.dedent(
        """\
        <root>
        \t<tag0>zfgrhbsddrfb</tag0>
        \t<tag1></tag1>
        \t<tag2/>
        \t<tag3/>
        \t<tag4/>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tags = [xml.find("tag0"), xml.find("tag1"), xml.find("tag2"), xml.find("tag3"), xml.find("tag4")]

    for index in range(100):
        index = random.randint(0, 4)
        tag = tags[index]
        if isinstance(tag, Element):
            tag.comment_out()
        else:
            tag.uncomment()

    for tag in tags:
        tag.comment_out()

    xml.write()
    result = file_name.read_text()
    assert result == all_tags_are_commented

    for tag in tags:
        tag.uncomment()

    xml.write()
    result = file_name.read_text()
    assert result == no_tags_is_commented
    _test_tree_integrity(xml)



def test_complex_comment_2():
    src = textwrap.dedent(
        """\
        <root>
        \t<!-- <A/> -->
        \t<!--
        \t\t<tag0/>
        \t\t<tag1>
        \t\t\t<tag2/>
        \t\t\t<tag3>
        \t\t\t\t<tag4>
        \t\t\t\t\t<tag5/>
        \t\t\t\t</tag4>
        \t\t\t</tag3>
        \t\t</tag1>
        \t-->
        </root>
        """
    )
    dst1 = textwrap.dedent(
        """\
        <root>
        \t<!-- <A/> -->
        \t<!-- <tag0/> -->
        \t<!--
        \t\t<tag1>
        \t\t\t<tag2/>
        \t\t\t<tag3>
        \t\t\t\t<tag4>
        \t\t\t\t\t<tag5/>
        \t\t\t\t</tag4>
        \t\t\t</tag3>
        \t\t</tag1>
        \t-->
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag0 = xml.find("tag0")
    tag1 = xml.find("tag1")
    tag3 = xml.find("tag3")

    tag0.comment_out() # Ok, as it is out of any comment


    with pytest.raises(IllegalOperation) as badXMLFormat:
        tag3.comment_out()
    assert str(badXMLFormat.value) == "Cannot comment out an element whose parent is a comment"
    assert badXMLFormat.type is IllegalOperation

    tag1.uncomment()
    tag3.comment_out()

    with pytest.raises(IllegalOperation) as badXMLFormat:
        tag1.comment_out()
    assert str(badXMLFormat.value) == "Cannot comment out an element whose descended is a comment"
    assert badXMLFormat.type is IllegalOperation

    tag3.uncomment()
    tag1.comment_out()

    xml.write()
    result = file_name.read_text()
    assert result == dst1
    _test_tree_integrity(xml)



def test_file_test_1():
    file_name = Path("./files/test_1.xml")
    xml = SmartXML(file_name)
    _test_tree_integrity(xml)
    tag = xml.find("lib:title")
    assert tag
    assert tag.content == "The Algorithm's Muse"



def test_file_test_2():
    file_name = Path("./files/test_2.xml")
    xml = SmartXML(file_name)
    _test_tree_integrity(xml)
    xml.write(Path(test_file_name))
    pass



def test_find_duplication():
    file_name = __create_file('<settings><A id="1"><A id="2"><A id="3"/></A></A></settings>')
    xml = SmartXML(file_name)

    all_a = xml.find("A", False)
    assert len(all_a) == 3

    aa = xml.find("A|A", False)
    assert len(aa) == 2

    aa = xml.find("A|A|A", False)
    assert len(aa) == 1

    a = xml.find("A")
    assert a.attributes["id"] == "1"



def test_attributes():
    src = textwrap.dedent(
        """\
        <settings>
        <user id="42" role="admin" xxxxxxxxxxxxxxxxxxxxxxxxx="yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"/>
        </settings>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    user = xml.find("user")
    assert user.attributes["id"] == "42"
    assert user.attributes["role"] == "admin"
    assert user.attributes["xxxxxxxxxxxxxxxxxxxxxxxxx"] == "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
    _test_tree_integrity(xml)



def test_find_name():
    src = textwrap.dedent(
        """\
        <start>
            <A id="1">
                <A id="2">
                    <A id="3"/>
                    <B/>
                    <A id="4"/>
                    <A id="5"/>
                    <A id="6">
                        <A id="7"/>
                        <B></B>
                    </A>
                </A>
            </A>
        </start>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    ab = xml.find("A|B", False)
    assert len(ab) == 2
    #
    aa = xml.find("A|A", False)
    assert len(aa) == 6

    aaa = xml.find("A|A|A", False)
    assert len(aaa) == 5

    aaaa = xml.find("A|B|C", False)
    assert len(aaaa) == 0

    aaaa = xml.find("A|A|A|A", False)
    assert len(aaaa) == 1

    aaaaa = xml.find("A|A|A|A|A", False)
    assert len(aaaaa) == 0

    # TOTO - complete



def test_find_name_2():
    src = textwrap.dedent(
        """\
        <start>
            <A id="A1">
                <B id="B1">
                    <C id="C1">
                        <D id="D1">
                            <E id="E1"/>
                        </D>
                        <A>
                            <B id="B2"></B>
                        </A>
                    </C>
                </B>
            </A>
        </start>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    abcd = xml.find("A|B|C|D", False)
    assert len(abcd) == 1
    assert abcd[0].attributes["id"] == "D1"
    assert xml.find("A|B|C|D").attributes["id"] == "D1"

    abcde = xml.find("A|B|C|D|E", False)
    assert len(abcde) == 1
    assert abcde[0].attributes["id"] == "E1"
    assert xml.find("A|B|C|D|E").attributes["id"] == "E1"

    abcb = xml.find("A|B|C|B", False)
    assert len(abcb) == 0

    abcb = xml.find("A|B|C|B", False)
    assert len(abcb) == 0

    abcdb = xml.find("A|B|C|D|B", False)
    assert len(abcdb) == 0



def test_find_1():
    src = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <start>
            <!DOCTYPE note [
                <!ELEMENT note (to, from, body)>
                <!ATTLIST to (#PCDATA)>
                <!ENTITY from (#PCDATA)>
                <!NOTATION body (#PCDATA)>
            ]>
            <A id="A1">
                <B id="B1">
                    <C id="C1">
                        <D id="D1">
                            <E id="E1"/>
                        </D>
                        <A>
                            <!-- fsdfsd -->
                            <B id="B2">BBB</B>
                        </A>
                    </C>
                </B>
            </A>
        </start>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    ab = xml.find("B")
    assert ab

    b = xml.find("B", only_one=False, with_content="ABC")
    assert len(b) == 0

    b = xml.find("B", only_one=False, with_content="ABC")
    assert len(b) == 0

    b = xml.find("B", only_one=False, with_content="BBB")
    assert len(b) == 1
    assert b[0].attributes["id"] == "B2"

    b = xml.find("B", with_content="BBB")
    assert b
    assert b.attributes["id"] == "B2"

    c = xml.find("C")
    assert c
    b = c.find("B")
    assert b
    assert b.attributes["id"] == "B2"

    b = c.find("A|B")
    assert b
    assert b.attributes["id"] == "B2"



def test_bad_find():
    src = textwrap.dedent(
        """\
        <head version="1.0">This is the head
        \t<tag1></tag1>
        </head>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    with pytest.raises(ValueError) as valueError:
        xml.find()
    assert str(valueError.value) == "At least one search criteria must be provided"
    assert valueError.type is ValueError



def test_bad_format_1():
    src = textwrap.dedent(
        """\
        <start><B>
        </start>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Mismatched XML tags, opening: B, closing: start, in line 2"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_2():
    src = textwrap.dedent(
        """\
        <start></start>
        <start></start>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "xml contains more than one outer element"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_3():
    src = textwrap.dedent(
        """\
        <user>
            <name>Alex</name>
            <email>alex@example.com
        </user>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Mismatched XML tags, opening: email, closing: user, in line 4"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_4():
    src = textwrap.dedent(
        """
        <b><i>This is bold and italic</b></i>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Mismatched XML tags, opening: i, closing: b, in line 2"
    assert badXMLFormat.type is BadXMLFormat



@pytest.mark.one
def test_bad_format_5():
    src = textwrap.dedent(
        """
        <1st_place>John</1st_place>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
        pass
    assert str(badXMLFormat.value) == 'Element name must start with a letter in element definition: "1st_place"'
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_6():
    src = textwrap.dedent(
        """\
         <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <head version="1.0">This is the head
        \t<tag1></tag1>
        \t<!-- <tag2></tag2> -->
        \t<tag3/>
        </head>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "XML declaration must be at the beginning of the file"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_7():
    src = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="UTF-8" standalone="yes">
        <head version="1.0">This is the head
        \t<tag1></tag1>
        \t<!-- <tag2></tag2> -->
        \t<tag3/>
        </head>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Malformed XML declaration"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_8():
    src = textwrap.dedent(
        """\
        <head version="1.0">This is the head
        \t<tag1></tag2>
        </head>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Mismatched XML tags, opening: tag1, closing: tag2, in line 2"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_9():
    src = textwrap.dedent(
        """\
        <head version="1.0">This is the head
        \t<!--tag1></tag1>
        </head>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Malformed comment in line 2"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_10():
    src = textwrap.dedent(
        """\
        <head version="1.0">This is the head
        \t<!--<tag1></tag1>>
        </head>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Malformed comment in line 2"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_11():
    src = textwrap.dedent(
        """\
        <head version="1.0">This is the head
        \t<!-- T!--AG /TAG -->
        </head>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Nested comments are not allowed in line 2"
    assert badXMLFormat.type is BadXMLFormat



def test_bad_format_12():
    src = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <head version="1.0">This is the head
        \t<tag1></tag1>
        \t<<tag2></tag2> -->
        \t<tag3/>
        </head>
        """
    )

    file_name = __create_file(src)

    with pytest.raises(BadXMLFormat) as badXMLFormat:
        SmartXML(file_name)
    assert str(badXMLFormat.value) == "Malformed element in line 4"
    assert badXMLFormat.type is BadXMLFormat


TEST_FOLDER = Path(__file__).resolve().parent


def test_read_me_example():
    # README example test
    input_file = TEST_FOLDER / Path('files/students.xml')

    xml = SmartXML(input_file)
    firstName = xml.find('students|student|firstName', with_content='Bob')
    bob = firstName.parent
    bob.comment_out()
    header = TextOnlyComment(' Bob is out ')
    header.add_before(bob)

    output_file = Path(test_file_name)
    xml.write(output_file)
    result = output_file.read_text()

    dst = textwrap.dedent(
        """\
<?xml version="1.0" encoding="UTF-8"?>
<students>
\t<student id="S001">
\t\t<firstName>Alice</firstName>
\t\t<lastName>Cohen</lastName>
\t\t<age>20</age>
\t\t<grade>90</grade>
\t\t<email>alice.cohen@example.com</email>
\t</student>
\t<!-- Bob is out -->
\t<!--
\t\t<student id="S002">
\t\t\t<firstName>Bob</firstName>
\t\t\t<lastName>Levi</lastName>
\t\t\t<age>22</age>
\t\t\t<grade>85</grade>
\t\t\t<email>bob.levi@example.com</email>
\t\t</student>
\t-->
\t<student id="S003">
\t\t<firstName>Noa</firstName>
\t\t<lastName>Shalev</lastName>
\t\t<age>19</age>
\t\t<grade>95</grade>
\t\t<email>noa.shalev@example.com</email>
\t</student>
</students>
"""
    )

    assert result == dst



def test_find_with_content():
    src = textwrap.dedent(
        """\
        <head version="1.0">This is the head
            <tag1></tag1>
            <!-- <tag2 id="1">content 1</tag2> -->
            <!-- <tag2 id="2">content 2</tag2> -->
            <tag2 id="3">content 3
                <tag2 id="4">content 4
                </tag2>
            </tag2>
            <tag3/>
        </head>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    head = xml.find("head", with_content="This is the head")
    assert head
    tag2_1 = xml.find("tag2", with_content="content 1")
    assert tag2_1
    assert tag2_1.attributes["id"] == "1"
    tag2_2 = xml.find("tag2", with_content="content 2")
    assert tag2_2
    assert tag2_2.attributes["id"] == "2"
    tag2_3 = xml.find("tag2", with_content="content 3")
    assert tag2_3
    assert tag2_3.attributes["id"] == "3"
    tag2_4 = xml.find("tag2", with_content="content 4")
    assert tag2_4
    assert tag2_4.attributes["id"] == "4"


def test_find_all_with_content():
    src = textwrap.dedent(
        """\
        <head version="1.0">This is the head
            <tag1></tag1>
            <!-- <tag2 id="1">content</tag2> -->
            <!-- <tag2 id="2">content</tag2> -->
            <tag2 id="3">content
                <tag2 id="4">content
                </tag2>
            </tag2>
            <tag3/>
            <tag4>xxx</tag4>
        </head>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tags = xml.find("tag2", with_content="content", only_one=False)
    assert len(tags) == 4
    for index in range(4):
        assert tags[index].attributes["id"] == str(index + 1)

    tag4 = xml.find(with_content="xxx")
    assert tag4
    assert tag4.name == "tag4"

    tag4 = xml.find(with_content="xxx", only_one=False)
    assert len(tag4) == 1
    assert tag4[0].name == "tag4"




def test_read_me_example_ver1():
    input_file = TEST_FOLDER / Path('./files/students.xml')

    xml = SmartXML(input_file)
    names = xml.find('students|student|firstName', only_one=False)
    for name in names:
        if name.content == 'Bob':
            bob = name.parent
            bob.comment_out()
            header = TextOnlyComment(' Bob is out ')
            header.add_before(bob)

    output_file = Path(test_file_name)
    xml.write(output_file)
    result = output_file.read_text()

    dst = textwrap.dedent(
        """\
<?xml version="1.0" encoding="UTF-8"?>
<students>
\t<student id="S001">
\t\t<firstName>Alice</firstName>
\t\t<lastName>Cohen</lastName>
\t\t<age>20</age>
\t\t<grade>90</grade>
\t\t<email>alice.cohen@example.com</email>
\t</student>
\t<!-- Bob is out -->
\t<!--
\t\t<student id="S002">
\t\t\t<firstName>Bob</firstName>
\t\t\t<lastName>Levi</lastName>
\t\t\t<age>22</age>
\t\t\t<grade>85</grade>
\t\t\t<email>bob.levi@example.com</email>
\t\t</student>
\t-->
\t<student id="S003">
\t\t<firstName>Noa</firstName>
\t\t<lastName>Shalev</lastName>
\t\t<age>19</age>
\t\t<grade>95</grade>
\t\t<email>noa.shalev@example.com</email>
\t</student>
</students>
"""
    )

    assert result == dst


def test_build_tree():
    dst = textwrap.dedent(
        """\
        <head version="1.0">This is the head
        \t<tag1></tag1>
        \t<!-- tag4 comment -->
        \t<!-- <tag2></tag2> -->
        \t<tag5></tag5>
        \t<tag3/>
        </head>
        """
    )

    xml = SmartXML()
    head = Element("head")
    head.content = "This is the head"
    head.attributes["version"] = "1.0"

    xml._tree = head

    tag1 = Element("tag1")
    tag2 = Element("tag2")
    tag3 = Element("tag3")
    tag4 = TextOnlyComment(" tag4 comment ")
    tag5 = Element("tag5")
    head.set_as_parent_of(tag1)
    tag2.add_as_son_of(head)
    tag3.add_as_son_of(head)
    tag4.add_before(tag2)
    tag5.add_after(tag2)
    tag2.comment_out()
    tag3._is_empty = True

    _test_tree_integrity(xml)

    file_name = Path(test_file_name)
    xml.write(file_name)
    result = file_name.read_text()
    assert result == dst



def test_declaration():
    src = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <head version="1.0">This is the head
        \t<tag1></tag1>
        \t<!-- <tag2></tag2> -->
        \t<tag3/>
        </head>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()
    result = file_name.read_text()

    assert xml.declaration == 'version="1.0" encoding="UTF-8" standalone="yes"'
    assert src == result



def test_remove():
    src = textwrap.dedent(
        """\
        <root>
            <!--
                <tag1>000</tag1>
            -->
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc> 
            </aaaaa>
        </root>
        """
    )
    dst1 = textwrap.dedent(
        """\
        <root>
        \t<!-- <tag1>000</tag1> -->
        \t<aaaaa></aaaaa>
        </root>
        """
    )
    dst2 = textwrap.dedent(
        """\
        <root>
        \t<aaaaa></aaaaa>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    bbbb = xml.find("bbbbb")
    cccc = xml.find("ccccc")

    bbbb.remove()
    cccc.remove()

    xml.write()
    result = file_name.read_text()
    assert result == dst1
    _test_tree_integrity(xml)

    tag1 = xml.find("tag1")
    tag1.remove()

    xml.write()
    result = file_name.read_text()
    assert result == dst2
    _test_tree_integrity(xml)



def test_remove2():
    src = textwrap.dedent(
        """\
        <root>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc> 
            </aaaaa>
        </root>
        """
    )
    dst = textwrap.dedent(
        """\
        <root></root>
        """
    )
    file_name = __create_file(src)
    xml = SmartXML(file_name)

    aaaa = xml.find("aaaaa")

    aaaa.remove()

    xml.write()
    result = file_name.read_text()
    assert result == dst
    _test_tree_integrity(xml)



def test_tag_manipulations():
    src = textwrap.dedent(
        """\
        <root>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc> 
            </aaaaa>
        </root>
        """
    )
    dst = textwrap.dedent(
        """\
        <root>
        \t<a id1="42" id2="aaa">content
        \t\t<!-- <bbbbb/> -->
        \t\t<ccccc/>
        \t</a>
        </root>
        """
    )
    file_name = __create_file(src)
    xml = SmartXML(file_name)

    aaaa = xml.find("aaaaa")
    bbbb = xml.find("bbbbb")
    cccc = xml.find("ccccc")
    aaaa.name = "a"
    aaaa.content = "content"
    aaaa.attributes["id1"] = "42"
    aaaa.attributes["id2"] = "aaa"

    cccc._is_empty = True
    bbbb.comment_out()

    with pytest.raises(ValueError) as valueError:
        cccc.name = "2badname"
    assert str(valueError.value) == "Invalid tag name '2badname'"
    assert valueError.type is ValueError

    with pytest.raises(ValueError) as valueError:
        cccc.name = ""
    assert str(valueError.value) == "Invalid tag name ''"
    assert valueError.type is ValueError

    xml.write()
    result = file_name.read_text()
    assert result == dst
    _test_tree_integrity(xml)



def test_indentation():
    src = textwrap.dedent(
        """\
        <root>
            <A>
                <B><C/></B>
                <A>
                    <B><B/></B>
                </A>
            </A>
        </root>
        """
    )
    dst1 = textwrap.dedent(
        """\
        <root>
         <A>
          <B>
           <C/>
          </B>
          <A>
           <B>
            <B/>
           </B>
          </A>
         </A>
        </root>
        """
    )
    dst2 = textwrap.dedent(
        """\
        <root>
        -<A>
        --<B>
        ---<C/>
        --</B>
        --<A>
        ---<B>
        ----<B/>
        ---</B>
        --</A>
        -</A>
        </root>
        """
    )
    dst3 = textwrap.dedent(
        """\
        <root>
        <A>
        <B>
        <C/>
        </B>
        <A>
        <B>
        <B/>
        </B>
        </A>
        </A>
        </root>
        """
    )
    dst4 = textwrap.dedent(
        """\
        <root>
        #$<A>
        #$#$<B>
        #$#$#$<C/>
        #$#$</B>
        #$#$<A>
        #$#$#$<B>
        #$#$#$#$<B/>
        #$#$#$</B>
        #$#$</A>
        #$</A>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write(indentation=" ")
    result = file_name.read_text()
    assert result == dst1

    xml.write(indentation="-")
    result = file_name.read_text()
    assert result == dst2

    xml.write(indentation="")
    result = file_name.read_text()
    assert result == dst3

    xml.write(indentation="#$")
    result = file_name.read_text()
    assert result == dst4



def test_c_data():
    src = textwrap.dedent(
        """\
        <root>
        \t<AAA/>
        \t<![CDATA[A story about <coding> & "logic". The <tags> inside here are ignored by the parser.]]>
        \t<AAA/>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()
    result = file_name.read_text()
    assert result == src



def test_c_data_2():
    src = textwrap.dedent(
        """\
        <?xml version="1.0"?>
        <!DOCTYPE note [
        \t<!ELEMENT note (to, from, body)>
        \t<!ATTLIST to (#PCDATA)>
        \t<!ENTITY from (#PCDATA)>
        \t<!NOTATION body (#PCDATA)>
        ]>
        <root>
        \t<![CDATA[A story about <coding> & "logic". The <tags> inside here are ignored by the parser.]]>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()
    result = file_name.read_text()
    assert result == src



def test_c_data_3():
    src = textwrap.dedent(
        """\
        <!DOCTYPE note [
        \t<!-- Parameter entity (DTD-only macro) -->
        \t<!ENTITY % personContent "(name, email)">
        \t<!-- General entity -->
        \t<!ENTITY author "Dudu Arbel">
        \t<!-- Notation (non-XML data type) -->
        \t<!NOTATION jpeg SYSTEM "image/jpeg">
        \t<!-- Element declarations -->
        \t<!ELEMENT note (from, to, body, attachment?)>
        \t<!ELEMENT from %personContent;>
        \t<!ELEMENT to %personContent;>
        \t<!ELEMENT name (#PCDATA)>
        \t<!ELEMENT email (#PCDATA)>
        \t<!ELEMENT body (#PCDATA)>
        \t<!ELEMENT attachment EMPTY>
        \t<!-- Attribute declarations -->
        \t<!ATTLIST note
        \t\tdate CDATA #REQUIRED>
        \t<!ATTLIST attachment
        \t\tsrc   CDATA   #REQUIRED
        \t\ttype  NOTATION (jpeg) #REQUIRED>
        ]>
        <root></root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    xml.write()
    result = file_name.read_text()
    assert result == src



def test_to_string():
    src = textwrap.dedent(
        """\
        <root>
            <tag1>
                <bbbbb/>
                <ccccc></ccccc> 
            </tag1>
        </root>
        """
    )

    dst1 = textwrap.dedent(
        """\
        <tag1>
        \t<bbbbb/>
        \t<ccccc></ccccc>
        </tag1>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    tag1 = xml.find("tag1")

    tag1_str = tag1.to_string()
    assert tag1_str == dst1


def test_read():

    xml = SmartXML()

    with pytest.raises(ValueError) as error:
        xml.write()
    assert str(error.value) == "File name is not specified"
    assert error.type is ValueError

    with pytest.raises(TypeError) as error:
        xml.read('ssss')
    assert str(error.value) == "file_name must be a pathlib.Path object"
    assert error.type is TypeError

    with pytest.raises(FileNotFoundError) as error:
        xml.read(Path('ssss'))
    assert str(error.value) == "File ssss does not exist"
    assert error.type is FileNotFoundError



    src = textwrap.dedent(
        """\
        <root>
        \t<AAA/>
        \t<![CDATA[A story about <coding> & "logic". The <tags> inside here are ignored by the parser.]]>
        \t<AAA/>
        </root>
        """
    )

    file_name = __create_file(src)
    xml.read(file_name)
    xml.write()
    result = file_name.read_text()
    assert result == src

def test_test_comment_more_than_one_line():
    src = textwrap.dedent(
        """\
        <root>
        \t<!--
        \tA story about coding logic.
        \tA story about coding logic.
        \t-->
        </root>
        """
    )
    file_name = __create_file(src)
    xml = SmartXML(file_name)

    xml.write()
    result = file_name.read_text()
    assert result == src

def test_test_comment_with_small_sign():
    src = textwrap.dedent(
        """\
        <root>
        \t<!--
        \tA story about <coding> & "logic".
        \tA story about <coding> & "logic".
        \t-->
        </root>
        """
    )
    file_name = __create_file(src)
    xml = SmartXML(file_name)

    xml.write()
    result = file_name.read_text()
    assert result == src

def test_test_comment_with_bad_elements():
    src = textwrap.dedent(
        """\
        <root>
        \t<!--
        \t<tag1> A story about</tag1>
        \t<tag2> Node: tag2 is not closed!!!! </tag2
        \t-->
        </root>
        """
    )
    file_name = __create_file(src)
    xml = SmartXML(file_name)

    xml.write()
    result = file_name.read_text()
    assert result == src

    with pytest.raises(AttributeError) as error:
        xml.tree._sons[0].uncomment()
    assert error.type is AttributeError



def test_readme():
    test_readme_example()

def test_read_elements():
    elements = _read_elements('<A><B></B><C/></A>')
    assert len(elements) == 1
    assert elements[0].name == 'A'
    assert len(elements[0]._sons) == 2
    assert elements[0]._sons[0].name == 'B'
    assert elements[0]._sons[1].name == 'C'

def test_read_elements_2():
    elements = _read_elements('<A/><B/><C>Data</C>')
    assert len(elements) == 3
    assert elements[0].name == 'A'
    assert elements[1].name == 'B'
    assert elements[2].name == 'C'
    assert elements[2].content == 'Data'

def test_read_elements_minimum_comment():
    elements = _read_elements('<!---->')
    assert len(elements) == 1
    assert isinstance(elements[0], TextOnlyComment)
    assert elements[0]._text == ''


def test_parse_element():
    element = _parse_element('name id="43" role="admin"')
    assert element.name == 'name'
    assert element.attributes['id'] == '43'
    assert element.attributes['role'] == 'admin'

    element = _parse_element('   name   id   =   " 4 3 "    role = " admin" ')
    assert element.name == 'name'
    assert element.attributes['id'] == ' 4 3 '
    assert element.attributes['role'] == ' admin'

    element = _parse_element(' name ')
    assert element.name == 'name'
    assert element.attributes == {}

    element = _parse_element('abc id=""')
    assert element.name == 'abc'
    assert element.attributes['id'] == ''

    with pytest.raises(Exception):
        _parse_element('name  id="43" role="admin')

    with pytest.raises(Exception):
        _parse_element('  id="43" role="admin"')

    with pytest.raises(Exception):
        _parse_element('aaa  id="43" 12role="admin"')

    with pytest.raises(Exception):
        _parse_element('1aaa  id="43" role="admin"')

    with pytest.raises(Exception):
        _parse_element('1aaa  id')

    with pytest.raises(Exception):
        _parse_element('1aaa  id kjjkj =')


def test_find_2():
    src = textwrap.dedent(
        """\
        <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <start>
            <!DOCTYPE note [
                <!ELEMENT note (to, from, body)>
                <!ATTLIST to (#PCDATA)>
                <!ENTITY from (#PCDATA)>
                <!NOTATION body (#PCDATA)>
            ]>
            <!-- AAA-->
            <!-- <A/ -->
            <!-- <B> -->
        </start>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    xx = xml.find(with_content="234543" )
    assert xx is None

    b = xml.find("B")
    assert b is None
