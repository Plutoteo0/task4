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

from app import METRICS
from tools import run_tool

if __name__ == "__main__":
    print(run_tool("get_unique_users", {"store": "STORE1"}, METRICS))
    print(run_tool("get_best_buyer", {"store": "STORE1"}, METRICS))
    print(run_tool("get_revenue", {"store": "STORE1", "start_date": "2026-01-01", "end_date": "2026-01-31"}, METRICS))
    print(run_tool("get_unique_users", {"store": "STORE9"}, METRICS))