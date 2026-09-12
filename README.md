# Deadline Agent

Built for AWS's **Agents for Humans** hackathon — Everyday Agents track.

## The problem

Deadlines (assignments, hackathons, certifications) pile up quietly and
you find out too late. Most "todo apps" still require *you* to remember
to open them and check. This agent flips that: it watches your
deadlines on its own, in the background, and only speaks up when
something actually needs your attention.

## How it works

- `tools.py` — three tools the agent can call on its own:
  - `get_upcoming_deadlines` — list what's coming up
  - `add_deadline` — add a new deadline
  - `get_most_urgent` — decide if anything is worth interrupting you for
- `agent.py` — wires those tools to a Strands `Agent`, with two modes:
  - **chat mode** — talk to it directly ("what's due this week?")
  - **watch mode** — it runs on a loop, checks on its own, and only
    prints an alert when something crosses the urgency threshold
    (default: due within 48 hours). This is the "autonomous" behavior
    the hackathon theme is about.

## Setup

1. **Python 3.10+** required. Check with `python --version`.

2. **Create a virtual environment** (keeps dependencies isolated):
   ```
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```
   pip install -r requirements.txt
   ```

4. **Get a free Gemini API key** (this is what powers the agent's
   reasoning :
   - Go to https://aistudio.google.com/apikey
   - Sign in with any Google account
   - Click "Create API key" and copy it
   - Set it as an environment variable:
     ```
     export GEMINI_API_KEY=your_key_here      # Windows: set GEMINI_API_KEY=your_key_here
     ```

5. **Verify it works**:
   ```
   python -c "import strands; print('ok')"
   ```
## Running it

Chat mode (talk to it directly):
```
python agent.py chat
```

Watch mode (autonomous background behavior — this is the part to show
in your demo):
```
python agent.py watch
```

## Customizing

- Edit `data/deadlines.json` to add your real deadlines, or use the
  `add_deadline` tool from chat mode.
- Change the urgency threshold by editing `urgency_threshold_hours` in
  `watch_mode()` inside `agent.py` (default: 48 hours).
