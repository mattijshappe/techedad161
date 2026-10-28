"""MCP tools indirection layer.

This module is the owned indirection layer for MCP tool loading.
Import `get_mcp_tools` from here — never directly from sap_cloud_sdk.agentgateway.
The test fixture patches this module to return mock tools when IBD_TESTING=1.
"""
from mcp_providers.agw import get_mcp_tools

__all__ = ["get_mcp_tools"]
