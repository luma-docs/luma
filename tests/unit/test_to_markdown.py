import pytest

from luma.models import PyClass, PyFunc, PyObj

EXAMPLE_PYFUNC = PyFunc(
    name="name",
    summary="summary",
    desc="desc",
    examples=[
        {"desc": None, "code": "code"},
    ],
    signature="signature",
    args=[
        {"name": "arg", "type": "int", "desc": "arg desc"},
    ],
    returns="returns",
)
EXAMPLE_PYFUNC_MARKDOWN = """## name

```python
signature
```

summary

desc

**Arguments**

- **arg**: arg desc

**Returns**

returns

**Examples**

```python
code
```"""

EXAMPLE_PYCLASS = PyClass(
    name="name",
    summary="summary",
    desc="desc",
    examples=[
        {"desc": None, "code": "code"},
    ],
    signature="signature",
    args=[
        {"name": "arg", "type": "int", "desc": "arg desc"},
    ],
    methods=[
        PyFunc(
            name="method",
            summary="summary",
            desc="desc",
            examples=[
                {"desc": None, "code": "code"},
            ],
            signature="signature",
            args=[
                {"name": "arg", "type": "int", "desc": "arg desc"},
            ],
            returns="returns",
        ),
    ],
)
EXAMPLE_PYCLASS_MARKDOWN = """## name

```python
signature
```

summary

desc

**Arguments**

- **arg**: arg desc

**Examples**

```python
code
```"""


@pytest.mark.parametrize(
    "api, expected_markdown",
    [
        (EXAMPLE_PYFUNC, EXAMPLE_PYFUNC_MARKDOWN),
        (EXAMPLE_PYCLASS, EXAMPLE_PYCLASS_MARKDOWN),
    ],
    ids=["func", "class"],
)
def test_to_markdown(api: PyObj, expected_markdown: str):
    assert api.to_markdown() == expected_markdown
