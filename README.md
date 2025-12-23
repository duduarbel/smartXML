# smartXML

The **smartXML** package enables you to read, search, manipulate, and write XML files with ease.

The API is designed to be simple, but it will be enhanced according to usage and requests.
The package includes a `SmartXML` representing the XML file, and `ElementBase` representing each element in the XML tree
### SmartXML:
    - properties:
        - `root`: the root element of the XML file
        - `declaration`: the XML declaration (e.g., `<?xml version="1.0" encoding="UTF-8"?>`)
    - methods:
        - `read`: reads the XML file from the root element
        - `write`: writes the XML to a file
        - `find`: finds elements from the root element

### ElementBase: (base class for Element, Comment, TextOnlyComment, CData, and Doctype)
    - properties:
        - `name`: the name of the element
        - `parent`: the parent element
    - methods:
        - `find`: finds elements from the current element
        - `remove`: removes the current element from its parent
        - `comment_out`: comments out the current element
        - `add_before`: adds an element before the current element
        - `add_after`: adds an element after the current element
        - `add_as_son_of`: adds an element as a son of the current element
        - `set_as_parent_of`: sets the current element as the parent of another element
        - `to_string`: converts the current element to a string


### Usage Example

```python
from pathlib import Path
from smartxml import SmartXML, TextOnlyComment

input_file = Path('./example.xml')
xml = SmartXML(input_file)

firstName = xml.find('students|student|firstName', with_content='Bob')
bob = firstName.parent
bob.comment_out()
header = TextOnlyComment('Bob is out')
header.add_before(bob)

xml.write()
```
result:
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