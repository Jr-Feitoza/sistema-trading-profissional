import time
import csv
import random
from datetime import datetime

log_file = "live_logs/orders.csv"
header = ["timestamp", "symbol", "action", "price", "qty"]

with open(log_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    for _ in range(20):
        row = [
            datetime.utcnow().isoformat(),
            "BTCUSDT",
            random.choice(["buy", "sell"]),
            round(random.uniform(30000, 35000), 2),
            round(random.uniform(0.01, 0.1), 4)
        ]
        writer.writerow(row)
        f.flush()
        time.sleep(1)

