import inspect
from pathlib import Path
from types import ModuleType

from python_tool_competition_2024.calculation.generation_results_calculator import (
    _target_to_file_info,
)
from python_tool_competition_2024.target_finder import find_targets

from .helpers import TARGETS_DIR, get_test_config


def test_import_module() -> None:
    config = get_test_config(show_commands=False, root_dir=Path.cwd())

    module_names = {}

    for target in find_targets(config):
        file_info = _target_to_file_info(target, config)
        module = file_info.import_module()
        assert inspect.ismodule(module)
        assert file_info.module_name == module.__name__
        module_names[file_info.absolute_path] = _get_public_attr_names(module)

    assert module_names == {
        TARGETS_DIR / "example1.py": frozenset({"other_method", "some_method"}),
        TARGETS_DIR / "example2.py": frozenset({"my_method"}),
        TARGETS_DIR / "sub_example" / "__init__.py": frozenset({"helper"}),
        TARGETS_DIR / "sub_example" / "example3.py": frozenset({"example"}),
    }


def _get_public_attr_names(module: ModuleType) -> frozenset[str]:
    return frozenset(name for name in dir(module) if not name.startswith("_"))
