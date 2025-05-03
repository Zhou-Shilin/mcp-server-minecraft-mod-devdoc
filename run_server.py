"""
Run the MCP Server with local repository
"""

import logging
import argparse
import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server_minecraft_mod_devdoc.core.server import MCPDocServer
from mcp_server_minecraft_mod_devdoc.providers.neoforge.provider import NeoforgeProvider

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Create the MCP server - this needs to be at module level for MCP CLI
server = MCPDocServer()

# Default values
DEFAULT_BRANCH = "main"
DEFAULT_REPO_DIR = os.path.join(str(Path.home()), ".local", "share", "mcp-server-minecraft-mod-devdoc", "neoforge")

# Initialize with default values first
repo_dir = DEFAULT_REPO_DIR
branch = DEFAULT_BRANCH

# Check for environment variables
if "MCP_REPO_DIR" in os.environ:
    repo_dir = os.environ["MCP_REPO_DIR"]
if "MCP_BRANCH" in os.environ:
    branch = os.environ["MCP_BRANCH"]

# Initialize provider with default values
try:
    logger.info(f"Initializing Neoforge provider with branch: {branch}")
    neoforge_provider = NeoforgeProvider(
        branch=branch,
        repo_dir=repo_dir
    )

    # Test if we can get versions
    versions = neoforge_provider.get_versions()
    if "Error" in versions:
        logger.warning(f"Failed to get versions from {branch} branch, trying alternative branch")
        alt_branch = "master" if branch == "main" else "main"
        logger.info(f"Trying with branch: {alt_branch}")
        neoforge_provider = NeoforgeProvider(
            branch=alt_branch,
            repo_dir=repo_dir
        )
except Exception as e:
    logger.warning(f"Error with {branch} branch: {e}, trying alternative branch")
    alt_branch = "master" if branch == "main" else "main"
    logger.info(f"Trying with branch: {alt_branch}")
    neoforge_provider = NeoforgeProvider(
        branch=alt_branch,
        repo_dir=repo_dir
    )

# Register the provider
server.register_provider("neoforge", neoforge_provider)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="MCP Server for Minecraft Mod Documentation")
    parser.add_argument("--repo-dir", help="Directory to store the cloned repositories")
    parser.add_argument("--branch", default="main", help="Branch to use for the Neoforge repository")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging")
    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Override with command line arguments if provided
    global repo_dir, branch, neoforge_provider
    if args.repo_dir:
        repo_dir = args.repo_dir
    if args.branch:
        branch = args.branch

    # Reinitialize provider if command line arguments were provided
    if args.repo_dir or args.branch:
        try:
            logger.info(f"Reinitializing Neoforge provider with branch: {branch}")
            neoforge_provider = NeoforgeProvider(
                branch=branch,
                repo_dir=repo_dir
            )
            server.register_provider("neoforge", neoforge_provider)
        except Exception as e:
            logger.error(f"Error reinitializing provider: {e}")

    # Run the server
    logger.info("Starting MCP Server for Minecraft Mod Documentation")
    server.run()

if __name__ == "__main__":
    main()
