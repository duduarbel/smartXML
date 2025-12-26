from pathlib import Path
from smartXML.xmltree import SmartXML, TextOnlyComment


def test_readme_example():
    input_file = Path('files/students.xml')
    xml = SmartXML(input_file)

    first_name = xml.find('students|student|firstName', with_content='Bob')
    bob = first_name.parent
    bob.comment_out()
    header = TextOnlyComment(' Bob is out ')
    header.add_before(bob)

    xml.write()

    # restore original file
    header.remove()
    bob.uncomment()
    xml.write()


