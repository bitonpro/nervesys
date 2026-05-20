# Sentinel LibreChat Integration

To connect the Sentinel MCP to your LibreChat instance:

1. Navigate to your LibreChat interface.
2. Select "Add MCP Server" (הוסף שרת MCP).
3. **Name**: Sentinel MCP
4. **Link to MCP Server**: The public or Tailscale IP/URL of your `gama-2` node (e.g., `https://aster-gama2.yohayai.com/` or the specific MCP port endpoint).
5. **Transport**: `SSE` (Server-Sent Events) is recommended for real-time device updates.
6. **Authentication**: Configure OAuth or API keys as dictated by your `token_manager.py` layer.

*Note: The system integrates with Google AI Studio (project `gen-lang-client-0969817112`).*
