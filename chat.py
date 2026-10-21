import json
import anthropic
from dotenv import load_dotenv
from tools import TOOLS, run_tool

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-haiku-5-5"

SYSTEM = (
    "You are an assistant for a bookstore analytics dashboard. "
    "There are five stores: STORE1..STORE5. "
    "Answer ONLY using results returned by the provided tools. "
    "Never guess, estimate or calculate numbers from memory: if a tool does not provide the data, "
    "say that you don't have it. If the user does not say which store, ask which one. "
    "Use the data_range from get_revenue to say when a requested period is outside the data. "
    "All money amounts are in USD. Answer in the language of the user's question, briefly."
    "report only facts present in tool results, plain text without markdown"
    "You can also show users on the dashboard with filter_users; after calling it, briefly say how many users were found. "
    "You can show a revenue date range on the dashboard chart with show_revenue_chart; after calling it, briefly confirm the range. "
    "When the user asks to show, display, plot or open revenue on the dashboard or chart "
    "(e.g.'show revenue'), call show_revenue_chart, not get_revenue. "
    "Use get_revenue only when the user asks for a number without asking to show it. "
)

def answer(messages, metrics, stores):
    actions = []
    for _ in range(6):
        resp = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM,
            tools=TOOLS,
            messages=messages
        )

        if resp.stop_reason != "tool_use":
            return {"answer": "".join(b.text for b in resp.content if b.type == "text"), "actions": actions}

        messages.append({"role": "assistant", "content": resp.content})

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                result = run_tool(block.name, block.input, metrics, stores)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result, ensure_ascii=False),
                })
                if result.get('ui_action'):
                    actions.append(result["ui_action"])
        messages.append({"role": "user", "content": results})

    return {"answer": "Sorry, I could not finish the request.", "actions": actions}

if __name__ == "__main__":
    from app import METRICS, STORES
    msgs = [{"role": "user", "content": "Покажи пользователей STORE1, у которых email начинается на s или p"}]
    print(answer(msgs, METRICS, STORES))