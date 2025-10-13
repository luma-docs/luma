import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Union

import yaml
from pydantic import BaseModel, model_validator

from .utils import get_module_and_relative_name, get_obj

CONFIG_FILENAME = "luma.yaml"

logger = logging.getLogger(__name__)


Page = str


class Reference(BaseModel):
    reference: str
    apis: List[str]

    @model_validator(mode="after")
    def validate_can_get_apis(self):
        for qualname in self.apis:
            self._validate_can_get_api(qualname)
        return self

    def _validate_can_get_api(self, qualname: str):
        try:
            module, relative_name = get_module_and_relative_name(qualname)
        except ImportError:
            package_name = qualname.split(".")[0]
            raise ValueError(
                f"Your config references '{qualname}', but Luma couldn't import the "
                f"package '{package_name}'. Make sure the module is installed in the "
                "current environment."
            )

        try:
            get_obj(module, relative_name)
        except AttributeError:
            raise ValueError(
                f"Your config references '{qualname}'. Luma imported the module "
                f"'{module.__name__}', but couldn't get the object '{relative_name}'. Are "
                "you sure the referenced object exists?"
            )


class Link(BaseModel):
    link: str
    title: Optional[str] = None


class Section(BaseModel):
    section: str
    contents: List[Union[Page, Reference, Link]]


NavigationItem = Union[Page, Section, Reference, Link]


class Config(BaseModel):
    name: str
    favicon: Optional[str] = None
    navigation: List[NavigationItem]

    # We manually add this field when we read the config file. The user can't specify
    # it.
    project_root: str

    @model_validator(mode="after")
    def validate_favicon_exists(self):
        if self.favicon is None:
            return self

        local_path = os.path.join(self.project_root, self.favicon)
        if not os.path.exists(local_path):
            raise ValueError(
                f"Your config specifies a favicon at '{self.favicon}', but the file doesn't "
                "exist. Create the file or update the config to point to an existing file."
            )

        return self

    @model_validator(mode="after")
    def validate_pages_exist(self):
        for item in self.navigation:
            if isinstance(item, str):
                self._validate_page_exists(item)
            elif isinstance(item, Section):
                for subitem in item.contents:
                    if isinstance(subitem, str):
                        self._validate_page_exists(subitem)

        return self

    def _validate_page_exists(self, path: str):
        if path.startswith(("http://", "https://")):
            return

        local_path = os.path.join(self.project_root, path)
        if not os.path.exists(local_path):
            raise ValueError(
                f"Your config references a page at '{path}', but the file doesn't "
                "exist. Create the file or update the config to point to an existing file."
            )

        if not path.endswith(".md"):
            raise ValueError(
                f"Your config references a page at '{path}', but the file isn't a "
                "Markdown file. Luma only supports Markdown files."
            )


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

    return Config.model_validate(config_data)


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
