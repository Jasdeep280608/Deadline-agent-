"""
Deadline Agent - built for the AWS "Agents for Humans" hackathon.

Theme: an agent that runs in the background and only surfaces when
there's a real decision to make - instead of another app you have to
open and check yourself.

Two ways to run it:
  python agent.py chat        -> talk to it interactively
  python agent.py watch       -> run it in "autonomous" mode: it checks
                                  your deadlines on its own and only
                                  prints something when action is needed
"""

import os
import sys
import time

from strands import Agent
from strands.models.gemini import GeminiModel
from tools import get_upcoming_deadlines, add_deadline, get_most_urgent

# Using Gemini instead of the default Bedrock provider - no AWS account or
# card required, just a free API key from https://aistudio.google.com/apikey
# Set it as an environment variable before running:
#   export GEMINI_API_KEY=your_key_here      (Windows: set GEMINI_API_KEY=...)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable not set. "
        "Get a free key at https://aistudio.google.com/apikey and set it with:\n"
        "  export GEMINI_API_KEY=your_key_here"
    )

MODEL = GeminiModel(
    client_args={"api_key": GEMINI_API_KEY},
    model_id="gemini-3.6-flash",
    params={"temperature": 0.3},
)

# To switch back to AWS Bedrock later, replace MODEL above with:
#   from strands.models import BedrockModel
#   MODEL = BedrockModel(model_id="us.amazon.nova-pro-v1:0")
# and remove the Gemini setup - everything else in this file stays the same.

SYSTEM_PROMPT = """You are a calm, no-nonsense deadline assistant for a
college student. You have tools to check upcoming deadlines, add new
ones, and check what's currently urgent.

Rules:
- Don't nag about things that aren't actually close (respect the
  threshold given by tools).
- When something is urgent, be direct and specific: what it is, when
  it's due, and one clear next action.
- When nothing is urgent, say so briefly - don't invent urgency.
- Keep responses short. This is a background assistant, not a chatbot
  the user wants to have a long conversation with.
"""


def build_agent() -> Agent:
    return Agent(
        model=MODEL,
        system_prompt=SYSTEM_PROMPT,
        tools=[get_upcoming_deadlines, add_deadline, get_most_urgent],
    )


def chat_mode():
    agent = build_agent()
    print("Deadline Agent (chat mode). Type 'exit' to quit.\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("exit", "quit"):
            break
        response = agent(user_input)
        print(f"\nAgent: {response}\n")


def watch_mode(poll_seconds: int = 60, urgency_threshold_hours: int = 48):
    """
    This is the 'autonomous' behavior the hackathon theme is looking for:
    the agent checks on its own, on a schedule, and only speaks up when
    there's something worth interrupting the user for.
    """
    agent = build_agent()
    print(
        f"Deadline Agent (watch mode). Checking every {poll_seconds}s, "
        f"alerting on anything due within {urgency_threshold_hours}h.\n"
        "Press Ctrl+C to stop.\n"
    )
    try:
        while True:
            result = get_most_urgent(threshold_hours=urgency_threshold_hours)
            if result != "NOTHING_URGENT":
                # Let the agent turn the raw urgent item into a clear,
                # actionable message instead of just printing raw data.
                response = agent(
                    f"Here is an urgent item that was just detected: {result}\n"
                    f"Give the user a short, direct heads up about it."
                )
                print(f"[ALERT] {response}\n")
            else:
                print("[ok] nothing urgent right now.")
            time.sleep(poll_seconds)
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "chat"
    if mode == "watch":
        watch_mode()
    else:
        chat_mode()
