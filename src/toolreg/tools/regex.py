from __future__ import annotations

from typing import Any, Literal


def re_replace(
    value: str = "",
    pattern: str = "",
    replacement: str = "",
    *,
    ignorecase: bool = False,
    multiline: bool = False,
    count: int = 0,
) -> str:
    """Perform a `re.sub` returning a string.

    Filter adapted from Ansible

    Args:
        value: The value to search-replace.
        pattern: The regex pattern to use
        replacement: The replacement pattern to use
        ignorecase: Whether to ignore casing
        multiline: Whether to do a multiline regex search
        count: Amount of maximum substitutes.
    """
    import re

    flags = 0
    if ignorecase:
        flags |= re.I
    if multiline:
        flags |= re.M
    pat = re.compile(pattern, flags=flags)
    output, _subs = pat.subn(replacement, value, count=count)
    return output


def re_findall(
    value: str,
    regex: str,
    *,
    ignorecase: bool = False,
    multiline: bool = False,
) -> list[Any]:
    """Perform re.findall and return the list of matches.

    Filter adapted from Ansible

    Args:
        value: The text to search in
        regex: The regex to use for searching
        ignorecase: Whether char casing should be ignored
        multiline: Whether to perform a multi-line search
    """
    import re

    flags = 0
    if ignorecase:
        flags |= re.I
    if multiline:
        flags |= re.M
    return re.findall(regex, value, flags)


def re_search(
    value: str,
    regex: str,
    *args: str,
    ignorecase: bool = False,
    multiline: bool = False,
) -> list[str] | None | str:
    """Perform re.search and return the list of matches or a backref.

    Filter adapted from Ansible

    Args:
        value: The text to search in
        regex: The regex to use for searching
        args: Optional back references to return
        ignorecase: Whether char casing should be ignored
        multiline: Whether to perform a multi-line search
    """
    import re

    def parse_group(arg: str) -> int | str:
        if arg.startswith("\\g"):
            if match := re.match(r"\\g<(\S+)>", arg):
                return match.group(1)
        elif arg.startswith("\\") and (match := re.match(r"\\(\d+)", arg)):
            return int(match.group(1))
        msg = "Unknown argument"
        raise ValueError(msg)

    groups = [parse_group(arg) for arg in args]

    flags = 0
    if ignorecase:
        flags |= re.I
    if multiline:
        flags |= re.M
    if match := re.search(regex, value, flags):
        if not groups:
            return match.group()
        return [match.group(item) for item in groups]
    return None


def re_escape(string: str, re_type: Literal["python", "posix_basic"] = "python") -> str:
    """Escape all regular expressions special characters from STRING.

    Filter adapted from Ansible

    Args:
        string: The string to escape
        re_type: The escape type
    """
    import re

    match re_type:
        case "python":
            return re.escape(string)
        case "posix_basic":
            # list of BRE special chars:
            return re_replace(string, r"([].[^$*\\])", r"\\\1")
        case _:
            msg = f"Invalid regex type ({re_type})"
            raise NotImplementedError(msg)


if __name__ == "__main__":
    result = re_replace("hello world", r"(\w+)", r"\1!")
    print(result)
