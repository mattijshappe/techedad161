"""Unit test for graceful handling of missing or empty tool results."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent import SampleAgent


@pytest.fixture
def mock_empty_product_tool():
    tool = MagicMock()
    tool.name = "list_a_product_for_api_product_srv"
    tool.description = "Retrieves a list of products."
    tool.arun = AsyncMock(return_value='{"results": []}')
    return tool


@pytest.mark.asyncio
async def test_empty_tool_result_handled_gracefully(mock_empty_product_tool):
    """Test that the agent clearly states when no data is found."""
    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=[mock_empty_product_tool])):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(
                            content=(
                                "No product was found matching 'UNKNOWN-999' in SAP S/4HANA. "
                                "Please verify the product ID and try again."
                            )
                        )
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="What are the details of product UNKNOWN-999?",
                context_id="test-ctx-missing-001",
                tools=[mock_empty_product_tool],
            )

    assert response.status == "completed"
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_partial_data_communicated(mock_empty_product_tool):
    """Test that the agent communicates partial data without fabricating missing fields."""
    mock_empty_product_tool.arun = AsyncMock(
        return_value='{"results": [{"Product": "P-300", "BaseUnit": "EA", "ProductDescription": null}]}'
    )

    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=[mock_empty_product_tool])):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(
                            content=(
                                "Product P-300 was found. Base unit: EA. "
                                "However, the product description is not available in the system."
                            )
                        )
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="What is the description of product P-300?",
                context_id="test-ctx-missing-002",
                tools=[mock_empty_product_tool],
            )

    assert response.status == "completed"
    assert len(response.message) > 0
