"""
tools.py — LLM tool definitions for the Maneuver voice agent.
Written for livekit-agents v1.5.x

Tools serve two purposes:
1. Capture discovery data from the conversation (lead fields)
2. Trigger UI updates on the frontend via LiveKit RPC
"""

import json
import logging
from typing import Annotated
from livekit.agents import function_tool, RunContext

logger = logging.getLogger(__name__)


def build_tools(lead_store: dict, rpc_sender):
    """
    Returns tool functions bound to the shared lead_store and rpc_sender.
    In v1.x, tools are plain async functions decorated with @function_tool.
    """

    @function_tool(
        description=(
            "Call this whenever you learn something about the person — "
            "their name, company, role, the problem they're solving, "
            "their timeline, or their budget. Call immediately as you learn it."
        )
    )
    async def update_lead_field(
        context: RunContext,
        field: Annotated[
            str,
            "One of: name, company, role, problem, solution, timeline, budget, notes",
        ],
        value: Annotated[str, "The value to store for that field"],
    ) -> str:
        """Store a piece of discovery information captured from the conversation."""
        lead_store[field] = value
        logger.info(f"Lead field updated: {field} = {value}")
        await rpc_sender("update_lead_field", {"field": field, "value": value})
        return f"Noted: {field} is {value}"

    @function_tool(
        description=(
            "Call this when the user asks about Maneuver's services or what we offer. "
            "Triggers the services card on their screen."
        )
    )
    async def show_services_slide(context: RunContext) -> str:
        """Display the services overview card on the frontend."""
        await rpc_sender("show_slide", {"slide": "services"})
        return "Services slide is now visible to the user."

    @function_tool(
        description=(
            "Call this when the user asks about Maneuver's pricing or cost."
        )
    )
    async def show_pricing_slide(context: RunContext) -> str:
        """Display the pricing card on the frontend."""
        await rpc_sender("show_slide", {"slide": "pricing"})
        return "Pricing slide is now visible to the user."

    @function_tool(
        description=(
            "Call this when the user asks about Maneuver's process or how engagements work."
        )
    )
    async def show_process_slide(context: RunContext) -> str:
        """Display the process card on the frontend."""
        await rpc_sender("show_slide", {"slide": "process"})
        return "Process slide is now visible to the user."

    @function_tool(
        description=(
            "Call this when the user asks about case studies, past work, or client results."
        )
    )
    async def show_case_studies_slide(context: RunContext) -> str:
        """Display the case studies card on the frontend."""
        await rpc_sender("show_slide", {"slide": "case_studies"})
        return "Case studies slide is now visible to the user."

    @function_tool(
        description=(
            "Call this when the user asks about the team or who they would work with."
        )
    )
    async def show_team_slide(context: RunContext) -> str:
        """Display the team card on the frontend."""
        await rpc_sender("show_slide", {"slide": "team"})
        return "Team slide is now visible to the user."

    @function_tool(
        description=(
            "Call this when the discovery conversation is complete and the call is wrapping up. "
            "Saves the lead record and notifies the system."
        )
    )
    async def finalize_lead(
        context: RunContext,
        summary: Annotated[
            str,
            "A 2-3 sentence summary of the conversation and what was discussed",
        ],
    ) -> str:
        """Mark the lead as complete and save final data."""
        lead_store["summary"] = summary
        lead_store["status"] = "completed"
        await rpc_sender("lead_finalized", {"lead": lead_store, "summary": summary})
        logger.info(f"Lead finalized: {json.dumps(lead_store, indent=2)}")
        return "Lead has been saved. Great conversation!"

    return [
        update_lead_field,
        show_services_slide,
        show_pricing_slide,
        show_process_slide,
        show_case_studies_slide,
        show_team_slide,
        finalize_lead,
    ]