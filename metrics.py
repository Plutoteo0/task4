from cleaning import load_orders, load_users, load_books
from cleaning import build_person_map, find_id_groups, merge_groups
def daily_revenue(orders):
    return orders.groupby("date")["paid_price"].sum()

def top_days(orders, n=5):
    top5 = daily_revenue(orders).nlargest(n)
    return [d.isoformat() for d in top5.index]

def best_buyer(users, orders):
    spent = orders.groupby("user_id")["paid_price"].sum()
    person = build_person_map(users)
    labels = spent.index.map(person)
    per_person = spent.groupby(labels).sum()
    best_spender = per_person.idxmax()
    return [uid for uid, label in person.items() if label == best_spender]

def best_buyer_details(users, orders):
    ids = best_buyer(users, orders)
    user_info = users[users["id"].isin(ids)].copy()
    spent = orders.groupby("user_id")["paid_price"].sum()
    user_info['spent'] = user_info["id"].map(spent).fillna(0)
    user_info = user_info.astype(object).where(user_info.notna(), None)
    return {
        "user_ids": ids,
        "total_spent": round(float(user_info["spent"].sum()),2),
        "profiles": user_info[["id", "name", "email", "phone", "address", "spent"]].to_dict("records"),
    }

def count_unique_users(users):
    found = find_id_groups(users)
    merged = merge_groups(found)
    extra = sum(len(c) - 1 for c in merged)
    return len(users) - extra

def top_authors(orders, books):
    orders = orders.merge(books[["id", "author_set"]], left_on="book_id", right_on="id")
    orders["authors"] = orders["author_set"].map(list)
    orders = orders.explode("authors")
    sold = orders.groupby("authors")["quantity"].sum()
    best = sold[sold == sold.max()].index.tolist()
    return best

def count_author_sets(books):
    return books["author_set"].nunique()

def compute_store(store_dir):
    return compute_metrics(load_store(store_dir))

def load_store(store_dir):
    return {"users": load_users(store_dir), "orders": load_orders(store_dir), "books": load_books(store_dir)}

def compute_metrics(data):
    orders, users, books = data["orders"], data["users"], data["books"]
    revenue = daily_revenue(orders)
    return {
            "top_days": top_days(orders),
            "unique_users": count_unique_users(users),
            "author_sets": count_author_sets(books),
            "top_authors": top_authors(orders, books),
            "best_buyer": best_buyer(users, orders),
            "daily_revenue": {d.isoformat(): round(float(v), 2) for d, v in revenue.items()},
            "best_buyer_details": best_buyer_details(users, orders)
        }

if __name__ == "__main__":
    users = load_users("./task4/Data/STORE1")
    orders = load_orders("./task4/Data/STORE1")
    books = load_books("./task4/Data/STORE1")
    print(top_days(orders))
    print(count_unique_users(users))
    print(count_author_sets(books))
    print(top_authors(orders, books))
    print(best_buyer(users, orders))