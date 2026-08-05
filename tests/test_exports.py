"""Guard against __all__ drifting away from what the packages actually import.

`py.typed` makes remnacrow a typed package, and under PEP 484 re-export rules a
name imported in an ``__init__.py`` is only visible to type checkers when it is
listed in ``__all__``. So a forgotten entry is not a style nit — it silently
hides the symbol from mypy/pyright users. These tests fail the moment a new
model/route/exception is imported but not exported (or vice versa).
"""

import types

import pytest

import remnacrow
from remnacrow import exceptions, models, routes

MODULES = [models, routes, exceptions]


def _public_names(module: types.ModuleType) -> set[str]:
    """Public, non-submodule names a package's __init__ pulled into its namespace"""
    return {
        name
        for name, value in vars(module).items()
        if not name.startswith("_") and not isinstance(value, types.ModuleType)
    }


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.__name__)
def test_all_matches_imports(module: types.ModuleType) -> None:
    assert _public_names(module) == set(module.__all__)


@pytest.mark.parametrize("module", MODULES, ids=lambda m: m.__name__)
def test_all_has_no_duplicates(module: types.ModuleType) -> None:
    assert len(module.__all__) == len(set(module.__all__))


@pytest.mark.parametrize("module", MODULES + [remnacrow], ids=lambda m: m.__name__)
def test_all_entries_resolve(module: types.ModuleType) -> None:
    for name in module.__all__:
        assert hasattr(module, name), f"{module.__name__}.__all__ lists missing {name!r}"


def test_package_is_typed() -> None:
    """py.typed must ship inside the package, or consumers get no types at all"""
    import pathlib

    assert (pathlib.Path(remnacrow.__file__).parent / "py.typed").is_file()
