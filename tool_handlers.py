from filters import filter_users

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
        raise ToolError("email_starts_with is required")
    users = stores[store]["users"]
    filtered_users = filter_users(users, args.get("email_starts_with"))
    return {"store": store, "count": len(filtered_users), "ui_action": {"type": "show_users", "store": store, "email_prefix": ",".join(args["email_starts_with"])}}

def show_revenue_chart(args, metrics, stores):
    store, m = get_store_metrics(args, metrics)
    start = args.get("start_date")
    end = args.get("end_date")
    if not start or not end:
        raise ToolError("start_date and end_date are required")
    daily = m["daily_revenue"]
    days = [d for d in daily if start <= d <= end]
    total = round(sum(daily[d] for d in days), 2)
    if not days:
        raise ToolError(f"No data in this range. Data covers {min(daily)} to {max(daily)}")
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