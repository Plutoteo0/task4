from filter import filter_users

class ToolError(Exception):
    pass

def get_store_metrics(args, metrics):
    store = args.get('store')
    if store not in metrics:
        raise ToolError(f"Unknown store: {store}. Available: {list(metrics)}")
    return store, metrics[store]

def list_stores(args, metrics, stores):
    return {"stores": list(metrics)}

def get_unique_users(args, metrics, stores):
    store, m = get_store_metrics(args, metrics)
    return {"store": store, "unique_users": m['unique_users']}

def get_author_sets_count(args, metrics, stores):
    store, m = get_store_metrics(args, metrics)
    return {"store": store, "author_sets_count": m["author_sets"]}

def get_top_authors(args, metrics, stores):
    store, m = get_store_metrics(args, metrics)
    return {"store": store, "top_authors": m["top_authors"]}

def get_top_days(args, metrics, stores):
    store, m = get_store_metrics(args, metrics)
    return {"store": store, "top_days": [
        {"rank": i + 1, "date": day, "revenue": m["daily_revenue"][day]}
        for i, day in enumerate(m["top_days"])
    ]}

def get_best_buyer(args, metrics, stores):
     store, m = get_store_metrics(args, metrics)
     return {"store": store, "best_buyer": m["best_buyer_details"]}

def get_revenue(args, metrics, stores):
    store, m = get_store_metrics(args, metrics)
    start = args.get("start_date") or "0000-00-00"
    end = args.get("end_date") or "9999-12-31"
    daily = m["daily_revenue"]
    days = {d: v for d, v in daily.items() if start <= d <= end}
    return {
        "store": store,
        "total_revenue": round(sum(days.values()), 2),
        "days_counted": len(days),
        "data_range": {"first_date": min(daily), "last_date": max(daily)},
    }

def filter_users_tool(args, metrics, stores):
    store, _ = get_store_metrics(args, metrics)
    if not args.get("email_starts_with"):
        return {"error": "Cannot use tool"}
    users = stores[store]["users"]
    filtred_users = filter_users(users, args.get("email_starts_with"))
    return {"count": len(filtred_users), "ui_action": {"type": "show_users", "store": store, "email_prefix": ",".join(args["email_starts_with"])}}

def show_revenue_chart(args, metrics, stores):
    store, m = get_store_metrics(args, metrics)
    start = args.get("start_date")
    end = args.get("end_date")
    if not start or not end:
        return {"error": "start_date and end_date are required"}
    daily = m["daily_revenue"]
    days = [d for d in daily if start <= d <= end]
    total = round(sum(daily[d] for d in days), 2)
    if not days:
        return {"error": f"No data in this range. Data covers {min(daily)} to {max(daily)}"}
    return {
        "store": store,
        "days_shown": len(days),
        "total_revenue": total,
            "ui_action": {
                "type": "show_revenue",
                "store": store,
                "start_date": start,
                "end_date": end,
            },
        }

STORE_PARAM = {
    "type": "string",
    "enum": ["STORE1", "STORE2", "STORE3", "STORE4", "STORE5"],
    "description": "Store identifier",
}

STORE_ONLY_SCHEMA = {
    "type": "object",
    "properties": {"store": STORE_PARAM},
    "required": ["store"],
}

HANDLERS = {
    "list_stores": {
        "fn": list_stores,
        "description": "List the available stores.",
        "input_schema": {"type": "object", "properties": {}},
    },
    "get_unique_users": {
        "fn": get_unique_users,
        "description": "Number of real unique users of a store, after merging duplicate accounts that belong to the same person.",
        "input_schema": STORE_ONLY_SCHEMA,
    },
    "get_author_sets_count": {
        "fn": get_author_sets_count,
        "description": "Number of unique author sets (distinct combinations of authors of a book) in a store's catalog.",
        "input_schema": STORE_ONLY_SCHEMA,
    },
    "get_top_authors": {
        "fn": get_top_authors,
        "description": "Most popular author(s) of a store by number of books sold. Can return several authors if there is a tie.",
        "input_schema": STORE_ONLY_SCHEMA,
    },
    "get_top_days": {
        "fn": get_top_days,
        "description": "Top 5 days of a store by revenue in USD, ranked from the highest.",
        "input_schema": STORE_ONLY_SCHEMA,
    },
    "get_best_buyer": {
        "fn": get_best_buyer,
        "description": "Best buyer of a store by total spending in USD: all user IDs of that person, total spent, and profile (name, email, phone, address) for each ID.",
        "input_schema": STORE_ONLY_SCHEMA,
    },
    "get_revenue": {
        "fn": get_revenue,
        "description": "Total revenue in USD of a store for a date range (inclusive). Without dates, the whole period. Also returns the date range covered by the data.",
        "input_schema": {
            "type": "object",
            "properties": {
                "store": STORE_PARAM,
                "start_date": {"type": "string", "description": "Start date, format YYYY-MM-DD (optional)"},
                "end_date": {"type": "string", "description": "End date, format YYYY-MM-DD (optional)"},
            },
            "required": ["store"],
        },
    },
    "filter_users": {
        "fn": filter_users_tool,
        "description": (
                "Show users of a store whose e-mail starts with given letters or prefixes "
                "(e.g. 's' and 'p'). Updates the dashboard Users tab and returns how many users matched."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "store": STORE_PARAM,
                "email_starts_with": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Letters or prefixes the e-mail must start with, e.g. ['s', 'p']",
                },
            },
            "required": ["store", "email_starts_with"],
        },
    },
    "show_revenue_chart": {
        "fn": show_revenue_chart,
        "description": (
            "Change the Revenue chart of the dashboard to show a given date range for a store. "
            "Use it when the user asks to SHOW or DISPLAY revenue on the chart. "
            "For a plain numeric answer use get_revenue instead."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "store": STORE_PARAM,
                "start_date": {"type": "string", "description": "Start date, format YYYY-MM-DD"},
                "end_date": {"type": "string", "description": "End date, format YYYY-MM-DD"},
            },
            "required": ["store", "start_date", "end_date"],
        },
    },
}

TOOLS = [
    {"name": name, "description": e["description"], "input_schema": e["input_schema"]}
    for name, e in HANDLERS.items()
]

def run_tool(name, args, metrics, stores):
    tool = HANDLERS.get(name)
    if tool is None:
        return {"error": f"unknown tool: {name}"}
    try:
        return tool["fn"](args, metrics, stores)
    except ToolError as e:
        return {"error": str(e)}

if __name__ == "__main__":
    from app import METRICS, STORES
    print(run_tool("get_unique_users", {"store": "STORE1"}, METRICS, STORES))
    print(run_tool("list_stores", {}, METRICS, STORES))
    print(run_tool("filter_users", {"store": "STORE1", "email_starts_with": ["s", "p"]}, METRICS, STORES))
    print(run_tool("get_revenue", {"store": "STORE1", "start_date": "2026-01-01", "end_date": "2026-01-31"}, METRICS, STORES))
    print(run_tool("show_revenue_chart", {"store": "STORE1", "start_date": "2026-01-01", "end_date": "2026-01-31"}, METRICS, STORES))
    print(run_tool("get_unique_users", {"store": "STORE9"}, METRICS, STORES))
    print(run_tool("no_such_tool", {}, METRICS, STORES))