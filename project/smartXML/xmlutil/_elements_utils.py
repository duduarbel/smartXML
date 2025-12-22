def _find_one_in_sons(
    element: "Element",
    names_list: list[str],
    with_content: str = None,
) -> "Element":
    if not names_list:
        return element
    for name in names_list:
        for son in element._sons:
            if _check_match(son, name, with_content):
                found = _find_one_in_sons(son, names_list[1:], with_content)
                if found:
                    return found
    return None


def _check_match(element: "Element", names: str, with_content: str) -> bool:
    if names and element.name != names:
        return False
    if with_content and element.content != with_content:
        return False

    return True


def _find_one(element: "Element", names: str, with_content: str) -> "Element":

    if _check_match(element, names=names, with_content=with_content):
        return element

    names_list = names.split("|")

    if len(names_list) > 1:
        if element.name == names_list[0]:
            found = _find_one_in_sons(element, names_list[1:], with_content)
            if found:
                return found

    for son in element._sons:
        found = _find_one(son, names, with_content)
        if found:
            return found
    return None


def _find_all(element: "Element", names: str, with_content: str) -> list["Element"]:
    results = []
    if _check_match(element, names=names, with_content=with_content):
        results.extend([element])
        for son in element._sons:
            results.extend(_find_all(son, names, with_content))
        return results

    names_list = names.split("|")

    if _check_match(element, names_list[0], with_content):
        sons = []
        sons.extend(element._sons)
        match = []
        for index, name in enumerate(names_list[1:]):
            for son in sons:
                if son.name == name:
                    if index == len(names_list) - 2:
                        results.append(son)
                    else:
                        match.extend(son._sons)
            sons.clear()
            sons.extend(match)
            match.clear()

    for son in element._sons:
        results.extend(_find_all(son, names, with_content))

    return results
