import textwrap

from smartXML.xmltree import SmartXML
from smartXML.element import Element, ElementBase, TextOnlyComment, ContentOnly

import pytest

from tests.test import __create_file, _test_tree_integrity


def _test_add_before(src: str, dst: str, addition: ElementBase, indentation: str = "    "):
    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    addition.add_before(tag1)
    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation=indentation)
    result = file_name.read_text()
    assert result == dst


def _test_add_after(src: str, dst: str, addition: ElementBase, indentation: str = "    "):
    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    addition.add_after(tag1)
    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation=indentation)
    result = file_name.read_text()
    assert result == dst


def test_stam():
    src = textwrap.dedent("""\
        <A><tag1>B</tag1>
            <C></C>
        </A>
        """)

    # add new and delete it
    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    new_tag = Element("new_tag")
    new_tag.add_after(tag1)
    new_tag.remove()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == src


def test_add_before_0():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1></tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <add_one></add_one>
          <tag1></tag1>
        </root>
        """)

    _test_add_before(src, dst, Element("add_one"))


def test_add_before_01():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1></tag1>
          <tag2></tag2>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <add_one></add_one>
          <tag1></tag1>
          <tag2></tag2>
        </root>
        """)

    _test_add_before(src, dst, Element("add_one"))


def test_add_before_1():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1>content1
            <first>000</first>  
              <second/>
            </tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <add_one></add_one>
          <tag1>content1
            <first>000</first>  
              <second/>
            </tag1>
        </root>
        """)

    _test_add_before(src, dst, Element("add_one"))


def test_add_before_2():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1>000
            <first>000</first>  
              <second/>
            </tag1>
            <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <add_one></add_one>
          <tag1>000
            <first>000</first>  
              <second/>
            </tag1>
            <tag2/>
        </root>
        """)

    _test_add_before(src, dst, Element("add_one"))


def test_add_before_3():
    src = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
                      <add_one></add_one><tag1>000</tag1>
        </root>
        """)

    _test_add_before(src, dst, Element("add_one"))


def test_add_before_4():
    src = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
            <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
                      <add_one></add_one><tag1>000</tag1>
            <tag2/>
        </root>
        """)

    _test_add_before(src, dst, Element("add_one"))


def test_add_before_5():
    src = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
            <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
                      <add_one attr="value">content
                          <one_son></one_son>
                      </add_one><tag1>000</tag1>
            <tag2/>
        </root>
        """)

    one = Element("add_one")
    content = ContentOnly("content")
    content.add_as_last_son_of(one)

    one.attributes["attr"] = "value"
    one1 = Element("one_son")
    one1.add_as_last_son_of(one)

    _test_add_before(src, dst, one)


def test_add_before_5a():
    src = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1><tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
                      <add_one attr="value">content
                          <one_son></one_son>
                      </add_one><tag1>000</tag1><tag2/>
        </root>
        """)

    one = Element("add_one")
    content = ContentOnly("content")
    content.add_as_last_son_of(one)
    one.attributes["attr"] = "value"
    one1 = Element("one_son")
    one1.add_as_last_son_of(one)

    _test_add_before(src, dst, one)


def test_add_before_6():
    src = textwrap.dedent("""\
        <root x="1">aa
            <tag1>000</tag1>
            <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
            <add_one attr="value">content
                <one_son></one_son>
            </add_one>
            <tag1>000</tag1>
            <tag2/>
        </root>
        """)

    one = Element("add_one")
    content = ContentOnly("content")
    content.add_as_last_son_of(one)
    one.attributes["attr"] = "value"
    one1 = Element("one_son")
    one1.add_as_last_son_of(one)

    _test_add_before(src, dst, one)


def test_add_after_1():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1>content1
            <first>000</first>  
              <second/>
            </tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <tag1>content1
            <first>000</first>  
              <second/>
            </tag1>
          <add_one></add_one>
        </root>
        """)

    _test_add_after(src, dst, Element("add_one"))


def test_add_after_2():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1>000
            <first>000</first>  
              <second/>
            </tag1>
            <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <tag1>000
            <first>000</first>  
              <second/>
            </tag1>
          <add_one></add_one>
            <tag2/>
        </root>
        """)

    _test_add_after(src, dst, Element("add_one"))


def test_add_after_3():
    src = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
                      <add_one></add_one>
        </root>
        """)

    _test_add_after(src, dst, Element("add_one"))


def test_add_after_4():
    src = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
            <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
                      <add_one></add_one>
            <tag2/>
        </root>
        """)

    _test_add_after(src, dst, Element("add_one"))


