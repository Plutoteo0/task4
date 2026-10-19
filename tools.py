def run_tool(name, args, metrics):
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
]

if __name__ == "__main__":
    from app import METRICS
    from tools import run_tool
    print(run_tool("get_unique_users", {"store": "STORE1"}, METRICS))
    print(run_tool("get_best_buyer", {"store": "STORE1"}, METRICS))
    print(run_tool("get_revenue", {"store": "STORE1", "start_date": "2026-01-01", "end_date": "2026-01-31"}, METRICS))
    print(run_tool("get_unique_users", {"store": "STORE9"}, METRICS))