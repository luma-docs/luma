import abc
from enum import Enum
from typing import List

from pydantic import BaseModel


class PyObjType(str, Enum):
    CLASS = "class"
    FUNC = "func"


class PyArg(BaseModel):
    name: str
    type: str | None
    desc: str | None


class DocstringExample(BaseModel):
    desc: str | None
    code: str


class PyObj(BaseModel, abc.ABC):
    name: str
    type: PyObjType
    summary: str | None
    desc: str | None
    examples: List[DocstringExample]

    @abc.abstractmethod
    def to_markdown(self) -> str: ...


class PyFunc(PyObj):
    type: PyObjType = PyObjType.FUNC
    signature: str
    args: List[PyArg]
    returns: str | None

    def to_markdown(self) -> str:
        markdown = f"# {self.name}\n"
        markdown += f"\n```python\n{self.signature}\n```\n"

        if self.summary:
            markdown += f"\n{self.summary}\n"

        if self.desc:
            markdown += f"\n{self.desc}\n"

        if self.args:
            markdown += "\n## Arguments\n\n"
            for arg in self.args:
                markdown += f"- **{arg.name}**: {arg.desc}\n"

        if self.returns:
            markdown += f"\n## Returns\n\n{self.returns}\n"

        if self.examples:
            markdown += "\n## Examples\n"
            for example in self.examples:
                markdown += f"\n```python\n{example.code}\n```"

        return markdown


class PyClass(PyObj):
    type: PyObjType = PyObjType.CLASS
    signature: str
    args: List[PyArg]
    methods: List[PyFunc]

    def to_markdown(self) -> str:
        markdown = f"# {self.name}\n"
        markdown += f"\n```python\n{self.signature}\n```\n"

        if self.summary:
            markdown += f"\n{self.summary}\n"

        if self.desc:
            markdown += f"\n{self.desc}\n"

        if self.args:
            markdown += "\n## Arguments\n\n"
            for arg in self.args:
                markdown += f"- **{arg.name}**: {arg.desc}\n"

        if self.examples:
            markdown += "\n## Examples\n"
            for example in self.examples:
                markdown += f"\n```python\n{example.code}\n```"

        return markdown
