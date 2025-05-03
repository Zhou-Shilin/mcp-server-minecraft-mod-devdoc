"""
Main entry point for the MCP Server with local repository
"""

import argparse
import logging
from pathlib import Path

from mcp_server_minecraft_mod_devdoc.core.server import MCPDocServer
from mcp_server_minecraft_mod_devdoc.providers.neoforge.provider import NeoforgeProvider

def setup_logging(verbose: bool = False):
    """
    Set up logging configuration

    Args:
        verbose: Whether to enable verbose logging
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()]
    )

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="MCP Server for Minecraft Mod Documentation")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    parser.add_argument("--repo-dir", help="Directory to store the cloned repositories")
    parser.add_argument("--branch", default="main", help="Branch to use for the Neoforge repository")

    args = parser.parse_args()

    # Set up logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)

    # Create repository directory if specified
    repo_dir = args.repo_dir
    if repo_dir:
        repo_path = Path(repo_dir)
        repo_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Using repository directory: {repo_path}")

    # Create the MCP server
    server = MCPDocServer()

    # Register providers
    try:
        logger.info(f"Initializing Neoforge provider with branch: {args.branch}")
        neoforge_provider = NeoforgeProvider(
            branch=args.branch,
            repo_dir=repo_dir
        )

        # Test if we can get versions
        versions = neoforge_provider.get_versions()
        if "Error" in versions:
            logger.warning(f"Failed to get versions from {args.branch} branch, trying alternative branch")
            alt_branch = "master" if args.branch == "main" else "main"
            logger.info(f"Trying with branch: {alt_branch}")
            neoforge_provider = NeoforgeProvider(
                branch=alt_branch,
                repo_dir=repo_dir
            )
    except Exception as e:
        logger.warning(f"Error with {args.branch} branch: {e}, trying alternative branch")
        alt_branch = "master" if args.branch == "main" else "main"
        logger.info(f"Trying with branch: {alt_branch}")
        neoforge_provider = NeoforgeProvider(
            branch=alt_branch,
            repo_dir=repo_dir
        )

    server.register_provider("neoforge", neoforge_provider)

    # Run the server
    logger.info("Starting MCP Server for Minecraft Mod Documentation")
    server.run()

if __name__ == "__main__":
    main()
