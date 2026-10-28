"""Unit test for product classification lookup tool."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent import SampleAgent


@pytest.fixture
def mock_classification_tool():
    tool = MagicMock()
    tool.name = "list_a_productclass_for_api_clfn_product_srv"
    tool.description = "Retrieves class assignments for products."
    tool.arun = AsyncMock(
        return_value='{"results": [{"Product": "P-100", "ClassType": "001", "ClassName": "PUMPS"}]}'
    )
    return tool


@pytest.mark.asyncio
async def test_classification_query(mock_classification_tool):
    """Test that the agent retrieves product classification data."""
    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=[mock_classification_tool])):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(content="P-100 belongs to the PUMPS class (Class Type 001).")
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="What category does product P-100 belong to?",
                context_id="test-ctx-clf-001",
                tools=[mock_classification_tool],
            )

    assert response.status == "completed"
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_classification_no_data(mock_classification_tool):
    """Test that the agent handles products with no classification data gracefully."""
    mock_classification_tool.arun = AsyncMock(return_value='{"results": []}')

    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=[mock_classification_tool])):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(
                            content="No classification data was found for product P-999 in SAP S/4HANA."
                        )
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="What category does product P-999 belong to?",
                context_id="test-ctx-clf-002",
                tools=[mock_classification_tool],
            )

    assert response.status == "completed"
    assert "No classification" in response.message or len(response.message) > 0
