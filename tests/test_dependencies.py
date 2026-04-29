from pathlib import Path

from packaging.specifiers import SpecifierSet
from packaging.version import Version


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _pyproject_dependency(name):
    lines = (PROJECT_ROOT / 'pyproject.toml').read_text(encoding='utf-8').splitlines()
    in_dependencies = False

    for line in lines:
        stripped = line.strip()

        if stripped == '[tool.poetry.dependencies]':
            in_dependencies = True
            continue

        if in_dependencies and stripped.startswith('['):
            break

        if in_dependencies and stripped.startswith(f'{name} = '):
            return stripped.split('=', 1)[1].strip().strip('"')

    raise AssertionError(f'{name} dependency not found')


def _poetry_constraint_to_specifier(constraint):
    if not constraint.startswith('^'):
        return constraint

    version = Version(constraint[1:])
    if version.major > 0:
        upper = f'{version.major + 1}.0.0'
    elif version.minor > 0:
        upper = f'0.{version.minor + 1}.0'
    else:
        upper = f'0.0.{version.micro + 1}'

    return f'>={version},<{upper}'


def test_httpx_dependency_accepts_027():
    specifier = SpecifierSet(_poetry_constraint_to_specifier(_pyproject_dependency('httpx')))

    assert Version('0.27.0') in specifier
