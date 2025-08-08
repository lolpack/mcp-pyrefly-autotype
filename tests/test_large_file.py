import math
import random
import datetime
import json
import os
from collections import defaultdict

# Global constants
PI = math.pi
DATA_DIR = "data"

# A simple class with multiple responsibilities
class OrderProcessor:
    def __init__(self, order_id, items, discounts=None):
        self.order_id = order_id
        self.items = items
        self.discounts = discounts or []
        self.status = "pending"

    def calculate_total(self):
        total = sum(item["price"] * item.get("quantity", 1) for item in self.items)
        for d in self.discounts:
            if d["type"] == "percent":
                total -= total * (d["value"] / 100)
            elif d["type"] == "fixed":
                total -= d["value"]
        return max(total, 0)

    def mark_shipped(self, tracking_number):
        self.status = "shipped"
        self.tracking_number = tracking_number
        self.shipped_at = datetime.datetime.now()

    def serialize(self):
        return {
            "order_id": self.order_id,
            "status": self.status,
            "items": self.items,
            "total": self.calculate_total(),
        }


# Standalone functions
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)

def load_json_file(file_name):
    path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return json.load(f)

def group_by_first_letter(words):
    grouped = defaultdict(list)
    for w in words:
        if w:
            grouped[w[0].lower()].append(w)
    return dict(grouped)

def random_points_in_circle(radius, count):
    points = []
    for _ in range(count):
        angle = random.uniform(0, 2 * PI)
        r = radius * math.sqrt(random.random())
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        points.append((x, y))
    return points

def get_most_expensive_item(items):
    if not items:
        return None
    return max(items, key=lambda x: x.get("price", 0))


# More complex function
def process_orders(orders):
    processed = []
    for o in orders:
        op = OrderProcessor(o["id"], o["items"], o.get("discounts"))
        total = op.calculate_total()
        if total > 100:
            op.mark_shipped("TRACK123")
        processed.append(op.serialize())
    return processed


# Nested data manipulation
def merge_user_data(user_list, activity_list):
    merged = {}
    for user in user_list:
        uid = user["id"]
        merged[uid] = {"name": user["name"], "activities": []}
    for activity in activity_list:
        uid = activity["user_id"]
        if uid in merged:
            merged[uid]["activities"].append(activity)
    return merged


# Simple CLI
if __name__ == "__main__":
    orders = [
        {
            "id": 1,
            "items": [{"name": "Widget", "price": 10.0, "quantity": 3}],
            "discounts": [{"type": "percent", "value": 10}],
        },
        {
            "id": 2,
            "items": [{"name": "Gadget", "price": 200.0}],
        },
    ]
    print(process_orders(orders))
    print(group_by_first_letter(["apple", "banana", "avocado", "berry", "cherry"]))
    print(random_points_in_circle(5, 10))
    print(fibonacci(6))
