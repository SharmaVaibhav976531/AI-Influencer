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
RECOMMENDATIONS = ["Highly Relevant", "Moderately Relevant", "Low Match"]
LOCATIONS = ["New Delhi", "Mumbai", "Bengaluru", "Pune", "Ahmedabad"]

def generate_base_row(index):
    platform = random.choice(PLATFORMS)
    language = random.choice(LANGUAGES)
    name = f"Creator {index}"
    handle = f"creator_{index}_{platform.lower()[:3]}"
    followers = random.choice([100, 5000, 50000, 500000, 5000000])
    
    return {
        "Name": name,
        "Handle": handle,
        "Platform": platform,
        "Followers": str(followers),
        "Following": str(random.randint(100, 2000)),
        "Posts": str(random.randint(50, 1000)),
        "Bio": f"Content creator focused on {random.choice(['Technology', 'Agriculture', 'Lifestyle'])}.",
        "Description": f"Keywords: {random.choice(['Digital India', 'PM Kisan', 'Skill India', 'Random'])}.",
        "Language": language,
        "Location": random.choice(LOCATIONS),
        "Profile URL": f"https://{platform.lower()}.com/{handle}",
        "Email": f"{handle}@example.com",
        "Website": f"https://{handle}.com"
    }

# Generate 250 base rows
data = [generate_base_row(i) for i in range(250)]

# --- Inject Export & Edge Case Validations ---
# Row 200: Hindi + Unicode + Emoji
data[200].update({
    "Name": "🚀 हिंदी गुरु 🇮🇳",
    "Bio": "डिजिटल इंडिया और टेक्नोलॉजी की दुनिया में आपका स्वागत है। 🚀🔥",
    "Description": "UPI से भुगतान अब और भी आसान। #DigitalIndia",
    "Language": "Hindi"
})

# Row 210: Commas and Quotes (Tests CSV escaping)
data[210].update({
    "Name": "Finance, The Expert",
    "Bio": 'He said, "Invest in Digital India and UPI wisely."',
    "Description": "Topics: \"Stock Market\", 'Mutual Funds', Economy."
})

# Row 220: New Lines (Tests Excel wrapping and CSV integrity)
data[220].update({
    "Name": "Multi Line Bio",
    "Bio": "Line 1: Digital India\nLine 2: Startup India\nLine 3: Viksit Bharat",
    "Description": "First paragraph.\n\nSecond paragraph with PM Kisan details."
})

# Row 230: Very Long Bio (Tests column sizing and UI wrapping)
data[230].update({
    "Name": "Long Bio User",
    "Bio": "A" * 400 + " Make in India and Swachh Bharat are great initiatives. " + "B" * 400
})

# Row 240: Zero Followers
data[240].update({
    "Name": "Zero Followers",
    "Followers": "0",
    "Bio": "Just starting out. Skill India and Education Mission focus."
})

# Row 245: Very High Followers
data[245].update({
    "Name": "Mega Influencer",
    "Followers": "5000000",
    "Bio": "Top tier influencer. Ayushman Bharat and Railway Development advocate."
})

# Row 248: Missing Optional Fields
data[248].update({
    "Name": "Minimalist User",
    "Bio": "",
    "Description": "",
    "Location": "",
    "Website": "",
    "Email": ""
})

HEADERS = ["Name", "Handle", "Platform", "Followers", "Following", "Posts", "Bio", "Description", "Language", "Location", "Profile URL", "Email", "Website"]

# Write CSV
with open("analytics_dashboard_dataset.csv", mode='w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=HEADERS)
    writer.writeheader()
    writer.writerows(data)
print("✅ Generated: analytics_dashboard_dataset.csv")

# Write Excel
wb = Workbook()
ws = wb.active
ws.title = "Influencers"
ws.append(HEADERS)
for row in data:
    ws.append([row[h] for h in HEADERS])
wb.save("analytics_dashboard_dataset.xlsx")
print("✅ Generated: analytics_dashboard_dataset.xlsx")

print("\n🎉 Analytics & Export QA datasets generated successfully!")