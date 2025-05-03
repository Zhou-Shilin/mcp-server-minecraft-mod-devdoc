"""
MCP Server implementation for Minecraft Mod Documentation
"""

from mcp.server.fastmcp import FastMCP, Context
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class MCPDocServer:
    """
    MCP Server for Minecraft Mod Documentation
    """

    def __init__(self, name: str = "Minecraft Mod Documentation"):
        """
        Initialize the MCP Server

        Args:
            name: The name of the server
        """
        self.mcp = FastMCP(name)
        self.providers = {}
        self._setup_resources()
        self._setup_tools()

    def _setup_resources(self):
        """Set up the resources for the server"""
        # Resources have been moved to tools

    def _setup_tools(self):
        """Set up the tools for the server"""

        @self.mcp.tool()
        def get_providers() -> str:
            """
            Get a list of available documentation providers and their versions

            Returns:
                A formatted string with providers and their versions
            """
            result = []

            for provider_name in self.providers.keys():
                result.append(f"## {provider_name}")

                # Get versions for this provider
                try:
                    versions = self.providers[provider_name].get_versions()
                    if not versions.startswith("Error") and not versions.startswith("No versions"):
                        result.append("\n**Available versions:**\n")
                        for version in versions.split("\n"):
                            result.append(f"- {version}")
                    else:
                        result.append(f"\n{versions}")
                except Exception as e:
                    result.append(f"\nError getting versions: {str(e)}")

                result.append("\n")  # Add empty line between providers

            if not result:
                return "No documentation providers registered."

            return "\n".join(result)

        @self.mcp.tool()
        def get_structure(provider: str, version: str) -> str:
            """
            Get the file structure with previews for a specific version of documentation

            Args:
                provider: The documentation provider (e.g., neoforge, fabric)
                version: The version of the documentation
            """
            if provider not in self.providers:
                return f"Error: Provider '{provider}' not found. Available providers: {', '.join(self.providers.keys())}"

            return self.providers[provider].get_structure(version)

        @self.mcp.tool()
        def get_full_content(provider: str, version: str, file_path: str) -> str:
            """
            Get the full content of a documentation file

            Args:
                provider: The documentation provider (e.g., neoforge, fabric)
                version: The version of the documentation
                file_path: The path to the file
            """
            if provider not in self.providers:
                return f"Error: Provider '{provider}' not found. Available providers: {', '.join(self.providers.keys())}"

            return self.providers[provider].get_full_content(version, file_path)

    def register_provider(self, name: str, provider):
        """
        Register a documentation provider

        Args:
            name: The name of the provider
            provider: The provider instance
        """
        self.providers[name] = provider
        logger.info(f"Registered provider: {name}")

    def run(self):
        """Run the MCP server"""
        self.mcp.run()
