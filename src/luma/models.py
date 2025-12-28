import abc
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel

from .rst_converter import convert_rst_to_markdown


class PyObjType(str, Enum):
    CLASS = "class"
    FUNC = "func"


class PyArg(BaseModel):
    name: str
    type: Optional[str]
    desc: Optional[str]


class DocstringExample(BaseModel):
    desc: Optional[str]
    code: str


class PyObj(BaseModel, abc.ABC):
    name: str
    type: PyObjType
    summary: Optional[str]
    desc: Optional[str]
    examples: List[DocstringExample]

    @abc.abstractmethod
    def to_markdown(self) -> str: ...


class PyFunc(PyObj):
    type: PyObjType = PyObjType.FUNC
    signature: str
    args: List[PyArg]
    returns: Optional[str]

    def to_markdown(self) -> str:
        markdown = f"## {self.name}\n"
        markdown += f"\n```python\n{self.signature}\n```\n"

        summary_md = convert_rst_to_markdown(self.summary)
        if summary_md:
            markdown += f"\n{summary_md}\n"

        desc_md = convert_rst_to_markdown(self.desc)
        if desc_md:
            markdown += f"\n{desc_md}\n"

        if self.args:
            markdown += "\n**Arguments**\n\n"
            for arg in self.args:
                desc_md = convert_rst_to_markdown(arg.desc) or arg.desc
                if arg.type:
                    markdown += f"- **{arg.name}** ({arg.type}): {desc_md}\n"
                else:
                    markdown += f"- **{arg.name}**: {desc_md}\n"

        returns_md = convert_rst_to_markdown(self.returns)
        if returns_md:
            markdown += f"\n**Returns**\n\n{returns_md}\n"

        if self.examples:
            markdown += "\n**Examples**\n"
            for example in self.examples:
                markdown += f"\n```python\n{example.code}\n```"

        return markdown


class PyClass(PyObj):
    type: PyObjType = PyObjType.CLASS
    signature: str
    args: List[PyArg]
    methods: List[PyFunc]

    def to_markdown(self) -> str:
        markdown = f"## {self.name}\n"
        markdown += f"\n```python\n{self.signature}\n```\n"

        summary_md = convert_rst_to_markdown(self.summary)
        if summary_md:
            markdown += f"\n{summary_md}\n"

        desc_md = convert_rst_to_markdown(self.desc)
        if desc_md:
            markdown += f"\n{desc_md}\n"

        if self.args:
            markdown += "\n**Arguments**\n\n"
            for arg in self.args:
                desc_md = convert_rst_to_markdown(arg.desc) or arg.desc
                if arg.type:
                    markdown += f"- **{arg.name}** ({arg.type}): {desc_md}\n"
                else:
                    markdown += f"- **{arg.name}**: {desc_md}\n"

        if self.examples:
            markdown += "\n**Examples**\n"
            for example in self.examples:
                markdown += f"\n```python\n{example.code}\n```"

        return markdown
