import textwrap

from smartXML.xmltree import SmartXML
from smartXML.element import Element, TextOnlyComment
import pytest


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
        \t\t<age>300
        \t\t\t<old/>
        \t\t</age>
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
    \t\t<!--
    \t\t\t<age>20
    \t\t\t\t<old/>
    \t\t\t</age>
    \t\t-->
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
    \t\t<!-- tag4 comment -->
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


@pytest.mark.one
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
    tag1 = xml.find("tag1")
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
    \t<!--new text-->
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
    <students><A>
    \t\t<B>
    \t\t\t<!--BBBBB-->
    \t\t</B>
    </A>
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


def test_preserve_formatting_comment():
    src = textwrap.dedent(
        """\
        <root>
            <!-- first comment -->
            <!--
                <tag1>000</tag1>
                <tag2>000</tag2>
                <tag3>000</tag3>
            -->
            <tag4>000</tag4>
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
            <!-- first comment -->
            <!--
                <tag1>000</tag1>
        \t\t<tag2>000
        \t\t\t<tag2_1>
        \t\t\t</tag2_1>
        \t\t</tag2>
                <tag3>000</tag3>
            -->
            <tag4>000</tag4>
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
    tag2_1 = Element("tag2_1")
    tag2_1.add_as_last_son_of(tag2)
    xml.write(preserve_format=True)
    result = file_name.read_text()
    assert result == dst


# TODO - add multiple modifications
# TODO - add comment modificaions
# TODO - add several new tags to unformatted file
# TODO - reset _orig_start_index when element is moved
# TODO - add contect to _is_empty tag ???
# TODO - test format + special indentataion (3 spaces e.g.)
# TODO change text comment to short/long text
# TODO - support removing elements (keep them dead???)
# TODO - move an element to a new location (check old removed, new added in right place)
