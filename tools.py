from filter import filter_users

def run_tool(name, args, metrics, stores):
    if name == "list_stores":
        return {"stores": list(metrics)}

    store = args.get("store")
    if store not in metrics:
        return {"error": f"Unknown store: {store}. Available: {list(metrics)}"}
    m = metrics[store]

    if name == "get_unique_users":
         return {"store": store, "unique_users": m["unique_users"]}
    if name == "get_author_sets_count":
        return {"store": store, "author_sets_count": m["author_sets"]}
    if name == "get_top_authors":
        return {"store": store, "top_authors": m["top_authors"]}
    if name == "get_top_days":
        return {"store": store, "top_days": [
    {"rank": i + 1, "date": day, "revenue": m["daily_revenue"][day]}
    for i, day in enumerate(m["top_days"])
    ]}
    if name == "get_best_buyer":
        return {"store": store, "best_buyer": m["best_buyer_details"]}
    
    if name == "get_revenue":
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

    if name == "filter_users":
        if not args.get("email_starts_with"):
                    return {"error": "Cannot use tool"}
        users = stores[store]["users"]
        filtred_users = filter_users(users, args.get("email_starts_with"))
        return {"count": len(filtred_users), "ui_action": {"type": "show_users", "store": store, "email_prefix": ",".join(args["email_starts_with"])}}

    if name == "show_revenue_chart":
        start = args.get("start_date")
        end = args.get("end_date")
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

    return {"error": f"unknown tool: {name}"}

STORE_PARAM = {
    "type": "string",
    "enum": ["STORE1", "STORE2", "STORE3", "STORE4", "STORE5"],
    "description": "Store identifier",
}

TOOLS = [
    {
        "name": "list_stores",
        "description": "List the available stores.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "get_unique_users",
        "description": "Number of real unique users of a store, after merging duplicate accounts that belong to the same person.",
        "input_schema": {"type": "object", "properties": {"store": STORE_PARAM}, "required": ["store"]},
    },
    {
        "name": "get_author_sets_count",
        "description": "Number of unique author sets (distinct combinations of authors of a book) in a store's catalog.",
        "input_schema": {"type": "object", "properties": {"store": STORE_PARAM}, "required": ["store"]},
    },
    {
        "name": "get_top_authors",
        "description": "Most popular author(s) of a store by number of books sold. Can return several authors if there is a tie.",
        "input_schema": {"type": "object", "properties": {"store": STORE_PARAM}, "required": ["store"]},
    },
    {
        "name": "get_top_days",
        "description": "Top 5 days of a store by revenue in USD, ranked from the highest.",
        "input_schema": {"type": "object", "properties": {"store": STORE_PARAM}, "required": ["store"]},
    },
    {
        "name": "get_best_buyer",
        "description": "Best buyer of a store by total spending in USD: all user IDs of that person, total spent, and profile (name, email, phone, address) for each ID.",
        "input_schema": {"type": "object", "properties": {"store": STORE_PARAM}, "required": ["store"]},
    },
    {
        "name": "get_revenue",
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
    {
        "name": "filter_users",
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
        {
        "name": "show_revenue_chart",
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
]

if __name__ == "__main__":
    from app import METRICS, STORES
    print(run_tool("get_unique_users", {"store": "STORE1"}, METRICS, STORES))
    print(run_tool("filter_users", {"store": "STORE1", "email_starts_with": ["s", "p"]}, METRICS, STORES))
    print(run_tool("show_revenue_chart", {"store": "STORE1", "start_date": "2026-01-01", "end_date": "2026-01-31"}, METRICS, STORES))
    print(run_tool("show_revenue_chart", {"store": "STORE1", "start_date": "2030-01-01", "end_date": "2030-01-31"}, METRICS, STORES))