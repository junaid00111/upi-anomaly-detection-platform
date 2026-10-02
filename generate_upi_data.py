import csv
import random
import uuid
from datetime import datetime, timedelta

def generate_upi_data(num_records=10000, output_file="upi.csv"):
    random.seed(42)  # For reproducible realistic data

    first_names = [
        "Aarav", "Vivaan", "Aditya", "Vihaan", "Arjun", "Sai", "Reyansh", "Ayaan", "Krishna", "Ishaan",
        "Shaurya", "Atharva", "Advik", "Pranav", "Advaith", "Aaryan", "Dhruv", "Kabir", "Ritvik", "Darsh",
        "Aanya", "Diya", "Saanvi", "Ananya", "Aadhya", "Pari", "Chiara", "Myra", "Anvi", "Prisha",
        "Riya", "Isha", "Kavya", "Avani", "Navya", "Sneha", "Pooja", "Meera", "Tanvi", "Shreya",
        "Rahul", "Rohan", "Amit", "Suresh", "Ramesh", "Deepak", "Priya", "Neha", "Sunita", "Anjali"
    ]

    last_names = [
        "Sharma", "Verma", "Patel", "Singh", "Kumar", "Gupta", "Reddy", "Mehta", "Joshi", "Nair",
        "Iyer", "Rao", "Das", "Banerjee", "Chatterjee", "Mishra", "Pandey", "Yadav", "Chauhan", "Bhat",
        "Kulkarni", "Deshmukh", "Pillai", "Menon", "Agarwal", "Shah", "Malhotra", "Kapoor", "Saxena", "Choudhury"
    ]

    merchants = [
        ("Swiggy", "Food & Dining"),
        ("Zomato", "Food & Dining"),
        ("Blinkit", "Groceries"),
        ("Zepto", "Groceries"),
        ("BigBasket", "Groceries"),
        ("Amazon Pay Merchant", "Shopping"),
        ("Flipkart", "Shopping"),
        ("Myntra", "Shopping"),
        ("Uber India", "Transportation"),
        ("Ola Cabs", "Transportation"),
        ("Rapido", "Transportation"),
        ("BookMyShow", "Entertainment"),
        ("Netflix India", "Entertainment"),
        ("Hotstar", "Entertainment"),
        ("Airtel Prepaid/Postpaid", "Bills & Utilities"),
        ("Jio Recharge", "Bills & Utilities"),
        ("BESCOM / Electricity Bill", "Bills & Utilities"),
        ("Apollo Pharmacy", "Healthcare"),
        ("Medplus", "Healthcare"),
        ("Cult.fit", "Health & Fitness"),
        ("Local Kirana Store", "Groceries"),
        ("Chai Point", "Food & Dining"),
        ("Starbucks", "Food & Dining"),
        ("Decathlon", "Shopping"),
        ("Indian Oil Petrol Pump", "Fuel")
    ]

    upi_handles = ["okhdfcbank", "oksbi", "okicici", "okaxis", "ybl", "ibl", "paytm", "apl", "upi", "barodampay"]
    banks = ["HDFC Bank", "State Bank of India", "ICICI Bank", "Axis Bank", "Kotak Mahindra Bank", "Punjab National Bank", "Bank of Baroda", "Canara Bank", "Union Bank of India", "IndusInd Bank"]
    apps = ["Google Pay", "PhonePe", "Paytm", "BHIM", "CRED", "Amazon Pay", "WhatsApp Pay", "Axis Pay"]
    app_weights = [0.35, 0.35, 0.15, 0.05, 0.05, 0.03, 0.01, 0.01]

    device_types = ["Android", "iOS"]
    device_weights = [0.78, 0.22]

    states = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi NCR", "Uttar Pradesh", "Telangana", "Gujarat", "West Bengal", "Rajasthan", "Kerala"]

    # Pre-generate a pool of 500 users
    user_pool = []
    for _ in range(500):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        uname = f"{fn.lower()}.{ln.lower()}{random.randint(10, 999)}"
        handle = random.choice(upi_handles)
        vpa = f"{uname}@{handle}"
        bank = random.choice(banks)
        user_pool.append({
            "name": f"{fn} {ln}",
            "vpa": vpa,
            "bank": bank,
            "state": random.choice(states)
        })

    fieldnames = [
        "transaction_id",
        "timestamp",
        "sender_name",
        "sender_upi_id",
        "sender_bank",
        "receiver_name",
        "receiver_upi_id",
        "receiver_bank",
        "amount_inr",
        "transaction_type",
        "category",
        "upi_app",
        "device_os",
        "location_state",
        "status",
        "failure_reason"
    ]

    start_date = datetime(2024, 1, 1, 0, 0, 0)
    end_date = datetime(2024, 6, 30, 23, 59, 59)
    time_span_seconds = int((end_date - start_date).total_seconds())

    rows = []

    for i in range(num_records):
        txn_id = f"UPI{datetime.now().strftime('%Y%m')}{random.randint(1000000000, 9999999999)}"
        random_seconds = random.randint(0, time_span_seconds)
        txn_time = start_date + timedelta(seconds=random_seconds)

        sender = random.choice(user_pool)

        # 60% P2M (Peer to Merchant), 40% P2P (Peer to Peer)
        txn_type = "P2M" if random.random() < 0.60 else "P2P"

        if txn_type == "P2M":
            merchant_name, category = random.choice(merchants)
            receiver_name = merchant_name
            m_slug = merchant_name.lower().replace(" ", "").replace("&", "").replace("/", "")[:10]
            receiver_upi_id = f"{m_slug}@{random.choice(upi_handles)}"
            receiver_bank = random.choice(banks)

            # Realistic amount distributions by category
            if category == "Groceries":
                amount = round(random.uniform(50, 2500), 2)
            elif category == "Food & Dining":
                amount = round(random.uniform(30, 1500), 2)
            elif category == "Shopping":
                amount = round(random.uniform(200, 10000), 2)
            elif category == "Transportation":
                amount = round(random.uniform(30, 800), 2)
            elif category == "Entertainment":
                amount = round(random.uniform(150, 1500), 2)
            elif category == "Bills & Utilities":
                amount = round(random.uniform(100, 4500), 2)
            elif category == "Fuel":
                amount = round(random.uniform(100, 3000), 2)
            else:
                amount = round(random.uniform(100, 5000), 2)
        else:
            receiver = random.choice(user_pool)
            while receiver["vpa"] == sender["vpa"]:
                receiver = random.choice(user_pool)
            receiver_name = receiver["name"]
            receiver_upi_id = receiver["vpa"]
            receiver_bank = receiver["bank"]
            category = "Peer Transfer"

            # P2P can vary from small split bills to larger transfers
            p_rand = random.random()
            if p_rand < 0.5:
                amount = round(random.uniform(20, 1000), 2)
            elif p_rand < 0.85:
                amount = round(random.uniform(1000, 10000), 2)
            else:
                amount = round(random.uniform(10000, 50000), 2)

        # Status: 92% SUCCESS, 6% FAILED, 2% PENDING
        status_rand = random.random()
        if status_rand < 0.92:
            status = "SUCCESS"
            failure_reason = "NA"
        elif status_rand < 0.98:
            status = "FAILED"
            failure_reason = random.choice([
                "INSUFFICIENT_FUNDS",
                "INCORRECT_UPI_PIN",
                "BANK_SERVER_DOWN",
                "TRANSACTION_LIMIT_EXCEEDED",
                "NETWORK_TIMEOUT"
            ])
        else:
            status = "PENDING"
            failure_reason = "AWAITING_BANK_CONFIRMATION"

        app = random.choices(apps, weights=app_weights)[0]
        os_type = random.choices(device_types, weights=device_weights)[0]

        rows.append({
            "transaction_id": txn_id,
            "timestamp": txn_time.strftime("%Y-%m-%d %H:%M:%S"),
            "sender_name": sender["name"],
            "sender_upi_id": sender["vpa"],
            "sender_bank": sender["bank"],
            "receiver_name": receiver_name,
            "receiver_upi_id": receiver_upi_id,
            "receiver_bank": receiver_bank,
            "amount_inr": amount,
            "transaction_type": txn_type,
            "category": category,
            "upi_app": app,
            "device_os": os_type,
            "location_state": sender["state"],
            "status": status,
            "failure_reason": failure_reason
        })

    # Sort rows chronologically
    rows.sort(key=lambda x: x["timestamp"])

    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Successfully generated {num_records} UPI transaction records into {output_file}")

if __name__ == "__main__":
    generate_upi_data(10000, "upi.csv")
