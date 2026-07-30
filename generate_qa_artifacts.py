import csv
import random
import os

try:
    from openpyxl import Workbook
except ImportError:
    print("Error: openpyxl not installed. Run: pip install openpyxl")
    exit(1)

# --- Data Pools ---
NAMES = ["Rahul Sharma", "Priya Singh", "Amit Patel", "Sneha Gupta", "Vikram Rathore", "Ananya Das", "Karan Mehta", "Pooja Verma", "Rohan Joshi", "Neha Kapoor"]
PLATFORMS = ["Instagram", "YouTube", "LinkedIn", "Twitter", "Facebook"]
LANGUAGES = ["Hindi", "English", "Mixed"]
LOCATIONS = ["New Delhi", "Mumbai", "Bengaluru", "Pune", "Ahmedabad"]
NICHES = {
    "Technology": ["Digital India", "Startup India", "UPI", "AI Innovation"],
    "Agriculture": ["PM Kisan", "Farmer Welfare", "Agri-Tech"],
    "Education": ["Skill India", "NEP 2020", "Education Mission"],
    "Healthcare": ["Ayushman Bharat", "Public Health", "Yoga"],
    "Infrastructure": ["National Highway", "Railway", "Make in India", "Viksit Bharat"],
    "Lifestyle": ["Swachh Bharat", "Environment", "Travel India"]
}
BIOS = {
    "Technology": "Tech enthusiast discussing Digital India, UPI, and the startup ecosystem.",
    "Agriculture": "Empowering farmers with PM Kisan updates and modern agriculture techniques.",
    "Education": "Passionate about Skill India and the New Education Mission.",
    "Healthcare": "Advocate for Ayushman Bharat and public health awareness.",
    "Infrastructure": "Tracking India's growth via National Highways and Railway expansions.",
    "Lifestyle": "Exploring the beauty of India. Supporting Swachh Bharat initiatives."
}

HEADERS = ["Name", "Handle", "Platform", "Followers", "Following", "Posts", "Bio", "Description", "Language", "Location", "Profile URL", "Email", "Website"]

def get_random_row(niche=None):
    niche = niche or random.choice(list(NICHES.keys()))
    name = random.choice(NAMES)
    platform = random.choice(PLATFORMS)
    handle = f"{name.lower().replace(' ', '_')}_{platform.lower()[:3]}_{random.randint(10,99)}"
    followers = random.choice(["500", "2K", "15K", "120K", "800K", "5M"])
    
    return {
        "Name": name,
        "Handle": handle,
        "Platform": platform,
        "Followers": followers,
        "Following": str(random.randint(100, 2000)),
        "Posts": str(random.randint(50, 1000)),
        "Bio": BIOS[niche],
        "Description": f"Content creator focused on {niche}. Keywords: {', '.join(random.sample(NICHES[niche], 2))}.",
        "Language": random.choice(LANGUAGES),
        "Location": random.choice(LOCATIONS),
        "Profile URL": f"https://{platform.lower()}.com/{handle}",
        "Email": f"{handle}@example.com",
        "Website": f"https://{handle}.com"
    }

def write_csv(filename, data, headers=HEADERS):
    with open(filename, mode='w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Generated: {filename}")


# 1. sample_influencers.csv & .xlsx (100 valid rows)
print("Generating standard datasets...")
valid_data = [get_random_row() for _ in range(100)]
write_csv("sample_influencers.csv", valid_data)

wb = Workbook()
ws = wb.active
ws.title = "Influencers"
ws.append(HEADERS)
for row in valid_data:
    ws.append([row[h] for h in HEADERS])
wb.save("sample_influencers.xlsx")
print("✅ Generated: sample_influencers.xlsx")

# 2. large_dataset.csv (>10MB)
print("Generating large dataset...")
large_data = [get_random_row() for _ in range(150000)]
write_csv("large_dataset.csv", large_data)

# 3. Missing Columns Files
print("Generating missing column datasets...")
write_csv("missing_columns_handle.csv", valid_data[:5], headers=[h for h in HEADERS if h != "Handle"])
write_csv("missing_columns_name.csv", valid_data[:5], headers=[h for h in HEADERS if h != "Name"])
write_csv("missing_columns_platform.csv", valid_data[:5], headers=[h for h in HEADERS if h != "Platform"])
write_csv("missing_columns_followers.csv", valid_data[:5], headers=[h for h in HEADERS if h != "Followers"])

# 4. Invalid Extensions
print("Generating invalid extension files...")
with open("invalid_extension.pdf", "wb") as f: f.write(b"%PDF-1.4\n" + b"A" * 1024 * 1024)
with open("invalid_extension.txt", "w", encoding="utf-8") as f: f.write("This is not a CSV or Excel file.\n" * 50000)
print("✅ Generated: invalid_extension.pdf, invalid_extension.txt")

# 5. duplicate_dataset.csv
print("Generating duplicate dataset...")
dup_data = valid_data[:10].copy()
dup_data.extend(valid_data[:5]) # Add exact duplicates
write_csv("duplicate_dataset.csv", dup_data)

# 6. edge_cases.csv
print("Generating edge cases dataset...")
edge_data = []
# Valid rows
edge_data.extend([get_random_row() for _ in range(20)])

# Missing Name (Invalid)
row = get_random_row(); row["Name"] = ""; edge_data.append(row)
# Missing Handle (Invalid)
row = get_random_row(); row["Handle"] = ""; edge_data.append(row)
# Missing Platform (Invalid - will default to OTHER, but let's make it blank to test normalization)
row = get_random_row(); row["Platform"] = ""; edge_data.append(row)

# Blank Language/Bio
row = get_random_row(); row["Language"] = ""; row["Bio"] = ""; edge_data.append(row)

# Invalid Followers
row = get_random_row(); row["Followers"] = "N/A"; edge_data.append(row)
row = get_random_row(); row["Followers"] = "Unknown"; edge_data.append(row)
row = get_random_row(); row["Followers"] = "-500"; edge_data.append(row) # Negative
row = get_random_row(); row["Followers"] = "Ten Thousand"; edge_data.append(row) # Alphabetic

# Unicode / Emoji / Special Chars
row = get_random_row(); row["Name"] = "🚀 Tech Guru 🇮🇳"; row["Bio"] = "हिंदी में टेक्नोलॉजी! Digital India & Startup India. 🚀🔥"; edge_data.append(row)
row = get_random_row(); row["Bio"] = "SQL Injection: ' OR 1=1 --"; edge_data.append(row)
row = get_random_row(); row["Bio"] = "<script>alert('XSS')</script>"; edge_data.append(row)

# Very Long Bio
row = get_random_row(); row["Bio"] = "A" * 1000 + " This is a massive bio to test database limits."; edge_data.append(row)

# Whitespace values
row = get_random_row(); row["Name"] = "   "; row["Handle"] = "   "; edge_data.append(row) # Should be treated as empty/invalid

# Duplicate Handles (within the same file)
row1 = get_random_row(); row1["Handle"] = "exact_duplicate_handle"; row1["Platform"] = "Instagram"
row2 = get_random_row(); row2["Handle"] = "exact_duplicate_handle"; row2["Platform"] = "Instagram"
edge_data.extend([row1, row2])

write_csv("edge_cases.csv", edge_data)

print("\n🎉 All QA Artifacts generated successfully!")