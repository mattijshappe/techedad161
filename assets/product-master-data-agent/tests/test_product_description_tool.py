"""Unit test for product description and specification tool."""
import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent import SampleAgent, AgentResponse


@pytest.fixture
def mock_product_tool():
    """Create a mock product description tool."""
    tool = MagicMock()
    tool.name = "list_a_productdescription_for_api_product_srv"
    tool.description = "Retrieves product descriptions."
    tool.arun = AsyncMock(
        return_value='{"results": [{"Product": "P-100", "Language": "EN", "ProductDescription": "Industrial Pump Model A"}]}'
    )
    return tool


@pytest.mark.asyncio
async def test_product_description_query(mock_product_tool):
    """Test that the agent answers product description queries using the mock tool."""
    agent = SampleAgent()

    with patch("agent.get_mcp_tools", new=AsyncMock(return_value=[mock_product_tool])):
        with patch("agent.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(content="P-100 is the Industrial Pump Model A.")
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="What is the description of product P-100?",
                context_id="test-ctx-001",
                tools=[mock_product_tool],
            )

    assert response.status == "completed"
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_product_spec_milestone_logging(mock_product_tool, caplog):
    """Test that M1.achieved is logged on a successful spec query."""
    agent = SampleAgent()

    with patch("agent.get_mcp_tools", new=AsyncMock(return_value=[mock_product_tool])):
        with patch("agent.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(content="P-100 specs: flow rate 500 L/min, pressure 16 bar.")
                    ]
                }
            )
            mock_create.return_value = mock_graph

            with caplog.at_level(logging.INFO, logger="agent"):
                await agent.invoke(
                    query="What are the specifications of product P-100?",
                    context_id="test-ctx-002",
                    tools=[mock_product_tool],
                )

    assert any("M1.achieved" in record.message for record in caplog.records)
