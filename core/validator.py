import json, base64
from pathlib import Path
from typing import Dict, List

class SecurityError(Exception):
    pass

class Validator:
    def __init__(self, config):
        self.config = config
        self.workspace = Path(config["workspace"]["root_directory"]).resolve()
        self.allowed = [Path(p).resolve() for p in config["workspace"].get("allowed_paths", [])]
        self.wl = config["execution"]["command_whitelist"]
        self.bl = config["execution"]["command_blacklist"]
        self.sm = config["system"]["safety_mode"]

    def sanitize_path(self, path: str) -> Path:
        target = Path(path)
        if target.is_absolute():
            target = Path(target.name)
        if ".." in target.parts:
            target = Path(target.name)
        target = (self.workspace / target).resolve()
        if not str(target).startswith(str(self.workspace)):
            target = self.workspace / target.name
        return target

    def validate_build_manifest(self, manifest: dict) -> dict:
        """Ensure the manifest has required keys, return cleaned version."""
        if not isinstance(manifest, dict):
            raise SecurityError("Invalid manifest (not a dict)")
        project = manifest.get("project", manifest.get("project_name", "project"))
        files = manifest.get("files", [])
        dirs = manifest.get("directories", manifest.get("dirs", []))
        if not files:
            raise SecurityError("Manifest contains no files")
        clean = {
            "project": project,
            "directories": dirs,
            "files": files
        }
        return clean

    def validate_file_content(self, content: str) -> str:
        """Ensure generated file content is non-empty and not just an error message."""
        stripped = content.strip()
        if not stripped:
            raise SecurityError("Empty file content from AI")
        if len(stripped) < 3:
            raise SecurityError("File content too short")
        return stripped

    def validate_execution_plan(self, plan):
        # Unused for /build now, but keep for other commands
        return plan
