"""
Main agent entry point for ADK web interface.

This file exports the main weather team agent that coordinates
all the specialized sub-agents in the system.
"""

from agents.weather_team.agent import weather_team_agent

# Export the main agent for ADK web interface as 'agent'
agent = weather_team_agent
__all__ = ['agent'] 