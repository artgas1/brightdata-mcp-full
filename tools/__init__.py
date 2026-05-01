"""brightdata-mcp-full tools package.

Each subpackage corresponds to a Bright Data product group (account_management,
proxy_manager, scrapers, etc.). Each subpackage exports `register_tools(mcp)`
which the server calls during startup based on the GROUPS env var.
"""
