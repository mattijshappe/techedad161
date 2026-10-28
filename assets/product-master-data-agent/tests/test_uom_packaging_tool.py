"""Unit test for unit of measure and packaging tool."""
import logging
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent import SampleAgent


@pytest.fixture
def mock_uom_tool():
    tool = MagicMock()
    tool.name = "list_a_productunitsofmeasure_for_api_product_srv"
    tool.description = "Retrieves units of measure for products."
    tool.arun = AsyncMock(
        return_value='{"results": [{"Product": "P-100", "AlternativeUnit": "EA", "QuantityNumerator": "1.000"}, {"Product": "P-100", "AlternativeUnit": "PAL", "QuantityNumerator": "20.000"}]}'
    )
    return tool


@pytest.mark.asyncio
async def test_uom_query_returns_packaging_info(mock_uom_tool):
    """Test that the agent handles UoM/packaging queries."""
    agent = SampleAgent()

    with patch("agent.get_mcp_tools", new=AsyncMock(return_value=[mock_uom_tool])):
        with patch("agent.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(content="P-100 is available as EA (each) and PAL (pallet, 20 units).")
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="What packaging options are available for product P-100?",
                context_id="test-ctx-uom-001",
                tools=[mock_uom_tool],
            )

    assert response.status == "completed"
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_uom_milestone_logging(mock_uom_tool, caplog):
    """Test that M2.achieved is logged on a successful UoM query."""
    agent = SampleAgent()

    with patch("agent.get_mcp_tools", new=AsyncMock(return_value=[mock_uom_tool])):
        with patch("agent.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [MagicMock(content="P-100 unit of measure is EA.")]
                }
            )
            mock_create.return_value = mock_graph

            with caplog.at_level(logging.INFO, logger="agent"):
                await agent.invoke(
                    query="What is the unit of measure for product P-100?",
                    context_id="test-ctx-uom-002",
                    tools=[mock_uom_tool],
                )

    assert any("M2.achieved" in record.message for record in caplog.records)
