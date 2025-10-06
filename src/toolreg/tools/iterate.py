from __future__ import annotations

from collections.abc import Mapping
import itertools
import operator
from typing import TYPE_CHECKING, Any

from toolreg import Example, register_tool


if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Iterable


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:compare",
    examples=[
        Example(
            title="basic",
            template="""{% for a, b in [1, 2, 3, 4] | pairwise %}
{{ a }}: {{ b }}
{% endfor %}""",
        )
    ],
)
def pairwise[T](items: Iterable[T]) -> itertools.pairwise[tuple[T, T]]:
    """Return an iterator of overlapping pairs taken from the input iterator.

    s -> (s0,s1), (s1,s2), (s2, s3), ...

    Args:
        items: The items to iter pair-wise
    """
    return itertools.pairwise(items)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:link-chain",
    examples=[
        Example(
            title="basic",
            template="""{% for val in range(3) | chain(range(5)) %}
{{ val }}
{% endfor %}""",
        )
    ],
)
def chain[T](*iterables: Iterable[T]) -> itertools.chain[T]:
    """Chain all given iterators.

    Make an iterator that returns elements from the first iterable until it is
    exhausted, then proceeds to the next iterable, until all of the iterables
    are exhausted. Used for treating consecutive sequences as a single sequence.

    Examples:
        ``` py
        chain('ABC', 'DEF') --> A B C D E F
        ```
    Args:
        iterables: The iterables to chain
    """
    return itertools.chain(*iterables)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:multiplication",
    examples=[
        Example(
            title="basic",
            template="""{% for val in "ABCD" | product("xy") %}
{{ val }}
{% endfor %}""",
        )
    ],
)
def product(
    *iterables: Iterable[Any],
    repeat: int = 1,
) -> itertools.product[tuple[Any, ...]]:
    """Cartesian product of input iterables.

    Roughly equivalent to nested for-loops in a generator expression.
    For example, product(A, B) returns the same as ((x,y) for x in A for y in B).

    The nested loops cycle like an odometer with the rightmost element advancing
    on every iteration. This pattern creates a lexicographic ordering so that if
    the input's iterables are sorted, the product tuples are emitted in sorted order.

    To compute the product of an iterable with itself, specify the number of repetitions
    with the optional repeat keyword argument. For example, product(A, repeat=4)
    means the same as product(A, A, A, A).

    Examples:
        ``` py
        product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        ```

    Args:
        iterables: The iterables to create a cartesian product from
        repeat: The amount of repititions
    """
    return itertools.product(*iterables, repeat=repeat)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:repeat",
    examples=[
        Example(
            title="basic",
            template="""{% for val in "ABCD" | repeat(2) %}
{{ val }}
{% endfor %}""",
        )
    ],
)
def repeat[T](obj: T, times: int | None = None) -> Iterable[T]:
    """Make an iterator that returns object over and over again.

    Runs indefinitely unless the times argument is specified.

    Examples:
        ``` py
        repeat(10, 3) --> 10 10 10
        ```

    Args:
        obj: The object to return over and over again
        times: The amount of times to return the object (None means infinite)
    """
    if times:
        return itertools.repeat(obj, times=times)
    return itertools.repeat(obj)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:zip-box-outline",
    examples=[
        Example(
            title="basic",
            template="""{% for val in "ABCD" | zip_longest("xy", fillvalue="-") %}
{{ val }}
{% endfor %}""",
        )
    ],
)
def zip_longest(*iterables: Iterable[Any], fillvalue: Any = None) -> Iterable[Any]:
    """Make an iterator that aggregates elements from each of the iterables.

    If the iterables are of uneven length, missing values are filled-in with fillvalue.
    Iteration continues until the longest iterable is exhausted.

    Examples:
        ``` py
        zip_longest('ABCD', 'xy', fillvalue='-') --> Ax By C- D-
        ```

    Args:
        iterables: The iterables to zip
        fillvalue: value to use for filling in case the iterables are of uneven length
    """
    return itertools.zip_longest(*iterables, fillvalue=fillvalue)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:segment",
    examples=[
        Example(
            title="basic",
            template=(
                """{% for val in "ABCDEFG" | islice(2) %}"""
                """{{ val }}"""
                """{% endfor %}"""
            ),
        )
    ],
)
def islice[T](iterable: Iterable[T], *args: int | None) -> itertools.islice[T]:
    """Make an iterator that returns selected elements from the iterable.

    If start is non-zero, then elements from the iterable are skipped until start
    is reached. Afterward, elements are returned consecutively unless step is set
    higher than one which results in items being skipped. If stop is None,
    then iteration continues until the iterator is exhausted, if at all;
    otherwise, it stops at the specified position.

    If start is None, then iteration starts at zero. If step is None,
    then the step defaults to one.

    Unlike regular slicing, islice() does not support negative values
    for start, stop, or step. Can be used to extract related fields from data
    where the internal structure has been flattened (for example, a multi-line report
    may list a name field on every third line).

    Examples:
        ``` py
        islice('ABCDEFG', 2) --> A B
        islice('ABCDEFG', 2, 4) --> C D
        islice('ABCDEFG', 2, None) --> C D E F G
        islice('ABCDEFG', 0, None, 2) --> A C E G
        ```

    Args:
        iterable: Iterable to slice
        args: Arguments passed to itertools.islice
    """
    return itertools.islice(iterable, *args)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:zip-box",
    examples=[
        Example(
            title="basic",
            template="""
{% for a, b in [1, 2] | zip([3, 4]) %}
{{ a }}: {{ b }}
{% endfor %}""",
        )
    ],
)
def do_zip[T](*items: Iterable[T]) -> zip[tuple[T, ...]]:
    """Zip iterables into a single one.

    Args:
        items: The iterables to zip
    """
    return zip(*items)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:list-status",
    examples=[
        Example(
            title="basic",
            template="""{{ ["1", "2", "3", "1"] | reduce_list }}""",
        )
    ],
)
def reduce_list[T](items: Iterable[T]) -> list[T]:
    """Reduce duplicate items in a list and preserve order.

    Args:
        items: The iterable to recude to a unique-item list
    """
    return list(dict.fromkeys(items))


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:unfold-more-horizontal",
    examples=[
        Example(
            title="basic",
            template="""{{ {"a": {"b": {"c": "d"} } } | flatten_dict }}""",
        )
    ],
)
def flatten_dict(dct: Mapping, sep: str = "/", _parent_key: str = "") -> Mapping:
    """Flatten a nested dictionary to a flat one.

    The individual parts of the "key path" are joined with given separator.

    Args:
        dct: The dictionary to flatten
        sep: The separator to use for joining
        _parent_key: Internal parameter for recursive calls
    """
    items: list[tuple[str, str]] = []
    for k, v in dct.items():
        new_key = _parent_key + sep + k if _parent_key else k
        if isinstance(v, Mapping):
            flattened = flatten_dict(v, _parent_key=new_key, sep=sep)
            items.extend(flattened.items())
        else:
            items.append((new_key, v))
    return dict(items)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:view-grid",
    examples=[
        Example(
            title="basic",
            template="""{% for a, b in range(10) | batched(2) %}
{{ a }}: {{ b }}
{% endfor %}""",
        )
    ],
)
def batched[T](iterable: Iterable[T], n: int) -> Generator[tuple[T, ...], None, None]:
    """Batch data into tuples of length n. The last batch may be shorter.

    Note: this function was added to Py3.12 itertools

    Examples:
        ``` py
        batched('ABCDEFG', 3)  # returns ABC DEF G
        ```

    Args:
        iterable: The iterable to yield as batches
        n: The batch size
    """
    if n < 1:
        msg = "n must be at least one"
        raise ValueError(msg)
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:sort-alphabetical-ascending",
    examples=[
        Example(
            title="basic",
            template="""{{ ["A1", "B1", "A2", "A10"] | natsort }}""",
        )
    ],
)
def natsort[T](
    val: Iterable[T],
    key: str | Callable[[T], Any] | None = None,
    reverse: bool = False,
    ignore_case: bool = True,
) -> Iterable[T]:
    """Using the natsort package, sort a list naturally.

    i.e. A1, B1, A2, A10 will sort A1, A2, A10, B1.

    Args:
        val: the iterable to sort
        key: If str, sort by attribute with given name. If callable, use it as keygetter.
             If None, sort by objects itself
        reverse: Whether to reverse the sort order
        ignore_case: Whether to ignore case for sorting
    """
    from natsort import natsorted, ns

    alg = ns.IGNORECASE
    if not ignore_case:
        alg = ns.LOWERCASEFIRST
    key_fn = operator.attrgetter(key) if isinstance(key, str) else key
    return natsorted(val, key=key_fn, reverse=reverse, alg=alg)


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:group",
    examples=[
        Example(
            title="basic",
            template=(
                """{{ ["20", "20", "100", "0"] | """
                """groupby_plus(natural_sort=True) }}"""
            ),
        )
    ],
)
def groupby[T](
    data: Iterable[T],
    key: Callable[[T], Any] | str | None = None,
    *,
    sort_groups: bool = True,
    natural_sort: bool = False,
    reverse: bool = False,
) -> dict[str, list[T]]:
    """Group given iterable using given group function.

    Args:
        data: Iterable to group
        key: Sort function or attribute name to use for sorting
        sort_groups: Whether to sort the groups
        natural_sort: Whether to use a natural sort algorithm
        reverse: Whether to reverse the value list
    """
    if key is None:

        def keyfunc(x):
            return x

    elif isinstance(key, str):
        keyfunc = operator.attrgetter(key)
    else:
        keyfunc = key
    if sort_groups or natural_sort:
        if natural_sort:
            import natsort

            data = natsort.natsorted(data, key=keyfunc)
        else:
            data = sorted(data, key=keyfunc)
    if reverse:
        data = reversed(list(data))
    return {k: list(g) for k, g in itertools.groupby(data, keyfunc)}


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:alphabetical",
    examples=[
        Example(
            title="basic",
            template=(
                """{{ ["apple", "banana", "cherry", "avocado"] | """
                """groupby_first_letter }}"""
            ),
        )
    ],
)
def groupby_first_letter[T](
    data: Iterable[T],
    keyfunc: Callable[..., Any] | None = None,
) -> dict[str, list[T]]:
    """Group given iterable by first letter.

    Args:
        data: Iterable to group
        keyfunc: Optional alternative sort function
    """
    data = sorted(data, key=keyfunc or (lambda x: x))

    def first_letter(x: Any) -> Any:
        return keyfunc(x)[0].upper() if keyfunc else x[0].upper()

    return {k.upper(): list(g) for k, g in itertools.groupby(data, first_letter)}


@register_tool(
    typ="filter",
    group="iter",
    icon="mdi:check-circle-outline",
    examples=[
        Example(
            title="basic",
            template="""{{ [True, False] | any }}""",
        )
    ],
)
def do_any(seq: Iterable[Any], attribute: str | None = None) -> bool:
    """Check if at least one of the item in the sequence evaluates to true.

    The `any` builtin as a filter for Jinja templates.

    Args:
        seq: An iterable object.
        attribute: The attribute name to use on each object of the iterable.
    """
    if attribute is None:
        return any(seq)
    return any(getattr(i, attribute) for i in seq)


if __name__ == "__main__":
    # Example test
    data = ["A1", "B1", "A2", "A10"]
    result = natsort(data)
    print(list(result))  # Should print: ['A1', 'A2', 'A10', 'B1']
