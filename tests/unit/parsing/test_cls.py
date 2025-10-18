from luma.models import DocstringExample, PyArg, PyObjType
from luma.parser import parse_obj


def test_comprehensive():
    class A:
        """Class summary.

        Class description.

        Examples:
            >>> A(0)
        """

        def __init__(self, x: int):
            """Constructor summary.

            Constructor description.

            Args:
                x: Constructor arg description.
            """
            pass

        def f(self, y: int) -> str:
            """Method summary.

            Method description.

            Args:
                x: Method arg description.

            Returns:
                Method returns description.

            Examples:
                >>> a = A(0)
                >>> a.f(0)
            """
            return ""

    class_definition = parse_obj(A, "A")

    assert class_definition.name == "A"
    assert class_definition.type == PyObjType.CLASS
    assert class_definition.summary == "Class summary."
    assert class_definition.desc == "Class description."
    assert class_definition.examples == [DocstringExample(desc=None, code=">>> A(0)")]
    assert class_definition.signature == "A(x: int)"
    assert class_definition.args == [
        PyArg(name="x", type="int", desc="Constructor arg description.")
    ]
    assert len(class_definition.methods) == 1


def test_signature():
    class A:
        def __init__(self, x: int):
            pass

    definition = parse_obj(A, "A")

    assert definition.signature == "A(x: int)"


def test_signature_with_no_constructor():
    class A:
        pass

    definition = parse_obj(A, "A")

    assert definition.signature == "A()"
