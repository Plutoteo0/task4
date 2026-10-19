import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np
from itertools import combinations
import yaml

pattern = re.compile(r"([A-Za-z$€]+\s*)?(\s*\d+(?:[.¢]\d*)?)(\s*[A-Za-z$€]+)?")
pattern_cents = re.compile(r"(\d+)([$€])(\d+)¢")
CURRENCY_MAP = {"$": "USD", "USD": "USD", "€": "EUR", "EUR": "EUR"}

def load_orders(store_dir):
    orders = pd.read_parquet(Path(store_dir) / "orders.parquet")
    orders[["price", "currency"]] = orders["unit_price"].apply(parse_price).apply(pd.Series)
    orders["rate"] = orders["currency"].map({"USD": 1.0, "EUR": 1.2})
    orders['price_usd'] = (orders["price"] * orders["rate"]).round(2)
    orders['paid_price'] = (orders["quantity"] * orders["price_usd"]).round(2)
    orders["date"] = orders["timestamp"].apply(parse_date)
    
    return orders

def parse_price(unit_price):
    m = re.fullmatch(pattern, unit_price)
    if m is not None:
        price = m.group(2).strip().replace("¢", ".")
        currency = m.group(1) or m.group(3) or "USD"
        currency = currency.strip()
        price = float(price)
        return (price, CURRENCY_MAP[currency])
    else:
        m = re.fullmatch(pattern_cents, unit_price)
        if m is None:
            raise ValueError(f"Cannot parse price: {unit_price!r}")
        whole = m.group(1)
        currency = m.group(2)
        cents = m.group(3)
        price = float(f"{whole}.{cents}")
        return (price, CURRENCY_MAP[currency])

DATE_FORMATS = [
    (re.compile(r"\d{4}-\d{2}-\d{2}"),                                         "%Y-%m-%d"),
    (re.compile(r"\d{1,2}\.\d{1,2}\.\d{4}"),                                   "%d.%m.%Y"),
    (re.compile(r"\d{1,2}/\d{1,2}/\d{2}"),                                     "%m/%d/%y"),
    (re.compile(r"\d{1,2}-[A-Za-z]{3}-\d{4}"),                                 "%d-%b-%Y"),
    (re.compile(r"\d{1,2}-[A-Za-z]{4,}-\d{4}"),                                "%d-%B-%Y"),
    (re.compile(r"[A-Za-z]{3} [A-Za-z]{3} +\d{1,2} \d{2}:\d{2}:\d{2} \d{4}"),  "%a %b %d %H:%M:%S %Y"),
]

def parse_date(timestamp):
    for pattern, fmt in DATE_FORMATS:
        m = pattern.search(timestamp)
        if m is not None:
            return datetime.strptime(m.group(0), fmt).date()
    raise ValueError(f"Cannot parse date: {timestamp!r}")

def load_users(store_dir):
    users = pd.read_csv(Path(store_dir) / "users.csv")
    for col in ["name", "address", "phone", "email"]:
        users[col] = users[col].str.strip()
        users[col] = users[col].replace("", np.nan)
    users["phone"] = users["phone"].replace(r"\D", "", regex=True)
    return users

def find_id_groups(users):
    fields = ["name", "address", "phone", "email"]
    triplets = list(combinations(fields, 3))
    all_groups = []
    for comb in triplets:
        groups = users.groupby(list(comb))["id"].agg(list)
        lengths = groups.map(len)
        dups = groups[lengths > 1].tolist()
        all_groups.extend(dups)
    return all_groups

def merge_groups(groups):
    merged = []
    for group in groups:
        s = set(group)
        rest = []
        for m in merged:
            if m & s:
                s |= m
            else:
                rest.append(m)
        rest.append(s)
        merged = rest
    return merged


def build_person_map(users):
    found = find_id_groups(users)
    merged = merge_groups(found)
    person = {}
    for num, company in enumerate(merged):
        for uid in company:
            person[uid] = num
    next_num = len(merged)
    for uid in users["id"]:
        if uid not in person:
            person[uid] = next_num
            next_num += 1
    return person

def load_books(store_dir):
    with open(Path(store_dir) / "books.yaml", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    df = pd.DataFrame(data)
    df.columns = df.columns.str.lstrip(":")
    df["author_set"] = df["author"].map(parse_authors)
    return df

TITLES   = ["The Hon.", "Mr.", "Mrs.", "Ms.", "Miss", "Dr.", "Prof.", "Fr.",
            "Gov.", "Pres.", "Sen.", "Rep.", "Rev.", "Msgr.", "Amb."]
SUFFIXES = ["Jr.", "Sr.", "Esq.", "Ret.", "DDS", "PhD", "CPA", "MD", "DVM",
            "JD", "DO", "DC", "VM", "LLD", "III", "II", "IV", "V", "I"]

title = "|".join(re.escape(x) for x in TITLES)
suffix = "|".join(re.escape(x) for x in SUFFIXES)

TITLE_SUFFIX_RE = re.compile(rf"^(?:(?:{title})\s+)?(.+?)(?:\s+(?:{suffix}))?$")

def clean_author(name):
    m = re.fullmatch(TITLE_SUFFIX_RE, name)
    if m is None:
        raise ValueError(f"Cannot parse name {name!r}")
    parsed_name = m.group(1)
    return parsed_name

def parse_authors(author_str):
    authors = author_str.split(", ")
    return frozenset(clean_author(name) for name in authors)   
