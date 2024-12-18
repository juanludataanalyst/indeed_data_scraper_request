# 🔧 Indeed Data Scraper

Welcome to the **Indeed Data Scraper**! This Python-based project is designed to scrape job postings from Indeed for specific roles and locations using **Requests** and Beautiful Soup and . It collects the HTML of individual job postings and traverses all available pages from the last 14 days, allowing users to extract detailed descriptions and all relevant data from every posting.

---

## 🌎 Supported Countries
The scraper currently supports the following countries:

- 🇪🇸 Spain
- 🇬🇧 United Kingdom
- 🇨🇦 Canada
- 🇩🇪 Germany
- 🇦🇺 Australia
- 🇸🇬 Singapore
- 🇮🇳 India
- 🇨🇴 Colombia

---

## 🔍 Features

- Developed using **Requests** and **Beautiful Soup** for efficient and reliable web scraping.  
- Scrapes job postings for a given role and location.  
- Collects and saves the HTML content of each job posting.  
- Traverses all available pages until no more results are found.  
- Extracts job postings from the last **14 days** for relevant and recent data.  
- With the current setup, it averages scraping **1000 job postings** in 6 hours without being blocked. This number can increase if smaller delays are configured between requests, but risk of being blocked increases.


---

## 🛠️ Installation

To get started with this project, follow these steps:

### 1. Clone the Repository
```bash
https://github.com/juanludataanalyst/indeed-data-scraper.git
cd indeed-data-scraper
```

### 2. Set Up the Virtual Environment
Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate # On Windows: .\env\Scripts\activate
```

### 3. Install Dependencies
Install the required Python libraries:
```bash
pip install -r requirements.txt
```

---

## 🔧 Usage

Run the script with the following syntax:
```bash
python main.py --role "<Job Title>" --location "<Country Name>"
```
### Example
To scrape job postings for **Data Scientist** roles in **United States**:
```bash
python main.py --role "Data Scientist" --location "United States"
```

---

## 🛠️ Key Configuration Details

- **Scraping Time Frame**: Captures job postings from the past **14 days**.
- **Blocking Avoidance**: Utilizes random user agents and delays to prevent being blocked.

---

## 📚 Contributing
Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/your-feature`).
3. Commit your changes (`git commit -m "Add your message"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Open a pull request.

---

## 🛤 Disclaimer
This project is for **educational purposes only**. Ensure that you comply with Indeed’s [terms of service](https://www.indeed.com/legal) when using this tool.

---

## 🎨 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## 🔗 Connect
Feel free to reach out or follow the project on GitHub:

- Email: juanludataanalyst@gmail.com

