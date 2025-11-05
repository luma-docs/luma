"""Internal configuration models used by the frontend.

These models represent the resolved/processed version of the user config
after validation, path resolution, and title inference.
"""

from typing import List, Literal, Optional, Union

from pydantic import BaseModel


class ResolvedSocial(BaseModel):
    platform: str
    url: str


class ResolvedPage(BaseModel):
    type: Literal["page"] = "page"
    title: str
    path: str
    section: Optional[str] = None


class ResolvedLink(BaseModel):
    type: Literal["link"] = "link"
    href: str
    title: str


class ResolvedReference(BaseModel):
    type: Literal["reference"] = "reference"
    title: str
    relative_path: str
    apis: List[str]
    section: Optional[str] = None


class ResolvedSection(BaseModel):
    type: Literal["section"] = "section"
    title: str
    contents: List[Union[ResolvedPage, ResolvedReference, ResolvedLink]]


class ResolvedTab(BaseModel):
    type: Literal["tab"] = "tab"
    title: str
    contents: List[
        Union[ResolvedPage, ResolvedSection, ResolvedReference, ResolvedLink]
    ]


class ResolvedConfig(BaseModel):
    name: str
    favicon: Optional[str] = None
    navigation: List[
        Union[
            ResolvedPage, ResolvedSection, ResolvedReference, ResolvedLink, ResolvedTab
        ]
    ]
    socials: Optional[List[ResolvedSocial]] = None
