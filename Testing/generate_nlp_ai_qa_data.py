import csv
import os

DATASETS = {
    "nlp_test_dataset.csv": [
        {"Name": "Rahul Tech", "Handle": "rahul_tech", "Platform": "YouTube", "Followers": "150K", "Following": "500", "Posts": "320", "Bio": "Tech enthusiast discussing Digital India, UPI, and the startup ecosystem.", "Description": "Building a Viksit Bharat through innovation and technology.", "Language": "Hindi", "Location": "New Delhi", "Profile URL": "https://youtube.com/rahul_tech", "Email": "rahul@example.com", "Website": "https://rahul.com"},
        {"Name": "Priya Krishi", "Handle": "priya_krishi", "Platform": "Instagram", "Followers": "50K", "Following": "1200", "Posts": "890", "Bio": "Empowering farmers with PM Kisan updates and modern agriculture techniques.", "Description": "Jai Jawan Jai Kisan. Supporting Swaminathan policies and organic farming.", "Language": "Hindi", "Location": "Pune", "Profile URL": "https://instagram.com/priya_krishi", "Email": "priya@example.com", "Website": ""},
        {"Name": "Amit Finance", "Handle": "amit_finance", "Platform": "LinkedIn", "Followers": "800K", "Following": "3000", "Posts": "150", "Bio": "Demystifying finance, mutual funds, and the Indian economy.", "Description": "Helping you achieve financial freedom through smart investments and Digital Payments.", "Language": "English", "Location": "Mumbai", "Profile URL": "https://linkedin.com/in/amit_finance", "Email": "amit@example.com", "Website": "https://amitfinance.com"},
        {"Name": "Sneha Health", "Handle": "sneha_health", "Platform": "Facebook", "Followers": "200K", "Following": "800", "Posts": "1200", "Bio": "Advocate for Ayushman Bharat and public health awareness.", "Description": "Promoting Yoga, fitness, and mental wellness for a healthier India.", "Language": "Mixed", "Location": "Bengaluru", "Profile URL": "https://facebook.com/sneha_health", "Email": "sneha@example.com", "Website": ""},
        {"Name": "Vikram Infra", "Handle": "vikram_infra", "Platform": "Twitter", "Followers": "500K", "Following": "200", "Posts": "5000", "Bio": "Tracking India's growth via National Highways and Railway expansions.", "Description": "Proud of Make in India and Smart Cities initiatives.", "Language": "English", "Location": "Ahmedabad", "Profile URL": "https://twitter.com/vikram_infra", "Email": "vikram@example.com", "Website": "https://vikraminfra.com"},
    ],
    "unicode_dataset.csv": [
        {"Name": "🚀 Tech Guru 🇮🇳", "Handle": "tech_guru_99", "Platform": "Instagram", "Followers": "1.2M", "Following": "100", "Posts": "450", "Bio": "हिंदी में टेक्नोलॉजी! Digital India & Startup India. 🚀🔥", "Description": "UPI से भुगतान अब और भी आसान। #DigitalIndia #ViksitBharat", "Language": "Hindi", "Location": "Delhi", "Profile URL": "https://instagram.com/tech_guru_99", "Email": "tech@example.com", "Website": ""},
        {"Name": "किसान मित्र", "Handle": "kisan_mitra_01", "Platform": "YouTube", "Followers": "500K", "Following": "50", "Posts": "200", "Bio": "प्रधानमंत्री किसान सम्मान निधि की पूरी जानकारी। 🚜", "Description": "भारत का विकास कृषि से ही संभव है। PM Kisan योजना पर चर्चा।", "Language": "Hindi", "Location": "Lucknow", "Profile URL": "https://youtube.com/kisan_mitra", "Email": "kisan@example.com", "Website": ""},
        {"Name": "HTML Tester", "Handle": "html_test", "Platform": "Twitter", "Followers": "10K", "Following": "10", "Posts": "50", "Bio": "<script>alert('XSS')</script> Testing HTML stripping.", "Description": "Visit my site: <a href='https://test.com'>Test</a>. Email: test@test.com. Call: 9876543210.", "Language": "English", "Location": "Chennai", "Profile URL": "https://twitter.com/html_test", "Email": "html@example.com", "Website": "https://test.com"},
        {"Name": "Empty Bio User", "Handle": "empty_bio_user", "Platform": "LinkedIn", "Followers": "5K", "Following": "500", "Posts": "10", "Bio": "", "Description": "", "Language": "Unknown", "Location": "Kolkata", "Profile URL": "https://linkedin.com/in/empty", "Email": "empty@example.com", "Website": ""},
        {"Name": "Long Bio User", "Handle": "long_bio_user", "Platform": "Facebook", "Followers": "20K", "Following": "200", "Posts": "100", "Bio": "A" * 800 + " This is a massive bio to test NLP tokenization limits and database storage.", "Description": "Skill India and National Education Policy are game changers.", "Language": "English", "Location": "Jaipur", "Profile URL": "https://facebook.com/long_bio", "Email": "long@example.com", "Website": ""},
    ],
    "ai_test_dataset.csv": [
        {"Name": "Govt Supporter A", "Handle": "govt_support_a", "Platform": "YouTube", "Followers": "2M", "Following": "10", "Posts": "1000", "Bio": "Strongly support Digital India, Make in India, and Viksit Bharat. The government is doing great work.", "Description": "Highlighting the success of Ayushman Bharat and Railway Development.", "Language": "Hindi", "Location": "Delhi", "Profile URL": "https://youtube.com/govt_a", "Email": "govt_a@example.com", "Website": ""},
        {"Name": "Neutral Observer B", "Handle": "neutral_obs_b", "Platform": "Twitter", "Followers": "100K", "Following": "500", "Posts": "5000", "Bio": "Discussing politics, economy, and society. No specific agenda.", "Description": "Analyzing policies like NEP 2020 and Swachh Bharat objectively.", "Language": "English", "Location": "Mumbai", "Profile URL": "https://twitter.com/neutral_b", "Email": "neutral_b@example.com", "Website": ""},
        {"Name": "Non-Govt Critic C", "Handle": "critic_c", "Platform": "Instagram", "Followers": "500K", "Following": "200", "Posts": "800", "Bio": "Questioning the implementation of various schemes. Demanding accountability.", "Description": "Focus on grassroots issues, not just Highway Infrastructure or Startup India hype.", "Language": "Mixed", "Location": "Kolkata", "Profile URL": "https://instagram.com/critic_c", "Email": "critic_c@example.com", "Website": ""},
    ],
    "retry_test_dataset.csv": [
        {"Name": "Retry Test 1", "Handle": "retry_test_1", "Platform": "Instagram", "Followers": "10K", "Following": "100", "Posts": "50", "Bio": "Testing AI retry logic with Digital India content.", "Description": "UPI and Skill India mentions.", "Language": "English", "Location": "Delhi", "Profile URL": "https://instagram.com/retry_1", "Email": "retry1@example.com", "Website": ""},
        {"Name": "Retry Test 2", "Handle": "retry_test_2", "Platform": "YouTube", "Followers": "50K", "Following": "200", "Posts": "100", "Bio": "Testing AI retry logic with PM Kisan content.", "Description": "Agriculture and farmer welfare.", "Language": "Hindi", "Location": "Pune", "Profile URL": "https://youtube.com/retry_2", "Email": "retry2@example.com", "Website": ""},
    ]
}

def write_csv(filename, data):
    if not data: return
    headers = list(data[0].keys())
    with open(filename, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    print(f"✅ Generated: {filename}")

if __name__ == "__main__":
    for filename, data in DATASETS.items():
        write_csv(filename, data)
    print("\n🎉 All NLP/AI QA Artifacts generated successfully!")