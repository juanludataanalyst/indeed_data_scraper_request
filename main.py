import os
import random
import subprocess
import argparse
from datetime import date
from bs4 import BeautifulSoup
from time import sleep

def get_data_from_indeed(role, location):
    # List of User-Agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36"
    ]

    def fetch_and_retry_until_valid(url, user_agent, max_retries=100):
        retries = 0
        while retries < max_retries:
            command = [
                "curl",
                "-L",  # Follow redirects
                "-A", user_agent,  # Randomly chosen User-Agent
                "--compressed",  # Allow Gzip compression
                "--max-time", "10",  # Maximum time for the request
                "--cookie", "",  # Send an empty cookie
                "--cookie-jar", "/dev/null",  # Do not save cookies
                "-H", "Referer: https://www.indeed.com/",  # Referer to simulate browsing
                "-H", "Accept-Language: en-US,en;q=0.9",  # Accepted language
                "-H", "Connection: keep-alive",  # Keep connection open
                "--no-keepalive",  # Disable persistent connections after the request
                url  # Target URL
            ]

            try:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

                if result.returncode == 0:
                    content = result.stdout

                    if len(content) < 50240:  # Less than 50 KB
                        print("Response too small, possible CAPTCHA. Retrying...")
                    elif "Just a moment..." in content or "cf_chl_opt" in content:
                        print("CAPTCHA detected in the response. Retrying...")
                    else:
                        return content  # Valid HTML
                else:
                    print(f"Request error: {result.stderr}")

            except Exception as e:
                print(f"Error: {e}")

            retries += 1
            print(f"Retry {retries}/{max_retries}...")

        print("Maximum retries reached. Could not fetch valid HTML.")
        return None

    def extract(url):
        user_agent = random.choice(user_agents)
        print(f"Extracting data from: {url}")
        html_content = fetch_and_retry_until_valid(url, user_agent)

        if html_content:
            return BeautifulSoup(html_content, 'html.parser')
        else:
            return None

    def fetch_and_save_html_with_validation(titles_vjks_urls, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        for title, vjk, url in titles_vjks_urls:
            user_agent = random.choice(user_agents)
            print(f"Processing: {title}")

            html_content = fetch_and_retry_until_valid(url, user_agent)

            if html_content:
                sleep(random.uniform(1, 5))
                sanitized_title = title.replace(" ", "_").replace("/", "_")
                file_name = f"{output_dir}/{sanitized_title}_{vjk}.html"

                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(html_content)
                print(f"Valid HTML saved: {file_name}")
            else:
                print(f"Could not fetch valid HTML for: {title}")

    def transform_and_build_unique_urls(soup, base_url):
        titles_vjks_urls = set()
        if soup:
            divs = soup.find_all('div', class_='job_seen_beacon')
            for item in divs:
                title_element = item.find('h2', class_='jobTitle')
                title = title_element.text.strip() if title_element else "Title not found"

                vjk_element = title_element.find('a', {'data-jk': True}) if title_element else None
                vjk = vjk_element['data-jk'] if vjk_element else None

                if vjk:
                    new_url = f"{base_url}&vjk={vjk}"
                    titles_vjks_urls.add((title, vjk, new_url))
        return list(titles_vjks_urls)

    def get_url(role, location, start):
        base_url = 'https://www.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14'
        return base_url.format(role.replace(' ', '+'), location.replace(' ', '+'), start)

    start = 0
    today = date.today().isoformat()
    while True:
        url = get_url(role, location, start)
        soup = extract(url)

        if not soup:
            print("Could not extract valid content.")
            break

        next_page = soup.find('a', {'aria-label': 'Next Page'})
        output_dir = f"{today}_{location.replace(' ', '_')}_{role.replace(' ', '_')}_{start}"
        titles_vjks_urls = transform_and_build_unique_urls(soup, url)
        fetch_and_save_html_with_validation(titles_vjks_urls, output_dir)

        if next_page:
            sleep(random.uniform(1, 5))
            start += 10
        else:
            print("No more pages available.")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch job data from Indeed.")
    parser.add_argument("--role", type=str, required=True, help="Job role to search for.")
    parser.add_argument("--location", type=str, required=True, help="Job location to search for.")
    args = parser.parse_args()

    get_data_from_indeed(args.role, args.location)
