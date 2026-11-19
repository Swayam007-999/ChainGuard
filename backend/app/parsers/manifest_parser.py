"""Package manifest and lockfile parsers for dependency vulnerability scanning."""

import json
import re

from fastapi import HTTPException, status

MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB safety ceiling


class ManifestParseError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


def parse_manifest_file(
    filename: str, content_bytes: bytes
) -> tuple[str, list[dict[str, str]]]:
    """Parse a manifest or lockfile and return (ecosystem, list_of_dependencies).

    Returns:
        ecosystem: "npm" | "pypi"
        dependencies: [{"name": str, "version": str}]
    """
    if len(content_bytes) > MAX_FILE_SIZE_BYTES:
        raise ManifestParseError("File size exceeds 5MB maximum limit")

    try:
        content_text = content_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ManifestParseError("File is not valid UTF-8 text") from exc

    basename = filename.lower().split("/")[-1].split("\\")[-1]

    if basename == "package-lock.json" or basename.endswith("package-lock.json") or "package-lock" in basename:
        return "npm", _parse_package_lock_json(content_text)
    elif basename == "package.json" or basename.endswith("package.json") or basename.endswith(".json"):
        # Check if content is actually a lockfile
        if "lockfileVersion" in content_text and "packages" in content_text:
            return "npm", _parse_package_lock_json(content_text)
        return "npm", _parse_package_json(content_text)
    elif basename == "requirements.txt" or basename.endswith(".txt") or "requirements" in basename:
        return "pypi", _parse_requirements_txt(content_text)
    else:
        raise ManifestParseError(
            f"Unsupported manifest file '{filename}'. Supported: package.json, package-lock.json, requirements.txt"
        )


def _clean_semver(ver: str) -> str:
    """Strip semver range specifiers (e.g. ^1.2.3, ~2.0.0, >=3.0.0) to get base version."""
    cleaned = re.sub(r"^[^\d]*", "", ver.strip())
    # Take first version if range e.g. "1.2.3 - 2.0.0"
    cleaned = cleaned.split(" ")[0].split("<")[0].split(">")[0].strip()
    return cleaned or "0.0.0"


def _parse_package_json(text: str) -> list[dict[str, str]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ManifestParseError(f"Invalid JSON in package.json: {exc}") from exc

    deps: dict[str, str] = {}

    for section in ("dependencies", "devDependencies"):
        section_data = data.get(section, {})
        if isinstance(section_data, dict):
            for name, ver in section_data.items():
                if isinstance(name, str) and isinstance(ver, str):
                    deps[name.strip()] = _clean_semver(ver)

    return [{"name": name, "version": ver} for name, ver in deps.items()]


def _parse_package_lock_json(text: str) -> list[dict[str, str]]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ManifestParseError(f"Invalid JSON in package-lock.json: {exc}") from exc

    deps: dict[str, str] = {}

    # Lockfile v2 / v3 uses data["packages"]
    if "packages" in data and isinstance(data["packages"], dict):
        for pkg_path, pkg_info in data["packages"].items():
            if not pkg_path:  # Root package is ""
                continue
            if isinstance(pkg_info, dict) and "version" in pkg_info:
                # Format: "node_modules/lodash" or "node_modules/@scope/pkg"
                name = pkg_path.split("node_modules/")[-1]
                ver = pkg_info.get("version", "")
                if name and ver and isinstance(ver, str):
                    deps[name.strip()] = _clean_semver(ver)

    # Lockfile v1 fallback uses data["dependencies"]
    elif "dependencies" in data and isinstance(data["dependencies"], dict):
        for name, info in data["dependencies"].items():
            if isinstance(info, dict) and "version" in info:
                ver = info.get("version", "")
                if isinstance(ver, str):
                    deps[name.strip()] = _clean_semver(ver)

    return [{"name": name, "version": ver} for name, ver in deps.items()]


REQ_REGEX = re.compile(
    r"^\s*([a-zA-Z0-9_\-\.]+)\s*(?:==|>=|<=|~=|>|<|===)?\s*([a-zA-Z0-9_\-\.]*)"
)


def _parse_requirements_txt(text: str) -> list[dict[str, str]]:
    deps: dict[str, str] = {}

    for line in text.splitlines():
        line = line.strip()
        # Skip empty lines, comments, and pip flags (-r, -i, --extra-index-url)
        if not line or line.startswith(("#", "-")):
            continue
        # Strip trailing environment markers or comments
        line = line.split(";")[0].split("#")[0].strip()

        match = REQ_REGEX.match(line)
        if match:
            pkg_name = match.group(1).strip()
            pkg_ver = match.group(2).strip() or "0.0.0"
            deps[pkg_name] = pkg_ver

    return [{"name": name, "version": ver} for name, ver in deps.items()]
