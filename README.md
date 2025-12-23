# smartXML

The **smartXML** package enables you to read, search, manipulate, and write XML files with ease.

The API is designed to be as simple as possible, but it will be enhanced according to usage and requests.

---

## Usage Example

```python
from pathlib import Path
from smartxml import SmartXML, TextOnlyComment

input_file = Path('./example.xml')
xml = SmartXML(input_file)

names = xml.find('students|student|firstName', only_one=False)

for name in names:
    if name.content == 'Bob':
        bob = name.parent
        bob.comment_out()

        header = TextOnlyComment('Bob is out')
        header.add_before(bob)

xml.write()
