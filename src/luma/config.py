import os
from typing import Dict, List, Union
from pathlib import Path
import yaml
from pydantic import BaseModel
from typing import Optional
from .utils import get_obj, get_module_and_qualname


class Page(BaseModel):
    title: str
    path: str


class Reference(BaseModel):
    ref: str


class Section(BaseModel):
    section: str
    contents: List[Union[Page, Reference]]


class Config(BaseModel):
    name: str
    navigation: List[Union[Section, Page, Reference]]

    class Config:
        frozen = True


def load_config(dir: str) -> Config:
    assert os.path.isdir(dir), f"'dir' must be a directory: '{dir}'"

    config_path = _discover_config(dir)
    if config_path is None:
        raise FileNotFoundError(f"Config file not found: '{dir}'")

    filename = os.path.basename(config_path)
    assert filename == "luma.yaml", f"Invalid config file: {filename}"

    with open(config_path) as file:
        try:
            config_data: Dict = yaml.safe_load(file)
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing config file: {e}")

    return Config.model_validate(config_data)


def _discover_config(dir: str) -> Optional[str]:
    assert os.path.isdir(dir), f"'dir' must be a directory: '{dir}'"

    # 'resolve()' ensures the path is absolute and resolves any symbolic links.
    resolved_dir = Path(dir).resolve()

    # Traverse upwards until we reach the root directory
    for parent in [resolved_dir, *resolved_dir.parents]:
        config_path = parent / "luma.yaml"
        if config_path.exists():
            return str(config_path)

    return None


def create_or_update_config(dir: str, package_name: str) -> Config:
    assert os.path.isdir(dir), f"'dir' must be a directory: '{dir}'"

    try:
        config = load_config(dir)
    except FileNotFoundError:
        config = Config(name=package_name, navigation={})

    updated_config = config.model_copy(update={"name": package_name})

    config_path = os.path.join(dir, "luma.yaml")
    with open(config_path, "w") as file:
        yaml.dump(updated_config.model_dump(), file, default_flow_style=False)

    return updated_config


def validate_config(config: Config, project_root: str) -> None:
    for item in config.navigation:
        assert isinstance(item, (Section, Page, Reference)), f"Invalid item: {item}"

        if isinstance(item, Section):
            _validate_section(item, project_root)
        if isinstance(item, Reference):
            _validate_reference(item)
        if isinstance(item, Page):
            _validate_page(item, project_root)


def _validate_section(section: Section, project_root: str):
    for item in section.contents:
        if isinstance(item, Reference):
            _validate_reference(item)
        if isinstance(item, Page):
            _validate_page(item, project_root)


def _validate_reference(reference: Reference):
    fully_qualified_name = reference.ref

    try:
        module, qualname = get_module_and_qualname(fully_qualified_name)
    except ImportError:
        package_name = fully_qualified_name.split(".")[0]
        raise ValueError(
            f"Your config references '{fully_qualified_name}', but Luma couldn't "
            f"import the package '{package_name}'. Make sure the module is installed "
            "in the current environment."
        )

    try:
        get_obj(module, qualname)
    except AttributeError:
        raise ValueError(
            f"Your config references '{qualname}'. Luma imported the module "
            f"'{module.__name__}',' but couldn't get the object '{qualname}'. Are you "
            "sure the referenced object exists?"
        )


def _validate_page(page: Page, project_root: str):
    page_path = os.path.join(project_root, page.path)
    if not os.path.exists(page_path):
        raise ValueError(
            f"Your config references a page at '{page.path}', but the file doesn't "
            "exist. Create the file or update the config to point to an existing file."
        )

    if not page.path.endswith(".md"):
        raise ValueError(
            f"Your config references a page at '{page.path}', but the file isn't a "
            "Markdown file. Luma only supports Markdown files."
        )
