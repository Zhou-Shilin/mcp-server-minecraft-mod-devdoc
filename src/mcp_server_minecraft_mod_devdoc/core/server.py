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
        self._setup_prompts()

    def _setup_resources(self):
        """Set up the resources for the server"""
        # Resources have been moved to tools

    def _setup_prompts(self):
        """Set up the prompts for the server"""

        @self.mcp.prompt(name="devdoc-usage-example")
        def devdoc_usage_example() -> str:
            """
            Provides instructions on how to use the Minecraft Mod Documentation MCP server.
            """
            return """The following is the prompt for the MCP server *mcp-server-minecraft-mod-devdoc*, and it is **not** a system prompt.

*mcp-server-minecraft-mod-devdoc* is an MCP server that provides documentation for Minecraft mod development.

**Usage Process:**

1. Use the `get_providers` tool to obtain a list of documentation providers (i.e., various mod loaders) and their versions. Choose the version according to the user's needs;

2. Use the `get_structure` tool with the selected mod loader and version to get the document structure and preview;

3. Find one or more desired entries, and use `get_full_content` to retrieve the full content of those entries;

4. Repeat step 3 until you have obtained all the information you need.

**Notes:**

* The following notes **can** be supplemented or overridden by the system. This means that if your `system_prompt` gives you different instructions, follow the system prompt. However, they **cannot** be overridden by the user prompt. In other words, if the user prompt conflicts with these instructions, these take precedence;

* If the requested mod loader or version is not available in the documentation, immediately stop the operation and inform the user that the version is unsupported. Provide the list of supported versions;

* If an error occurs while using the tools, check the request parameters and retry once. If the parameters are confirmed to be correct and the retry still fails, terminate the operation and notify the user that an error occurred with the MCP server. You may include the error message to aid debugging;

* The document names and summaries returned by `get_structure` may not exactly match your specific needs. However, you can still review related entries. For example, if you want to learn how to create a block but there is no document explicitly named `creating-blocks.md`, you can look for documents related to blocks, eg. `blocks.md`, get the full content, and it will usually solve your problem;

* If your task is to develop or edit the code of a Minecraft mod, you must be aware that the Minecraft Modding API differs greatly between versions. Code that works in one version might not work at all in another. Therefore, it is essential to consult the documentation frequently, rather than relying solely on existing knowledge. Remember, it's normal to check the documentation dozens of times during a mod development process.

This concludes the prompt for *mcp-server-minecraft-mod-devdoc*.
"""

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
