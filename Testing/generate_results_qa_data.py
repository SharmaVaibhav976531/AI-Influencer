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
LOCATIONS = ["New Delhi", "Mumbai", "Bengaluru", "Pune", "Ahmedabad", "Chennai", "Kolkata"]
SOURCES = ["UPLOADED", "MOCK", "INSTAGRAM", "YOUTUBE"]

KEYWORD_POOLS = {
    "govt_tech": ["Digital India", "UPI", "Startup India", "Viksit Bharat", "Make in India"],
    "govt_agri": ["PM Kisan", "Swachh Bharat", "Farmer Welfare", "Agriculture"],
    "govt_health": ["Ayushman Bharat", "Healthcare", "Public Health", "Yoga"],
    "govt_edu": ["Skill India", "Education Mission", "NEP 2020", "Learning"],
    "neutral": ["Lifestyle", "Travel", "Entertainment", "Sports", "Fashion", "Gaming"],
    "unrelated": ["Random text", "Unrelated content", "Just for fun", "No specific niche"]
}

def generate_row(index):
    # Base generation
    platform = random.choice(PLATFORMS)
    language = random.choice(LANGUAGES)
    source = random.choice(SOURCES)
    
    # Assign niche and keywords based on index to ensure predictable test data
    if index < 20:
        niche = "govt_tech"
        name = f"Tech Guru {index}"
        bio = f"Passionate about {', '.join(random.sample(KEYWORD_POOLS[niche], 2))}. Building the future."
    elif index < 40:
        niche = "govt_agri"
        name = f"Kisan Mitra {index}"
        bio = f"Supporting {', '.join(random.sample(KEYWORD_POOLS[niche], 2))} and rural development."
    elif index < 60:
        niche = "neutral"
        name = f"Lifestyle Creator {index}"
        bio = f"Sharing my journey in {', '.join(random.sample(KEYWORD_POOLS[niche], 2))}."
    elif index < 80:
        niche = "unrelated"
        name = f"Random User {index}"
        bio = "Just posting random stuff. No specific agenda or keywords."
    else:
        niche = "govt_edu"
        name = f"Edu Expert {index}"
        bio = f"Focused on {', '.join(random.sample(KEYWORD_POOLS[niche], 2))} and student success."

    # Edge case injections
    if index == 90:
        name = "🚀 Unicode & Emoji Test 🇮🇳"
        bio = "हिंदी में टेक्नोलॉजी! Digital India & Startup India. 🚀🔥 <script>alert('xss')</script>"
        language = "Hindi"
    elif index == 91:
        name = "Long Bio User"
        bio = "A" * 800 + " This is a massive bio to test UI wrapping and database storage limits."
    elif index == 92:
        name = "Zero Follower Test"
        followers = "0"
    elif index == 93:
        name = "High Follower Test"
        followers = "5000000"
    elif index == 94:
        name = "Missing Optional Fields"
        bio = ""
        language = ""
        location = ""
    else:
        followers = random.choice(["500", "5000", "50000", "500000", "5000000"])

    handle = f"{name.lower().replace(' ', '_').replace('🚀', '').replace('🇮🇳', '')}_{platform.lower()[:3]}_{index}"
    
    return {
        "Name": name,
        "Handle": handle,
        "Platform": platform,
        "Followers": followers if 'followers' in locals() else random.choice(["500", "5000", "50000", "500000", "5000000"]),
        "Following": str(random.randint(100, 2000)),
        "Posts": str(random.randint(50, 1000)),
        "Bio": bio,
        "Description": f"Content creator focused on {niche}. Keywords: {', '.join(random.sample(KEYWORD_POOLS.get(niche, ['general']), 2))}.",
        "Language": language if 'language' in locals() else random.choice(LANGUAGES),
        "Location": location if 'location' in locals() else random.choice(LOCATIONS),
        "Profile URL": f"https://{platform.lower()}.com/{handle}",
        "Email": f"{handle}@example.com",
        "Website": f"https://{handle}.com" if random.random() > 0.3 else ""
    }

HEADERS = ["Name", "Handle", "Platform", "Followers", "Following", "Posts", "Bio", "Description", "Language", "Location", "Profile URL", "Email", "Website"]

# Generate 100 rows
data = [generate_row(i) for i in range(100)]

# Write CSV
with open("results_dashboard_dataset.csv", mode='w', encoding='utf-8-sig', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=HEADERS)
    writer.writeheader()
    writer.writerows(data)
print("✅ Generated: results_dashboard_dataset.csv")

# Write Excel
wb = Workbook()
ws = wb.active
ws.title = "Influencers"
ws.append(HEADERS)
for row in data:
    ws.append([row[h] for h in HEADERS])
wb.save("results_dashboard_dataset.xlsx")
print("✅ Generated: results_dashboard_dataset.xlsx")

print("\n🎉 Results Dashboard QA datasets generated successfully!")