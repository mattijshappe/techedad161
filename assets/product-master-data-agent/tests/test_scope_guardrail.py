"""Unit test for out-of-scope query guardrail (pricing, stock)."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent import SampleAgent


@pytest.mark.asyncio
async def test_pricing_query_rejected():
    """Test that the agent declines pricing queries as out of scope."""
    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=[])):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(
                            content=(
                                "I'm sorry, but pricing information is outside my scope. "
                                "I can only answer questions about product descriptions, "
                                "specifications, units of measure, packaging, and classifications."
                            )
                        )
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="What is the price of product P-100?",
                context_id="test-ctx-scope-001",
                tools=[],
            )

    assert response.status == "completed"
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_stock_query_rejected():
    """Test that the agent declines stock availability queries as out of scope."""
    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=[])):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(
                            content=(
                                "Stock availability is outside my scope. "
                                "I focus on product master data such as descriptions and specifications."
                            )
                        )
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="How much stock do we have for product P-100?",
                context_id="test-ctx-scope-002",
                tools=[],
            )

    assert response.status == "completed"
    assert len(response.message) > 0
