# smartXML

**smartXML** is a lightweight Python package for reading, searching, manipulating, and writing XML files with a clean and intuitive API.

It is designed to make common XML operations straightforward while preserving full control over the XML structure. The API is intentionally minimal and will evolve based on real-world usage and feedback.

At its core, the package provides:
- `SmartXML`: a high-level representation of an XML document
- `ElementBase`: a common base class for all XML node types

---

## Core Concepts

### `SmartXML`

`SmartXML` represents an entire XML document, including its declaration and root element.

#### Properties
- **`tree`**  
  The root element of the XML document.

- **`declaration`**  
  The XML declaration string  
  (e.g. `<?xml version="1.0" encoding="UTF-8"?>`)

#### Methods
- **`read(path)`**  
  Read and parse an XML file from disk.

- **`write(path)`**  
  Write the current XML tree to a file.

- **`find(...)`**  
  Search for elements by name and/or content.

- **`to_string()`**  
  Serialize the entire XML document to a string.

---

### `ElementBase`

`ElementBase` is the base class for all node types in the XML tree, including:

- `Element`
- `Comment`
- `TextOnlyComment`
- `CData`
- `Doctype`

It provides common navigation, manipulation, and serialization functionality.

#### Properties
- **`name`**  
  The element name.

- **`parent`**  
  A reference to the parent element  
  (`None` if this is the root).

#### Methods
- **`find(...)`**  
  Search for descendant elements.

- **`remove()`**  
  Remove the current element from its parent.

- **`comment_out()`**  
  Comment out the current element.

- **`uncomment()`**  
  Restore a previously commented-out element.

- **`is_comment()`**  
  Return `True` if this element represents a comment.

- **`to_string()`**  
  Serialize the element (and its children) to a string.

- **`get_path()`**  
  Return the element’s path from the root, using `|` as a separator.

- **`add_before(sibling)`**  
  Insert this element before the given sibling.

- **`add_after(sibling)`**  
  Insert this element after the given sibling.

- **`add_as_last_son_of(parent)`**  
  Add this element as the last child of the given parent element.

---

## Design Goals

- Simple, readable API
- Explicit control over XML structure
- Safe and predictable tree manipulation
- Easy serialization back to valid XML

## Usage Example

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