# smartXML

The **smartXML** package enables you to read, search, manipulate, and write XML files with ease.

The API is designed to be simple, but it will be enhanced according to usage and requests.
The package includes a `SmartXML` representing the XML file, and `ElementBase` representing each element in the XML tree
### SmartXML:
- properties:
    - `tree`: the root element of the XML file
    - `declaration`: the XML declaration (e.g., `<?xml version="1.0" encoding="UTF-8"?>`)
- methods:
    - `read`: reads the XML file from the root element
    - `write`: writes the XML to a file
    - `find`: finds elements from the root element
    - `to_string`: converts the entire XML tree to a string

### ElementBase: (base class for Element, Comment, TextOnlyComment, CData, and Doctype)
- properties:
    - `name`: the name of the element
    - `parent`: the parent element
- methods:
    - `find`: finds elements from the current element
    - `remove`: removes the current element from its parent
    - `comment_out`: comments out the current element
    - `to_string`: converts the current element to a string
    - `get_path`: gets the path as a string from the root of the XML tree, separated by |
    - `is_comment` : returns True if the element is a comment
    - `add_before`: adds an element before the current element
    - `add_after`: adds an element after the current element
    - `add_as_last_son_of`: adds an element as the last son of the current element

### Usage Example

```python
from pathlib import Path
from smartXML.xmltree import SmartXML, TextOnlyComment

input_file = Path('files/students.xml')
xml = SmartXML(input_file)

first_name = xml.find('students|student|firstName', with_content='Bob')
bob = first_name.parent
bob.comment_out()
header = TextOnlyComment('Bob is out')
header.add_before(bob)

xml.write()
```
result (files/students.xml):
```xml
<students>
  <!-- Bob is out -->
  <!--
    <student id="S002">
	  <firstName>Bob</firstName>
	  <lastName>Levi</lastName>
    </student>
  -->
</students>
```