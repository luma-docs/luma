"""User-facing configuration models."""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, model_validator

from .validation import validate_favicon_exists, validate_page_exists

CONFIG_FILENAME = "luma.yaml"
SUPPORTED_SOCIAL_PLATFORMS = {"discord", "github", "twitter", "slack"}

logger = logging.getLogger(__name__)


Page = str
Social = Dict[str, str]  # Maps platform name to URL


class Reference(BaseModel):
    reference: str
    apis: List[str]


class Link(BaseModel):
    link: str
    title: Optional[str] = None


class Section(BaseModel):
    section: str
    contents: List[Union[Page, Reference, Link]]


class Tab(BaseModel):
    tab: str
    contents: List[Union[Page, Section, Reference, Link]]


NavigationItem = Union[Page, Section, Reference, Link, Tab]


class Config(BaseModel):
    name: str
    favicon: Optional[str] = None
    navigation: List[NavigationItem]
    socials: Optional[List[Social]] = None

    # We manually add this field when we read the config file. The user can't specify
    # it.
    project_root: str

    @model_validator(mode="after")
    def validate_favicon_exists(self):
        if self.favicon is None:
            return self

        validate_favicon_exists(self.favicon, self.project_root)
        return self

    @model_validator(mode="after")
    def validate_pages_exist(self):
        for item in self.navigation:
            if isinstance(item, str):
                validate_page_exists(item, self.project_root)
            elif isinstance(item, Section):
                for subitem in item.contents:
                    if isinstance(subitem, str):
                        validate_page_exists(subitem, self.project_root)

        return self

    @model_validator(mode="after")
    def validate_socials(self):
        if self.socials is None:
            return self

        for social in self.socials:
            if len(social) != 1:
                raise ValueError(
                    "Each social entry must have exactly one platform-url pair, "
                    f"got: {social}"
                )

            platform = list(social.keys())[0]
            if platform not in SUPPORTED_SOCIAL_PLATFORMS:
                raise ValueError(
                    f"Invalid social platform '{platform}'. Valid platforms are: "
                    f"{', '.join(sorted(SUPPORTED_SOCIAL_PLATFORMS))}"
                )

        return self


def load_config(dir: str) -> Config:
    assert os.path.isdir(dir), f"'dir' must be a directory: '{dir}'"

    project_root = _discover_project_root(dir)
    if project_root is None:
        raise FileNotFoundError(f"Config file not found: '{dir}'")

    config_path = os.path.join(project_root, CONFIG_FILENAME)
    filename = os.path.basename(config_path)
    assert filename == CONFIG_FILENAME, f"Invalid config file: {filename}"

    with open(config_path) as file:
        try:
            config_data: Dict = yaml.safe_load(file)
            # Manually add the project root. This is necessary so that we can validate
            # the model fields.
            config_data["project_root"] = project_root
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing config file: {e}")

    config = Config.model_validate(config_data)

    # Perform validation after Pydantic parsing
    from .validation import validate_config

    validate_config(config)

    return config


def _discover_project_root(dir: str) -> Optional[str]:
    assert os.path.isdir(dir), f"'dir' must be a directory: '{dir}'"

    # 'resolve()' ensures the path is absolute and resolves any symbolic links.
    resolved_dir = Path(dir).resolve()

    # Traverse upwards until we reach the root directory
    for parent in [resolved_dir, *resolved_dir.parents]:
        config_path = parent / CONFIG_FILENAME
        if config_path.exists():
            return str(parent)

    return None


def create_or_update_config(dir: str, package_name: str) -> Config:
    assert os.path.isdir(dir), f"'dir' must be a directory: '{dir}'"

    config = load_config(dir)
    updated_config = config.model_copy(update={"name": package_name})

    config_path = os.path.join(dir, CONFIG_FILENAME)
    with open(config_path, "w") as file:
        yaml.dump(updated_config.model_dump(), file, default_flow_style=False)

    return updated_config
