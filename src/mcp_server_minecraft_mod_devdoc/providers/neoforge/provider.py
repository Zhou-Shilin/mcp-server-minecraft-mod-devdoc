"""
Neoforge documentation provider implementation using local repository
"""

import re
import logging
import subprocess
import datetime
import time
import os
from typing import List, Dict, Optional, Any, Tuple
from pathlib import Path
from ...core.provider import DocProvider

logger = logging.getLogger(__name__)

class NeoforgeProvider(DocProvider):
    """
    Provider for Neoforge documentation using local repository
    """

    def __init__(self, repo_url: str = "https://github.com/neoforged/Documentation",
                 branch: str = "main",
                 repo_dir: Optional[str] = None):
        """
        Initialize the Neoforge documentation provider

        Args:
            repo_url: The URL of the Neoforge documentation repository
            branch: The branch of the repository to use
            repo_dir: The directory to store the cloned repository
        """
        self.repo_url = repo_url
        self.branch = branch

        # Set up repository directory
        if repo_dir:
            self.repo_dir = Path(repo_dir)
        else:
            self.repo_dir = Path.home() / ".local" / "share" / "mcp-server-minecraft-mod-devdoc" / "neoforge"

        self.repo_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Repository directory: {self.repo_dir}")

        # Last update timestamp file
        self.timestamp_file = self.repo_dir / "last_update.txt"

        # Clone or update the repository if needed
        self._ensure_repository()

    def _ensure_repository(self) -> bool:
        """
        Ensure the repository is cloned and up to date
        Only updates if the repository doesn't exist or if it hasn't been updated in the last 24 hours

        Returns:
            True if the repository is ready, False otherwise
        """
        repo_path = self.repo_dir / "Documentation"
        should_update = False

        # Check if we need to update
        if not repo_path.exists():
            logger.info("Repository doesn't exist, will clone it")
            should_update = True
        elif not self.timestamp_file.exists():
            logger.info("No timestamp file found, will update repository")
            should_update = True
        else:
            # Check when the repository was last updated
            try:
                last_update_time = float(self.timestamp_file.read_text().strip())
                current_time = time.time()
                time_diff = current_time - last_update_time

                # Update if more than 24 hours have passed
                if time_diff > 86400:  # 24 hours in seconds
                    logger.info(f"Repository was last updated {time_diff/3600:.1f} hours ago, will update")
                    should_update = True
                else:
                    logger.info(f"Repository was updated {time_diff/3600:.1f} hours ago, skipping update")
            except Exception as e:
                logger.warning(f"Error reading timestamp file: {e}, will update repository")
                should_update = True

        if not should_update and repo_path.exists():
            logger.info("Using existing repository without updating")
            return True

        try:
            if not repo_path.exists():
                logger.info(f"Cloning repository from {self.repo_url}...")
                result = subprocess.run(
                    ["git", "clone", "--branch", self.branch, self.repo_url, str(repo_path)],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.debug(f"Clone output: {result.stdout}")
            else:
                logger.info(f"Updating repository at {repo_path}...")
                # First try to checkout the specified branch
                try:
                    subprocess.run(
                        ["git", "-C", str(repo_path), "checkout", self.branch],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                except subprocess.CalledProcessError:
                    logger.warning(f"Failed to checkout branch {self.branch}, trying master...")
                    try:
                        subprocess.run(
                            ["git", "-C", str(repo_path), "checkout", "master"],
                            capture_output=True,
                            text=True,
                            check=True
                        )
                        self.branch = "master"
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Failed to checkout master branch: {e}")
                        return False

                # Pull the latest changes
                result = subprocess.run(
                    ["git", "-C", str(repo_path), "pull"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                logger.debug(f"Pull output: {result.stdout}")

            # Update the timestamp file
            self.timestamp_file.write_text(str(time.time()))
            logger.info("Updated repository timestamp file")

            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Git operation failed: {e.stderr}")
            return False
        except Exception as e:
            logger.exception(f"Error ensuring repository: {e}")
            return False

    def _get_directory_contents(self, path: str) -> List[Dict[str, Any]]:
        """
        Get the contents of a directory from the local repository

        Args:
            path: The path to the directory relative to the repository root

        Returns:
            A list of dictionaries containing file information
        """
        full_path = self.repo_dir / "Documentation" / path
        logger.debug(f"Getting directory contents: {full_path}")

        try:
            if not full_path.exists():
                logger.error(f"Directory does not exist: {full_path}")
                return []

            contents = []
            for item in full_path.iterdir():
                item_type = "dir" if item.is_dir() else "file"
                contents.append({
                    "name": item.name,
                    "type": item_type,
                    "path": str(item.relative_to(self.repo_dir / "Documentation"))
                })

            return contents
        except Exception as e:
            logger.exception(f"Error getting directory contents: {e}")
            return []

    def _get_file_content(self, path: str) -> str:
        """
        Get the content of a file from the local repository

        Args:
            path: The path to the file relative to the repository root

        Returns:
            The content of the file
        """
        full_path = self.repo_dir / "Documentation" / path
        logger.debug(f"Getting file content: {full_path}")

        try:
            if not full_path.exists():
                logger.error(f"File does not exist: {full_path}")
                return f"Error: File does not exist: {path}"

            return full_path.read_text(encoding="utf-8")
        except Exception as e:
            logger.exception(f"Error reading file content: {e}")
            return f"Error: Failed to read file content ({str(e)})"

    def get_versions(self) -> str:
        """
        Get a list of available documentation versions

        Returns:
            A string containing the list of available versions
        """
        try:
            # Ensure the repository is up to date
            if not self._ensure_repository():
                return "Error: Failed to ensure repository is up to date."

            contents = self._get_directory_contents("versioned_docs")
            versions = [item["name"] for item in contents if item["type"] == "dir" and item["name"].startswith("version-")]

            if not versions:
                return "No versions found in the Neoforge documentation repository."

            return "\n".join(versions)
        except Exception as e:
            logger.exception("Error getting versions")
            return f"Error: {str(e)}"

    def get_structure(self, version: str) -> str:
        """
        Get the file structure for a specific version of documentation

        Args:
            version: The version of the documentation

        Returns:
            A string containing the file structure
        """
        try:
            path = f"versioned_docs/{version}"
            structure = self._build_structure(path)

            if not structure:
                return f"No structure found for version: {version}"

            return structure
        except Exception as e:
            logger.exception("Error getting structure")
            return f"Error: {str(e)}"

    def _build_structure(self, path: str, indent: int = 0) -> str:
        """
        Build a string representation of the directory structure with file previews

        Args:
            path: The path to the directory
            indent: The indentation level

        Returns:
            A string representation of the directory structure with file previews
        """
        contents = self._get_directory_contents(path)
        if not contents:
            return ""

        result = []

        # Process directories first
        dirs = [item for item in contents if item["type"] == "dir"]
        files = [item for item in contents if item["type"] == "file" and item["name"].endswith(".md")]

        # Sort by name
        dirs.sort(key=lambda x: x["name"])
        files.sort(key=lambda x: x["name"])

        for item in dirs:
            name = item["name"]
            result.append("  " * indent + f"📁 {name}")
            sub_structure = self._build_structure(f"{path}/{name}", indent + 1)
            if sub_structure:
                result.append(sub_structure)

        for item in files:
            name = item["name"]
            file_path = f"{path}/{name}"

            # Get the content of the file
            content = self._get_file_content(file_path)

            # Extract title (first line)
            first_line = content.split("\n")[0] if content else name
            title = first_line.strip("# ")

            # Extract preview (first few paragraphs)
            paragraphs = re.split(r'\n\s*\n', content)
            preview_paragraphs = paragraphs[:3]
            preview = "\n\n".join(preview_paragraphs)

            # Add file entry with title
            result.append("  " * indent + f"📄 {name} - {title}")

            # Add indented preview
            preview_lines = preview.split("\n")
            for line in preview_lines:
                result.append("  " * (indent + 1) + line)

            # Add empty line after preview for better readability
            result.append("")

        return "\n".join(result)

    def get_preview(self, version: str, file_path: str) -> str:
        """
        Get a preview of a documentation file

        Args:
            version: The version of the documentation
            file_path: The path to the file

        Returns:
            A string containing the preview of the file
        """
        try:
            # Normalize the file path
            if not file_path.endswith(".md"):
                file_path += ".md"

            full_path = f"versioned_docs/{version}/{file_path}"
            content = self._get_file_content(full_path)

            # Extract the first few paragraphs (up to 3)
            paragraphs = re.split(r'\n\s*\n', content)
            preview_paragraphs = paragraphs[:3]

            return "\n\n".join(preview_paragraphs)
        except Exception as e:
            logger.exception("Error getting preview")
            return f"Error: {str(e)}"

    def get_full_content(self, version: str, file_path: str) -> str:
        """
        Get the full content of a documentation file

        Args:
            version: The version of the documentation
            file_path: The path to the file

        Returns:
            A string containing the full content of the file
        """
        try:
            # Normalize the file path
            if not file_path.endswith(".md"):
                file_path += ".md"

            full_path = f"versioned_docs/{version}/{file_path}"
            return self._get_file_content(full_path)
        except Exception as e:
            logger.exception("Error getting full content")
            return f"Error: {str(e)}"
