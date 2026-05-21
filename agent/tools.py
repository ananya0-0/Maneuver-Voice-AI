"""
tools.py — LLM tool definitions for the Maneuver voice agent.

Tools serve two purposes:
1. Capture discovery data from the conversation (lead fields)
2. Trigger UI updates on the frontend via LiveKit RPC
"""

import json
import logging
from typing import Literal
from livekit.agents import FunctionContext, function_tool

logger = logging.getLogger(__name__)


class ManeuverAgentTools(FunctionContext):
    """
    A container context class holding tools accessible by the LiveKit AI Agent.
    """
    def __init__(self, lead_store: dict, rpc_sender):
        super().__init__()
        self.lead_store = lead_store
        self.rpc_sender = rpc_sender

    @function_tool
    async def update_lead_field(
        self,
        field: Literal["name", "company", "role", "problem", "solution", "timeline", "budget", "notes"],
        value: str
    ) -> str:
        """
        Call this whenever you learn something about the person you're talking to — 
        their name, company, what they're building, the problem they're solving, 
        their timeline, or their budget. Call it as soon as you have the information; 
        don't wait until the end of the call.

        Args:
            field: The category of discovery information to store.
            value: The content details provided by the user.
        """
        self.lead_store[field] = value
        logger.info(f"Lead field updated: {field} = {value}")
        
        # Forward state change immediately to the React frontend UI
        await self.rpc_sender("update_lead_field", {"field": field, "value": value})
        return f"Noted: {field} is {value}"

    @function_tool
    async def show_services_slide(self) -> str:
        """
        Call this when the user asks about Maneuver's services or what we offer. 
        This triggers the services overview card on the user's screen.
        """
        await self.rpc_sender("show_slide", {"slide": "services"})
        return "Services slide is now visible to the user."

    @function_tool
    async def show_pricing_slide(self) -> str:
        """
        Call this when the user asks about Maneuver's pricing or cost. 
        This triggers the pricing card on the user's screen.
        """
        await self.rpc_sender("show_slide", {"slide": "pricing"})
        return "Pricing slide is now visible to the user."

    @function_tool
    async def show_process_slide(self) -> str:
        """
        Call this when the user asks about Maneuver's process, how we work, 
        or what the engagement looks like step by step.
        """
        await self.rpc_sender("show_slide", {"slide": "process"})
        return "Process slide is now visible to the user."

    @function_tool
    async def show_case_studies_slide(self) -> str:
        """
        Call this when the user asks about case studies, past work, or clients.
        """
        await self.rpc_sender("show_slide", {"slide": "case_studies"})
        return "Case studies slide is now visible to the user."

    @function_tool
    async def show_team_slide(self) -> str:
        """
        Call this when the user asks about the team, who works at Maneuver, 
        or who they would be working with.
        """
        await self.rpc_sender("show_slide", {"slide": "team"})
        return "Team slide is now visible to the user."

    @function_tool
    async def finalize_lead(self, summary: str) -> str:
        """
        Call this when the discovery conversation is complete and the user seems 
        ready to schedule a follow-up, or when the call is wrapping up naturally. 
        This saves the final lead record and notifies the system.

        Args:
            summary: A 2-3 sentence summary of the conversation and what was discussed.
        """
        self.lead_store["summary"] = summary
        self.lead_store["status"] = "completed"
        await self.rpc_sender("lead_finalized", {"lead": self.lead_store, "summary": summary})
        logger.info(f"Lead finalized: {json.dumps(self.lead_store, indent=2)}")
        return "Lead has been saved. Great conversation!"