# MCP Server for Minecraft Mod Documentation

[![Apache License 2.0](https://img.shields.io/badge/License-Apache-green.svg)](https://choosealicense.com/licenses/apache-2.0/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

这是一个基于 Model Context Protocol (MCP) 的服务器，用于查看 Minecraft 模组开发文档。目前支持 Neoforge 文档，并设计为可扩展以支持其他文档源（如 Fabric）。

## 功能

该MCP服务器提供以下功能：

1. **获取提供者和版本列表**：列出所有可用的文档提供者及其版本（例如，Neoforge的`version-1.20.4`, `version-1.20.6`, `version-1.21.1`等）。
2. **获取文件结构和预览**：查看指定版本的文档文件结构，包括目录和文件，同时显示每个文件的前几段内容作为预览。
3. **获取完整内容**：获取文档文件的完整内容。

服务器会自动管理本地仓库，只在必要时（首次使用或上次更新超过24小时）更新仓库内容。

### 与MCP客户端集成

该服务器实现了MCP协议，可以与支持MCP的客户端（如 Claude Desktop、VS Code 等）集成。

#### 客户端配置示例

在支持MCP的客户端中，可以使用以下配置：

```json
{
  "mcpServers": {
    "mcp-server-minecraft-mod-devdoc": {
      "command": "uv",
      "args": [
        "--directory", "${MCP_SERVER_PATH}",
        "run", "--with", "mcp", "mcp", "run", "run_server.py"
      ]
    }
  }
}
```

这将使用uv运行服务器，并通过MCP协议与客户端通信。`${MCP_SERVER_PATH}`变量应被替换为服务器的安装路径。

#### 推荐提示词

推荐使用这个提示词搭配本服务：

```markdown
The following is the prompt for the MCP server *mcp-server-minecraft-mod-devdoc*, and it is **not** a system prompt.

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
```

## 项目结构

```
src/
├── mcp_server_minecraft_mod_devdoc/
│   ├── __init__.py
│   ├── main.py                 # 主入口点
│   ├── core/
│   │   ├── __init__.py
│   │   ├── server.py           # MCP服务器实现
│   │   └── provider.py         # 文档提供者接口
│   └── providers/
│       ├── __init__.py
│       ├── neoforge/           # Neoforge文档提供者
│       │   ├── __init__.py
│       │   └── provider.py
│       └── fabric/             # Fabric文档提供者（未来扩展）
│           ├── __init__.py
│           └── provider.py
└── __main__.py                 # 命令行入口点
```

## 扩展

### 添加新的文档提供者

要添加新的文档提供者（如Fabric），请按照以下步骤操作：

1. 在`src/mcp_server_minecraft_mod_devdoc/providers/`目录下创建新的提供者类，实现`DocProvider`接口
2. 在`src/mcp_server_minecraft_mod_devdoc/main.py`中注册新的提供者

例如：

```python
# 创建Fabric提供者
fabric_provider = FabricProvider(repo_dir=repo_dir, branch="main")
server.register_provider("fabric", fabric_provider)
```

## 故障排除

### 无法获取文档内容

如果遇到"Error: Failed to read file content"错误，可能是由于以下原因：

1. **Git问题**：确保您的计算机已安装Git并可以正常使用
2. **仓库克隆问题**：检查仓库目录（默认为`~/.local/share/mcp-server-minecraft-mod-devdoc/neoforge`）是否存在并包含正确的内容
3. **仓库分支问题**：默认情况下，服务器会尝试从main分支获取内容，如果失败会尝试master分支
4. **权限问题**：确保您有权限读取仓库目录中的文件

### 服务器无法启动

如果服务器无法启动，可能是由于以下原因：

1. **依赖问题**：确保已安装所有必要的依赖（`pip install -r requirements.txt`）
2. **端口冲突**：MCP服务器默认使用特定端口，确保这些端口未被其他应用程序占用

## 贡献

欢迎贡献！如果您想为这个项目做出贡献，请遵循以下步骤：

1. Fork 这个仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个 Pull Request

## 依赖

本项目使用以下主要依赖：

- [MCP](https://github.com/modelcontextprotocol/python-sdk) - Model Context Protocol 实现
- [aiohttp](https://docs.aiohttp.org/) - 异步 HTTP 客户端/服务器
- [uvicorn](https://www.uvicorn.org/) - ASGI 服务器

完整的依赖列表请参见 `requirements.txt` 或 `pyproject.toml`。

## 许可证

[Apache License 2.0](LICENSE) - 查看 LICENSE 文件了解更多详情。