def test_add_after_5():
    src = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
            <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa<tag1>000</tag1>
                      <add_one attr="value">content
                          <one_son></one_son>
                      </add_one>
            <tag2/>
        </root>
        """)

    one = Element("add_one")
    content = ContentOnly("content")
    content.add_as_last_son_of(one)
    one.attributes["attr"] = "value"
    one1 = Element("one_son")
    one1.add_as_last_son_of(one)

    _test_add_after(src, dst, one)


def test_add_after_6():
    src = textwrap.dedent("""\
        <root x="1">aa
            <tag1>000</tag1>
            <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
            <tag1>000</tag1>
            <add_one attr="value">content
                <one_son></one_son>
            </add_one>
            <tag2/>
        </root>
        """)

    one = Element("add_one")
    content = ContentOnly("content")
    content.add_as_last_son_of(one)
    one.attributes["attr"] = "value"
    one1 = Element("one_son")
    one1.add_as_last_son_of(one)

    _test_add_after(src, dst, one)


@pytest.mark.skip(reason="multi write is not supported yet")
def test_preserve_formatting_1():
    src = textwrap.dedent("""\
        <students>
        <student id="S001">
        <firstName>Alice</firstName>
        \t\t<lastName>Cohen</lastName>
        \t\t\t<age>20<old/></age>
        \t\t\t\t<grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    dst = textwrap.dedent("""\
        <students>
        <student id="S001">
        <firstName>Alice</firstName>
        \t\t<lastName>Cohen</lastName>
        \t\t\t<age>300
        \t\t\t\t<old/>
        \t\t\t</age>
        \t\t\t\t<grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == src

    age = xml.find("age")

    content = ContentOnly("300")
    content.add_as_last_son_of(age)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_2():
    src = textwrap.dedent("""\
    <students>
    <student id="S001">
    <firstName>Alice</firstName>
    \t\t<lastName>Cohen</lastName>
    \t\t\t<age>20<old/></age>
    \t\t\t\t<grade>90</grade>
    \t\t\t\t\t<email>alice.cohen@example.com</email>
    \t\t\t\t\t\t</student></students>
        """)

    dst = textwrap.dedent("""\
    <students>
    <student id="S001">
    <firstName>Alice</firstName>
    \t\t<lastName>Cohen</lastName>
    \t\t\t<!--
    \t\t\t\t<age>20
    \t\t\t\t\t<old/>
    \t\t\t\t</age>
    \t\t\t-->
    \t\t\t\t<grade>90</grade>
    \t\t\t\t\t<email>alice.cohen@example.com</email>
    \t\t\t\t\t\t</student></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    age.comment_out()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_3():
    src = textwrap.dedent("""\
        <students>
        <student id="S001">
        <firstName>Alice</firstName>
        \t\t<lastName>Cohen</lastName>
        \t\t\t<age>20<old/>
        </age>
        \t\t\t\t<grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    dst = textwrap.dedent("""\
        <students>
        <student id="S001">
        <firstName>Alice</firstName>
        \t\t<lastName>Cohen</lastName>
        \t\t<!-- tag4 comment -->
        \t\t\t<age>20<old/>
        </age>
        \t\t\t\t<grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    tag4 = TextOnlyComment(" tag4 comment ")
    tag4.add_before(age)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_4():
    src = textwrap.dedent("""\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><age>20</age><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    dst = textwrap.dedent("""\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><new_age>45</new_age><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    age.name = "new_age"
    age._sons[0].text = "45"

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_5():
    src = textwrap.dedent("""\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><Bob><age id="avd"/></Bob><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    dst = textwrap.dedent("""\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><Bob><new_age id="avd"/></Bob><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    age.name = "new_age"

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_6():
    src = textwrap.dedent("""\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><Bob><age id="avd"/></Bob><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    dst = textwrap.dedent("""\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><Bob>
                                                                            <!-- age comment --><new_age id="avd"/></Bob><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    age.name = "new_age"

    tag4 = TextOnlyComment(" age comment ")
    tag4.add_before(age)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_text_only():
    src = textwrap.dedent("""\
    <students>
        <!-- text1 -->
        <A><!-- text2 --></A>
    </students>
        """)
    dst = textwrap.dedent("""\
    <students>
        <!--new text-->
        <A><!--t2--></A>
    </students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    comment1 = xml.tree._sons[0]
    comment1.text = "new text"
    a = xml.find("A")
    comment2 = a._sons[0]
    comment2.text = "t2"
    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_1():
    src = textwrap.dedent("""\
        <students><A><B/></A>
        </students>
        """)
    dst = textwrap.dedent("""\
        <students><A><B>
        \t\t\t\t<!--BBBBB-->
                     </B></A>
        </students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    b = xml.find("B")
    header = TextOnlyComment("BBBBB")
    header.add_as_last_son_of(b)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_all_kinds_of_oneline_changes():
    file_name = __create_file("<root><tag1>000</tag1><tag2>000</tag2></root>")
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    tag1._sons[0].text = "the weals of the bus go round and round"
    assert (
        xml.to_string(preserve_format=True)
        == "<root><tag1>the weals of the bus go round and round</tag1><tag2>000</tag2></root>"
    )
    tag1._sons[0].text = "A"
    assert xml.to_string(preserve_format=True) == "<root><tag1>A</tag1><tag2>000</tag2></root>"
    tag1.comment_out()
    assert xml.to_string(preserve_format=True) == "<root><!-- <tag1>A</tag1> --><tag2>000</tag2></root>"
    tag1.remove()
    assert xml.to_string(preserve_format=True) == "<root><tag2>000</tag2></root>"


def test_format_sons_changes():
    src = textwrap.dedent("""\
        <students><X>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </X></students>
        """)
    dst = textwrap.dedent("""\
        <students><X>
                <A>1111</A>
                <new_B/>
                <C/   >
                <!-- <D/> -->
        </X></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    a = xml.find("A")
    b = xml.find("B")
    d = xml.find("D")
    content = ContentOnly("1111")
    content.add_as_last_son_of(a)
    b.name = "new_B"
    d.comment_out()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_add_new_tags():
    src = textwrap.dedent("""\
        <students><X>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </X></students>
        """)
    dst = textwrap.dedent("""\
        <students><X>
                <A ></A>
                <B/  >
                <new></new>
                <C/   >
                <D/    >
        </X></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    b = xml.find("B")
    new = Element("new")
    new.add_after(b)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_move_element():
    src = textwrap.dedent("""\
        <students><tag1>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </tag1><tag2/></students>
        """)
    dst = textwrap.dedent("""\
        <students><tag1>
                <A></A>
                <C/   >
                <D/    >
        </tag1><tag2>
        \t\t<B/>
               </tag2></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    b = xml.find("B")
    tag2 = xml.find("tag2")
    b.add_as_last_son_of(tag2)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_move_element_add_after():
    src = textwrap.dedent("""\
        <students><tag1>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </tag1> <tag2/></students>
        """)
    dst = textwrap.dedent("""\
        <students><tag1>
                <A></A>
                <C/   >
                <D/    >
        </tag1> <tag2/>
                <B/></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    b = xml.find("B")
    tag2 = xml.find("tag2")
    b.add_after(tag2)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_move_element_add_before():
    src = textwrap.dedent("""\
        <students><tag1>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </tag1><tag2/></students>
        """)
    dst = textwrap.dedent("""\
        <students><tag1>
                <A></A>
                <C/   >
                <D/    >
        </tag1>
                  <B/><tag2/></students>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    b = xml.find("B")
    tag2 = xml.find("tag2")
    b.add_before(tag2)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


@pytest.mark.skip(reason="multi write is not supported yet")
def test_preserve_formatting_comment():
    src = textwrap.dedent("""\
        <root>
            <!-- first comment -->
            <!--
                <tag1>000</tag1>
            -->
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    dst1 = textwrap.dedent("""\
        <root>
        \t<!--A-->
            <!--
                <tag1>000</tag1>
            -->
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    dst2 = textwrap.dedent("""\
        <root>
        \t<!--Option 1: Use double quotes for the literal (recommended)-->
            <!--
                <tag1>000</tag1>
            -->
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag2 = xml.find("tag2")
    first_comment = tag2.parent._sons[0]
    first_comment.text = "A"

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst1

    first_comment.text = "Option 1: Use double quotes for the literal (recommended)"

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst2


@pytest.mark.skip(reason="multi write is not supported yet")
def test_preserve_formatting_change_comment():
    src = textwrap.dedent("""\
        <root>
            <!-- first comment -->
            <!--
                <tag1>000</tag1>
            -->
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    dst1 = textwrap.dedent("""\
        <root>
            <!-- first comment -->
        \t<!--
        \t\t<tag1>1234556hljfdghbofdj</tag1>
        \t-->
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    dst2 = textwrap.dedent("""\
        <root>
        <!--Option 1: Use double quotes for the literal (recommended)-->
        \t<tag1>1234556hljfdghbofdj</tag1>
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    content = ContentOnly("1234556hljfdghbofdj")
    content.add_as_last_son_of(tag1)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst1

    tag1.uncomment()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst2


def test_preserve_formatting_add_and_delete():
    src = textwrap.dedent("""\
        <root>
            <!-- first comment -->
            <!-- <tag1>000</tag1> -->
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    # add new and delete it
    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    new_tag = Element("new_tag")
    new_tag.add_after(tag1)
    new_tag.remove()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == src


def test_preserve_formatting_add_and_delete_2():
    src = textwrap.dedent("""\
        <root>
            <!-- first comment -->
            <tag1>000</tag1>
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    # add new and delete it
    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    new_tag = Element("new_tag")
    new_tag.add_after(tag1)
    new_tag.remove()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == src


def test_formatting_add_as_last_son_of_complex_tag():
    src = textwrap.dedent("""\
        <root>
            <tag1>000
                  <tag2>000</tag2>
                  <tag3/>
            </tag1>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root>
            <tag1>000
                  <tag2>000</tag2>
                  <tag3/>
                  <father>
        \t\t\t<son1/>
        \t\t\t<son2></son2>
                  </father>
            </tag1>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    father = Element("father")
    son1 = Element("son1")
    son1._is_empty = True
    son1.add_as_last_son_of(father)
    son2 = Element("son2")
    son2.add_after(son1)

    father.add_as_last_son_of(tag1)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst

    # the complex and the simple below does not work. need to calc where to add them


def test_formatting_add_as_last_son_of_1():
    src = textwrap.dedent("""\
        <root>
            <tag1>000
                  <tag2>000</tag2>
                  <tag3/>
            </tag1>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root>
            <tag1>000
                  <tag2>000</tag2>
                  <tag3/>
                  <nX5/>
            </tag1>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc>
            </aaaaa>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    nX5 = Element("nX5")
    nX5._is_empty = True
    nX5.add_as_last_son_of(tag1)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_formatting_move_element_to_same_parent():
    src = textwrap.dedent("""\
        <root>
            <tag1>000
                  <tag2>000</tag2>
                  <tag3/>
            </tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root>
            <tag1>000
                  <tag3/>
                  <tag2>000</tag2>
            </tag1>
        </root>
        """)

    # move element to the same parent!!!

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    tag2 = xml.find("tag2")
    tag2.add_as_last_son_of(tag1)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_all_adds():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1>000
            <first>000</first>
              <second/>
            </tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <add_one></add_one>
          <tag1>000
            <first>000</first>
              <second/>
              <add_two></add_two>
            </tag1>
          <add_three></add_three>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    one = Element("add_one")
    two = Element("add_two")
    three = Element("add_three")

    one.add_before(tag1)
    two.add_as_last_son_of(tag1)
    three.add_after(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_all_adds2():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1>000
            <first>000</first>
              <second/>
            </tag1>
         <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <one></one>
          <tag1>000
            <first>000</first>
              <second/>
              <two></two>
            </tag1>
          <three></three>
         <tag2/>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    one = Element("one")
    two = Element("two")
    three = Element("three")

    one.add_before(tag1)
    two.add_as_last_son_of(tag1)
    three.add_after(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_all_adds_complex():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1>000
            <first>000</first>
              <second/>
            </tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <add_one attr="value">content
            <one_son></one_son>
          </add_one>
          <tag1>000
            <first>000</first>
              <second/>
              <add_two attr="value">content
                <two_son></two_son>
              </add_two>
            </tag1>
          <add_three attr="value">content
            <three_son></three_son>
          </add_three>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    one = Element("add_one")
    content = ContentOnly("content")
    content.add_as_last_son_of(one)
    one.attributes["attr"] = "value"
    one1 = Element("one_son")
    one1.add_as_last_son_of(one)

    two = Element("add_two")
    content = ContentOnly("content")
    content.add_as_last_son_of(two)
    two.attributes["attr"] = "value"
    two1 = Element("two_son")
    two1.add_as_last_son_of(two)

    three = Element("add_three")
    content = ContentOnly("content")
    content.add_as_last_son_of(three)
    three.attributes["attr"] = "value"
    three1 = Element("three_son")
    three1.add_as_last_son_of(three)

    one.add_before(tag1)
    two.add_as_last_son_of(tag1)
    three.add_after(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="  ")
    result = file_name.read_text()
    assert result == dst


def test_all_adds2_complex():
    src = textwrap.dedent("""\
        <root x="1">aa
          <tag1>000
            <first>000</first>
              <second/>
            </tag1>
         <tag2/>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
          <add_one attr="value">content
            <one_son></one_son>
          </add_one>
          <tag1>000
            <first>000</first>
              <second/>
              <add_two attr="value">content
                <two_son></two_son>
              </add_two>
            </tag1>
          <add_three attr="value">content
            <three_son></three_son>
          </add_three>
         <tag2/>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    one = Element("add_one")
    content = ContentOnly("content")
    content.add_as_last_son_of(one)
    one.attributes["attr"] = "value"
    one1 = Element("one_son")
    one1.add_as_last_son_of(one)

    two = Element("add_two")
    content = ContentOnly("content")
    content.add_as_last_son_of(two)
    two.attributes["attr"] = "value"
    two1 = Element("two_son")
    two1.add_as_last_son_of(two)

    three = Element("add_three")
    content = ContentOnly("content")
    content.add_as_last_son_of(three)
    three.attributes["attr"] = "value"
    three1 = Element("three_son")
    three1.add_as_last_son_of(three)

    one.add_before(tag1)
    two.add_as_last_son_of(tag1)
    three.add_after(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="  ")
    result = file_name.read_text()
    assert result == dst


def test_all_adds_to_empty_element_1():
    src = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs"/>three little birds
           beside my doorstep
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
           <add_one></add_one>
           <tag1 dljhsn="sdfjhgs"/>three little birds
           beside my doorstep
        </root>
        """)

    # Add son to an empty element with content and attributes

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    one = Element("add_one")

    one.add_before(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="  ")
    result = file_name.read_text()
    assert result == dst


def test_all_adds_to_empty_element_2():
    src = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs"/>three little birds
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs">
             <add_two></add_two>
           </tag1>three little birds
        </root>
        """)

    # Add son to an empty element with content and attributes

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    two = Element("add_two")

    two.add_as_last_son_of(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="  ")
    result = file_name.read_text()
    assert result == dst


def test_all_adds_to_empty_element_3():
    src = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs"/>three little birds
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs"/>
           <add_three></add_three>three little birds
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    three = Element("add_three")

    three.add_after(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="  ")
    result = file_name.read_text()
    assert result == dst


def test_adds_as_first_son_with_content():
    src = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs">three little birds</tag1>
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs">
               <add_two></add_two>
               three little birds
           </tag1>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    two = Element("add_two")

    two.add_as_first_son_of(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="    ")
    result = file_name.read_text()
    assert result == dst


def test_all_adds_to_empty_element():
    src = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs"/>three little birds
        </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
           <add_one></add_one>
           <tag1 dljhsn="sdfjhgs">
             <add_two></add_two>
           </tag1>
           <add_three></add_three>three little birds
        </root>
        """)

    # Add son to an empty element with content and attributes

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    one = Element("add_one")
    two = Element("add_two")
    three = Element("add_three")

    one.add_before(tag1)
    two.add_as_last_son_of(tag1)
    three.add_after(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="  ")
    result = file_name.read_text()
    assert result == dst


def test_all_adds_several_sons_to_parent_with_no_sons():
    src = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs">three little birds
           </tag1>
                </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs">three little birds
             <add_one></add_one>
             <add_two></add_two>
             <add_three></add_three>
           </tag1>
                </root>
        """)

    # Add several new sons

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    one = Element("add_one")
    two = Element("add_two")
    three = Element("add_three")

    one.add_as_last_son_of(tag1)
    two.add_as_last_son_of(tag1)
    three.add_as_last_son_of(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="  ")
    result = file_name.read_text()
    assert result == dst


@pytest.mark.skip(reason="Multiline content not supported yet")
def test_all_adds_several_sons_to_parent_with_no_sons_same_line():
    src = textwrap.dedent("""\
        <root x="1">aa
           <tag1 dljhsn="sdfjhgs">three little birds</tag1>
                </root>
        """)

    dst = textwrap.dedent("""\
        <root x="1">aa
           <add_one></add_one>
           <tag1 dljhsn="sdfjhgs">three little birds
            <add_one></add_one>
            <add_two></add_two>
            <add_three></add_three>
           </tag1>
           <add_three></add_three>
        </root>
        """)

    # Add several new sons

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")

    one = Element("add_one")
    two = Element("add_two")
    three = Element("add_three")

    three.add_as_last_son_of(tag1)
    two.add_as_last_son_of(tag1)
    one.add_as_last_son_of(tag1)

    _test_tree_integrity(xml)

    xml.write(preserve_format=True, indentation="  ")
    result = file_name.read_text()
    assert result == dst


def test_modify_c_data():
    src = textwrap.dedent("""\
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
        """)

    dst = textwrap.dedent("""\
        <?xml version="1.0"?>
        <!DOCTYPE note [
        \t<!ELEMENT note (to, from, body)>
        \t<!ATTLIST to (#PCDATA)>
        \t<!ENTITY from (#PCDATA)>
        \t<!NOTATION body (#PCDATA)>
        ]>
        <root>
        \t<![CDATA[<<<>>>]]>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    c_data = xml.tree._sons[0]
    c_data.text = "<<<>>>"

    xml.write()
    result = file_name.read_text()
    assert result == dst


@pytest.mark.skip(reason="c data is not well defined. this xml is not valid!!!")
def test_modify_doctype():
    src = textwrap.dedent("""\
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
        """)

    dst = textwrap.dedent("""\
        <?xml version="1.0"?>
        <!DOCTYPE note [
        \t<!ELEMENT note (to, from, body)>
        \t<!not-this>
        \t<!ENTITY from (#PCDATA)>
        \t<!NOTATION body (#PCDATA)>
        ]>
        <root>
        \t<![CDATA[<<<>>>]]>
        </root>
        """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    doctype = xml._doctype
    son1 = doctype._sons[1]
    son1.name = "not-this"

    xml.write()
    result = file_name.read_text()
    assert result == dst


def test_remove_first_after_content():
    src = textwrap.dedent("""\
        <root x="1">aa
         <tag1 dljhsn="sdfjhgs">three little birds
            <add_one></add_one>
            <add_two></add_two>
            <add_three></add_three>
           </tag1>
           <add_three></add_three>
        </root>
        """)
    dst = textwrap.dedent("""\
        <root x="1">aa
         <tag1 dljhsn="sdfjhgs">three little birds
            <add_two></add_two>
            <add_three></add_three>
           </tag1>
           <add_three></add_three>
        </root>
    """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    add_one = xml.find("add_one")
    add_one.remove()
    _test_tree_integrity(xml)

    result = xml.to_string(preserve_format=True, indentation=" ")
    assert result == dst


def test_simple_remove():
    src = textwrap.dedent("""\
        <root x="1">aa
         <tag1 dljhsn="sdfjhgs">
            <add_one></add_one>
            <add_two></add_two>
            <add_three></add_three>
           </tag1>
           <add_three></add_three>
        </root>
        """)
    dst = textwrap.dedent("""\
        <root x="1">aa
         <tag1 dljhsn="sdfjhgs">
            <add_two></add_two>
            <add_three></add_three>
           </tag1>
           <add_three></add_three>
        </root>
    """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    add_one = xml.find("add_one")
    add_one.remove()
    _test_tree_integrity(xml)

    result = xml.to_string(preserve_format=True, indentation=" ")
    assert result == dst


def test_last_remove():
    src = textwrap.dedent("""\
        <root x="1">aa
         <tag1    dljhsn="sdfjhgs">
            <add_one></add_one>
           </tag1>
           <add_three></add_three>
        </root>
        """)
    dst = textwrap.dedent("""\
        <root x="1">aa
         <tag1 dljhsn="sdfjhgs"></tag1>
           <add_three></add_three>
        </root>
    """)

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    add_one = xml.find("add_one")
    add_one.remove()
    _test_tree_integrity(xml)

    result = xml.to_string(preserve_format=True, indentation=" ")
    assert result == dst


# TODO - add several new tags to unformatted file
# TODO - reset _orig_start_index when element is moved
# TODO - test format + special indentataion (3 spaces e.g.)
# TODO - move an element to a new location (check old removed, new added in right place)
# TODO - many changes/writes
# TODO - change a parent and its son
# TODO - change a parent and add new son
# TODO - move element (add_after) to SAME parent
# TODO - _is_empty (and all the rest ) must be properties, as we need to know whether they were changed
# TODO - add to element with content that breaks lines
# TODO - modify doctype and <?...>
# TODO - modify all elements but root
