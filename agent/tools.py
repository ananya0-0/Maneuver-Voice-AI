"""
tools.py — LLM tool definitions for the Maneuver voice agent.

Tools serve two purposes:
1. Capture discovery data from the conversation (lead fields)
2. Trigger UI updates on the frontend via LiveKit RPC
"""

import json
import asyncio
import logging
from typing import Annotated
from livekit.agents import llm

logger = logging.getLogger(__name__)


def build_tools(lead_store: dict, rpc_sender) -> list:
    """
    Returns a list of FunctionTool instances.
    lead_store: shared dict that accumulates lead data
    rpc_sender: async callable(method: str, payload: dict) → sends RPC to frontend
    """

    @llm.ai_callable(
        description=(
            "Call this whenever you learn something about the person you're talking to — "
            "their name, company, what they're building, the problem they're solving, "
            "their timeline, or their budget. Call it as soon as you have the information; "
            "don't wait until the end of the call."
        )
    )
    async def update_lead_field(
        field: Annotated[
            str,
            llm.TypeInfo(
                description=(
                    "One of: name, company, role, problem, solution, timeline, budget, notes"
                )
            ),
        ],
        value: Annotated[str, llm.TypeInfo(description="The value to store for that field")],
    ):
        """Store a piece of discovery information captured from the conversation."""
        lead_store[field] = value
        logger.info(f"Lead field updated: {field} = {value}")
        await rpc_sender("update_lead_field", {"field": field, "value": value})
        return f"Noted: {field} is {value}"

    @llm.ai_callable(
        description=(
            "Call this when the user asks about Maneuver's services or what we offer. "
            "This triggers the services overview card on the user's screen."
        )
    )
    async def show_services_slide():
        """Display the services overview card on the frontend."""
        await rpc_sender("show_slide", {"slide": "services"})
        return "Services slide is now visible to the user."

    @llm.ai_callable(
        description=(
            "Call this when the user asks about Maneuver's pricing or cost. "
            "This triggers the pricing card on the user's screen."
        )
    )
    async def show_pricing_slide():
        """Display the pricing card on the frontend."""
        await rpc_sender("show_slide", {"slide": "pricing"})
        return "Pricing slide is now visible to the user."

    @llm.ai_callable(
        description=(
            "Call this when the user asks about Maneuver's process, how we work, "
            "or what the engagement looks like step by step."
        )
    )
    async def show_process_slide():
        """Display the process/workflow card on the frontend."""
        await rpc_sender("show_slide", {"slide": "process"})
        return "Process slide is now visible to the user."

    @llm.ai_callable(
        description=(
            "Call this when the user asks about case studies, past work, or clients."
        )
    )
    async def show_case_studies_slide():
        """Display the case studies card on the frontend."""
        await rpc_sender("show_slide", {"slide": "case_studies"})
        return "Case studies slide is now visible to the user."

    @llm.ai_callable(
        description=(
            "Call this when the user asks about the team, who works at Maneuver, "
            "or who they would be working with."
        )
    )
    async def show_team_slide():
        """Display the team card on the frontend."""
        await rpc_sender("show_slide", {"slide": "team"})
        return "Team slide is now visible to the user."

    @llm.ai_callable(
        description=(
            "Call this when the discovery conversation is complete and the user seems "
            "ready to schedule a follow-up, or when the call is wrapping up naturally. "
            "This saves the final lead record and notifies the system."
        )
    )
    async def finalize_lead(
        summary: Annotated[
            str,
            llm.TypeInfo(
                description="A 2-3 sentence summary of the conversation and what was discussed"
            ),
        ],
    ):
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
