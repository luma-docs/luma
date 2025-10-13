"""This module defines the internal config model used by the frontend."""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel


class ResolvedPage(BaseModel):
    type: Literal["page"] = "page"
    title: str
    path: str


class ResolvedLink(BaseModel):
    type: Literal["link"] = "link"
    href: str
    title: str


class ResolvedReference(BaseModel):
    type: Literal["reference"] = "reference"
    title: str
    relative_path: str
    apis: List[str]


class ResolvedSection(BaseModel):
    type: Literal["section"] = "section"
    title: str
    contents: List[Union[ResolvedPage, ResolvedReference, ResolvedLink]]


class ResolvedConfig(BaseModel):
    name: str
    favicon: Optional[str] = None
    navigation: List[
        Union[ResolvedPage, ResolvedSection, ResolvedReference, ResolvedLink]
    ]
