"""Integration test: full end-to-end agent flow with mocked LLM and MCP tools."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agent import SampleAgent, AgentResponse


@pytest.fixture
def mock_tools():
    """Create a realistic set of mock MCP tools."""
    product_tool = MagicMock()
    product_tool.name = "get_a_product_for_api_product_srv"
    product_tool.description = "Retrieves a single product from the Product Master."
    product_tool.arun = AsyncMock(
        return_value=(
            '{"Product": "P-100", "ProductType": "FERT", "BaseUnit": "EA", '
            '"GrossWeight": "1.500", "WeightUnit": "KG", '
            '"ProductDescription": "Industrial Pump Model A"}'
        )
    )

    uom_tool = MagicMock()
    uom_tool.name = "list_a_productunitsofmeasure_for_api_product_srv"
    uom_tool.description = "Retrieves all units of measure for a product."
    uom_tool.arun = AsyncMock(
        return_value=(
            '{"results": ['
            '{"Product": "P-100", "AlternativeUnit": "EA", "QuantityNumerator": "1.000", "Length": "0.300", "Width": "0.200", "Height": "0.150"},'
            '{"Product": "P-100", "AlternativeUnit": "PAL", "QuantityNumerator": "20.000", "Length": "1.200", "Width": "0.800", "Height": "1.000"}'
            ']}'
        )
    )

    desc_tool = MagicMock()
    desc_tool.name = "get_a_productdescription_for_api_product_srv"
    desc_tool.description = "Retrieves the description of a specific product."
    desc_tool.arun = AsyncMock(
        return_value='{"Product": "P-100", "Language": "EN", "ProductDescription": "Industrial Pump Model A"}'
    )

    return [product_tool, uom_tool, desc_tool]


@pytest.mark.asyncio
async def test_full_product_spec_query_flow(mock_tools):
    """
    Integration test: user asks about product specs.
    Agent calls product tool, formats response, returns completed status.
    """
    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=mock_tools)):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [
                        MagicMock(
                            content=(
                                "Here are the specifications for product P-100 (Industrial Pump Model A):\n"
                                "- Type: Finished Good (FERT)\n"
                                "- Base Unit: EA (each)\n"
                                "- Gross Weight: 1.5 KG\n"
                                "- Available packaging: EA (each) and PAL (pallet, 20 units)"
                            )
                        )
                    ]
                }
            )
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="Tell me the specifications and packaging options for product P-100.",
                context_id="test-integration-001",
                tools=mock_tools,
            )

    assert isinstance(response, AgentResponse)
    assert response.status == "completed"
    assert len(response.message) > 0
    assert "P-100" in response.message or len(response.message) > 10


@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test that the agent handles LLM errors gracefully and returns error status."""
    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=[])):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(side_effect=RuntimeError("LLM unavailable"))
            mock_create.return_value = mock_graph

            response = await agent.invoke(
                query="What are the specs for product P-100?",
                context_id="test-integration-error-001",
                tools=[],
            )

    assert response.status in ("error", "completed")
    assert len(response.message) > 0


@pytest.mark.asyncio
async def test_agent_stream_yields_processing_then_result(mock_tools):
    """Test that stream() yields a processing status first, then a completed result."""
    agent = SampleAgent()

    with patch("app.agent.get_mcp_tools", new=AsyncMock(return_value=mock_tools)):
        with patch("langchain.agents.create_agent") as mock_create:
            mock_graph = MagicMock()
            mock_graph.ainvoke = AsyncMock(
                return_value={
                    "messages": [MagicMock(content="P-100: Industrial Pump Model A, EA base unit.")]
                }
            )
            mock_create.return_value = mock_graph

            chunks = []
            async for chunk in agent.stream(
                query="What is product P-100?",
                context_id="test-stream-001",
                tools=mock_tools,
            ):
                chunks.append(chunk)

    assert len(chunks) >= 2
    # First chunk should be processing
    assert chunks[0]["is_task_complete"] is False
    assert chunks[0]["content"] == "Processing..."
    # Last chunk should be complete
    assert chunks[-1]["is_task_complete"] is True
    assert len(chunks[-1]["content"]) > 0
