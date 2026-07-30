import csv
import random
import os

try:
    from openpyxl import Workbook
except ImportError:
    print("Error: openpyxl not installed. Run: pip install openpyxl")
    exit(1)

PLATFORMS = ["Instagram", "YouTube", "LinkedIn", "Twitter", "Facebook"]
LANGUAGES = ["Hindi", "English", "Mixed"]
LOCATIONS = ["New Delhi", "Mumbai", "Bengaluru", "Pune", "Ahmedabad"]
TOPICS = ["Digital India", "UPI", "PM Kisan", "Skill India", "Startup India", "Ayushman Bharat", "Swachh Bharat", "Railway Development", "Education", "Healthcare", "Agriculture", "Technology"]

def generate_row(index, force_duplicate=False):
    platform = random.choice(PLATFORMS)
    language = random.choice(LANGUAGES)
    name = f"Discovery Creator {index}"
    
    # Force specific handles for deduplication testing
    if force_duplicate:
        handle = f"discovery_creator_{index}_{platform.lower()[:3]}_99"
    else:
        handle = f"discovery_creator_{index}_{platform.lower()[:3]}_{random.randint(10, 80)}"
        
    followers = random.choice(["100", "5K", "50K", "500K", "5M"])
    topic = random.choice(TOPICS)
    
    return {
        "Name": name,
        "Handle": handle,
        "Platform": platform,
        "Followers": followers,
        "Following": str(random.randint(100, 2000)),
        "Posts": str(random.randint(50, 1000)),
        "Bio": f"Advocate for {topic} and national development. Supporting government initiatives.",
        "Description": f"Content focused on {topic}. Keywords: {topic}, Viksit Bharat, Make in India.",
        "Language": language,
        "Location": random.choice(LOCATIONS),
        "Profile URL": f"https://{platform.lower()}.com/{handle}",
        "Email": f"{handle}@example.com",
        "Website": f"https://{handle}.com"
    }

# Generate 90 unique rows
data = [generate_row(i) for i in range(90)]

# Generate 10 specific duplicate rows (exact same handles as the first 10)
for i in range(10):
    data.append(generate_row(i, force_duplicate=True))

HEADERS = ["Name", "Handle", "Platform", "Followers", "Following", "Posts", "Bio", "Description", "Language", "Location", "Profile URL", "Email", "Website"]

# Write CSV
with open("mock_discovery_dataset.csv", mode='w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=HEADERS)
    writer.writeheader()
    writer.writerows(data)
print("✅ Generated: mock_discovery_dataset.csv")

# Write Excel
wb = Workbook()
ws = wb.active
ws.title = "Discovery Mock Data"
ws.append(HEADERS)
for row in data:
    ws.append([row[h] for h in HEADERS])
wb.save("mock_discovery_dataset.xlsx")
print("✅ Generated: mock_discovery_dataset.xlsx")

print("\n🎉 Discovery QA datasets generated successfully!")