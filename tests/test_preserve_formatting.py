import textwrap

from smartXML.xmltree import SmartXML
from smartXML.element import Element, TextOnlyComment

import pytest

from tests.test import __create_file


def test_preserve_formatting_1():
    src = textwrap.dedent(
        """\
        <students>
        <student id="S001">
        <firstName>Alice</firstName>
        \t\t<lastName>Cohen</lastName>
        \t\t\t<age>20<old/></age>
        \t\t\t\t<grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

    dst = textwrap.dedent(
        """\
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
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == src

    age = xml.find("age")
    age.content = 300

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_2():
    src = textwrap.dedent(
        """\
    <students>
    <student id="S001">
    <firstName>Alice</firstName>
    \t\t<lastName>Cohen</lastName>
    \t\t\t<age>20<old/></age>
    \t\t\t\t<grade>90</grade>
    \t\t\t\t\t<email>alice.cohen@example.com</email>
    \t\t\t\t\t\t</student></students>
        """
    )

    dst = textwrap.dedent(
        """\
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
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    age.comment_out()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_3():
    src = textwrap.dedent(
        """\
        <students>
        <student id="S001">
        <firstName>Alice</firstName>
        \t\t<lastName>Cohen</lastName>
        \t\t\t<age>20<old/>
        </age>
        \t\t\t\t<grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

    dst = textwrap.dedent(
        """\
        <students>
        <student id="S001">
        <firstName>Alice</firstName>
        \t\t<lastName>Cohen</lastName>
        \t\t\t<!-- tag4 comment -->
        \t\t\t<age>20<old/>
        </age>
        \t\t\t\t<grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    tag4 = TextOnlyComment(" tag4 comment ")
    tag4.add_before(age)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_4():
    src = textwrap.dedent(
        """\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><age>20</age><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

    dst = textwrap.dedent(
        """\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><new_age>45</new_age><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    age.name = "new_age"
    age.content = 45

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_5():
    src = textwrap.dedent(
        """\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><Bob><age id="avd"/></Bob><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

    dst = textwrap.dedent(
        """\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><Bob><new_age id="avd"/></Bob><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    age = xml.find("age")
    age.name = "new_age"

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_6():
    src = textwrap.dedent(
        """\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><Bob><age id="avd"/></Bob><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

    dst = textwrap.dedent(
        """\
        <students>
        <student><firstName>Alice</firstName><lastName>Cohen</lastName><Bob><!-- age comment --><new_age id="avd"/></Bob><grade>90</grade>
        \t\t\t\t\t<email>alice.cohen@example.com</email>
        \t\t\t\t\t\t</student></students>
        """
    )

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
    src = textwrap.dedent(
        """\
    <students>
        <!-- text1 -->
        <A><!-- text2 --></A>
    </students>
        """
    )
    dst = textwrap.dedent(
        """\
    <students>
        <!--new text-->
        <A><!--t2--></A>
    </students>
        """
    )

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
    src = textwrap.dedent(
        """\
    <students><A><B/></A>
    </students>
        """
    )
    dst = textwrap.dedent(
        """\
    <students><A><B>
    \t<!--BBBBB-->
    </B></A>
    </students>
        """
    )

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
    tag1.content = "the weals of the bus go round and round"
    assert (
        xml.to_string(preserve_format=True)
        == "<root><tag1>the weals of the bus go round and round</tag1><tag2>000</tag2></root>"
    )
    tag1.content = "A"
    assert xml.to_string(preserve_format=True) == "<root><tag1>A</tag1><tag2>000</tag2></root>"
    tag1.comment_out()
    assert xml.to_string(preserve_format=True) == "<root><!-- <tag1>A</tag1> --><tag2>000</tag2></root>"
    tag1.remove()
    assert xml.to_string(preserve_format=True) == "<root><tag2>000</tag2></root>"


def test_format_sons_changes():
    src = textwrap.dedent(
        """\
        <students><X>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </X></students>
        """
    )
    dst = textwrap.dedent(
        """\
        <students><X>
                <A>1111</A>
                <new_B/>
                <C/   >
                <!-- <D/> -->
        </X></students>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    a = xml.find("A")
    b = xml.find("B")
    d = xml.find("D")
    a.content = "1111"
    b.name = "new_B"
    d.comment_out()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_add_new_tags():
    src = textwrap.dedent(
        """\
        <students><X>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </X></students>
        """
    )
    dst = textwrap.dedent(
        """\
        <students><X>
                <A ></A>
                <B/  >
                <new></new>
                <C/   >
                <D/    >
        </X></students>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    b = xml.find("B")
    new = Element("new")
    new.add_after(b)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_move_element():
    src = textwrap.dedent(
        """\
        <students><tag1>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </tag1><tag2/></students>
        """
    )
    dst = textwrap.dedent(
        """\
        <students><tag1>
                <A ></A>
                <C/   >
                <D/    >
        </tag1><tag2>
        \t<B/>
        </tag2></students>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    b = xml.find("B")
    tag2 = xml.find("tag2")
    b.add_as_last_son_of(tag2)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_move_element_add_after():
    src = textwrap.dedent(
        """\
        <students><tag1>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </tag1><tag2/></students>
        """
    )
    dst = textwrap.dedent(
        """\
        <students><tag1>
                <A ></A>
                <C/   >
                <D/    >
        </tag1><tag2/><B/></students>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    b = xml.find("B")
    tag2 = xml.find("tag2")
    b.add_after(tag2)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_format_move_element_add_before():
    src = textwrap.dedent(
        """\
        <students><tag1>
                <A ></A>
                <B/  >
                <C/   >
                <D/    >
        </tag1><tag2/></students>
        """
    )
    dst = textwrap.dedent(
        """\
        <students><tag1>
                <A ></A>
                <C/   >
                <D/    >
        </tag1><B/><tag2/></students>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    b = xml.find("B")
    tag2 = xml.find("tag2")
    b.add_before(tag2)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


def test_preserve_formatting_comment():
    src = textwrap.dedent(
        """\
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
        """
    )

    dst1 = textwrap.dedent(
        """\
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
        """
    )

    dst2 = textwrap.dedent(
        """\
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
        """
    )

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


def test_preserve_formatting_change_comment():
    src = textwrap.dedent(
        """\
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
        """
    )

    dst1 = textwrap.dedent(
        """\
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
        """
    )

    dst2 = textwrap.dedent(
        """\
        <root>
        <!--Option 1: Use double quotes for the literal (recommended)-->
        \t<tag1>1234556hljfdghbofdj</tag1>
            <tag2>000</tag2>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc> 
            </aaaaa>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    tag1.content = "1234556hljfdghbofdj"

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst1

    tag1.uncomment()

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst2


def test_preserve_formatting_add_and_delete():
    src = textwrap.dedent(
        """\
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
        """
    )

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
    src = textwrap.dedent(
        """\
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
        """
    )

    dst = textwrap.dedent(
        """\
        <root>
            <tag1>000
                  <tag3/>
                  <tag2>000</tag2> 
            </tag1>
            <father>
                <son1/> 
                <son2></son2>
            </father> 
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc> 
            </aaaaa>
        </root>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    father = Element("father")
    son1 = Element("son1")
    son1._is_empty = True
    son2 = Element("son2")
    father.add_as_last_son_of(tag1)
    son1.add_as_last_son_of(father)
    son2.add_after(son1)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst

    # the complex and the simple below does not work. need to calc where to add them


def test_formatting_add_as_last_son_of_1():
    src = textwrap.dedent(
        """\
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
        """
    )

    dst = textwrap.dedent(
        """\
        <root>
            <tag1>000
                  <tag3/>
                  <tag2>000</tag2> 
                  <nX5/> 
            </tag1>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc> 
            </aaaaa>
        </root>
        """
    )

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
    src = textwrap.dedent(
        """\
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
        """
    )

    dst = textwrap.dedent(
        """\
        <root>
            <tag1>000
                  <tag3/>
                  <tag2>000</tag2>  
            </tag1>
            <aaaaa>
                <bbbbb/>
                <ccccc></ccccc> 
            </aaaaa>
        </root>
        """
    )

    # move element to the same parent!!!

    file_name = __create_file(src)
    xml = SmartXML(file_name)
    tag1 = xml.find("tag1")
    tag2 = xml.find("tag2")
    tag2.add_as_last_son_of(tag1)

    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


@pytest.mark.one
def test_stam():
    src = textwrap.dedent(
        """\
        <A>
         <B>000
         <C>000</C>   
             <D>000</D>   
           </B>
        </A>
        """
    )
    src2 = textwrap.dedent(
        """\
        <A><B>000<C>000</C><D>000</D>   
           </B>
        </A>
        """
    )

    file_name = __create_file(src)
    xml = SmartXML(file_name)

    xml.write()
    result = file_name.read_text()
    pass


# TODO - add several new tags to unformatted file
# TODO - reset _orig_start_index when element is moved
# TODO - test format + special indentataion (3 spaces e.g.)
# TODO - move an element to a new location (check old removed, new added in right place)
# TODO - many changes/writes
# TODO - change a parent and its son
# TODO - change a parent and add new son
# TODO - add several new sons
# TODO - add new to an empty parent
# TODO - move element (add_after) to SAME parent
# TODO - _is_empty (and all the rest ) must be properties, as we need to know whether they were changed
