## 1.1.6
- fix a bug in content setter

## 1.1.5
- performance improvement

## 1.1.4
- add support for searching a text only comment via `find()`

## 1.1.3
- add __str__ to elements
- fix bugs

## 1.1.2
- remove `typing-extensions`

## 1.1.1
- add required `typing-extensions` to pipfile

## 1.1.0
- Improve support for multiple lines content
  - **Breaking Change** User can not directly change content via `tag.contnt = "abc"`
    - As content can be multiple lines, they are now a part of elements' sons  
- add `add_as_first_son_of` to `ElementBase`
- remove deprecated `add_as_son_of`
  - Use `add_as_first_son_of` or `add_as_last_son_of` instead.

## 1.0.21
- Safely write the file by writing to a temporary file first and then renaming it.

## 1.0.20
- Improve README

## 1.0.19
- Support mixed content

## 1.0.18
- Support case-insensitive search for content

## 1.0.17
- Support case-insensitive search

## 1.0.16
- A small performance improvement

## 1.0.15
- Fixed a bug causing a crash when searching an XML with DocType element in it

## 1.0.14
- Add `Element`'s method `add_as_last_son_of`

## 1.0.13
- Improve support for comments 

## 1.0.12
- Add line number to bad format xml exceptions

## 1.0.11
- Add `uncomment()` to `Element`

## 1.0.10
- Add support for Python 3.9

## 1.0.9
- Add support for Python 3.9

## 1.0.8
- Add support for Python 3.9

## 1.0.7
- Add support for Python 3.9

## 1.0.6
- fix an import in the README example

## 1.0.5
- deprecate `Element.add_as_son_of` and `Element.set_as_parent_of` 
  - It is unclear where the element is added in case of multiple children with the same name.
  - Use `add_before()` or `add_after()` instead.

## 1.0.5
- fix a bug in find with with_content only

## 1.0.4
- fix a bug in read()

## 1.0.3
- Add changelog

## 1.0.2
- Improve README

## 1.0.1
- Fix a bug in find with content

## 1.0.0
- Initial release

