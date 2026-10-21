import pandas as pd

def filter_users(users, prefixes):
    prefixes = tuple(p.lower() for p in prefixes)
    mask = users["email"].str.lower().str.startswith(prefixes, na=False)
    filtred_users = users[mask]
    filtred_users = filtred_users.astype(object).where(filtred_users.notna(), None)
    return filtred_users.to_dict("records")

if __name__ == "__main__":
    from pathlib import Path
    from metrics import load_store

    data = load_store(Path(__file__).parent / "Data" / "STORE1")
    rows = filter_users(data["users"], ["s", "p"])
    print(len(rows))
    print(rows[0])
    users = data["users"]
    print(users["email"].str.lower().str[0].isin(["s", "p"]).sum())