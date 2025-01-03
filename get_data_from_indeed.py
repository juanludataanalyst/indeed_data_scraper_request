import os
import random
import subprocess
import argparse
from datetime import date
from bs4 import BeautifulSoup
from time import sleep
import re

def get_data_from_indeed(role, location):


    user_agents = []

    # Generar 10,000 user agents únicos con variaciones en versiones principales, secundarias y de parches
    count = 0
    for major in range(100, 200):  # Versiones principales de Chrome
        for minor in range(0, 10):  # Subversiones
            for patch in range(0, 10):  # Parches
                for build in range(100, 110):  # Variación en el build final
                    if count >= 10000:
                        break
                    user_agents.append(
                        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major}.{minor}.{5735+patch}.{build} Safari/537.36"
                    )
                    count += 1
                if count >= 10000:
                    break
            if count >= 10000:
                break
        if count >= 10000:
            break

#print(f"Se generaron {len(user_agents)} user agents únicos.")

    # List of User-Agents
    #user_agents = [
    #   "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
    #  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
    #    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
    #    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",
    #    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36"
    #]

    def fetch_and_retry_until_valid(url, user_agent, max_retries=100):
        retries = 0
        while retries < max_retries:
            
            command = [
    "curl",
    "-L",
    "-A", user_agent,
    "--compressed",
    "--max-time", "10",
    "--cookie", "",
    "--cookie-jar", "/dev/null",
    "-H", "Referer: https://www.indeed.com/",
    "-H", "Accept-Language: en-US,en;q=0.9",
    "-H", "Connection: keep-alive",
    "--no-keepalive",
    url
]

            try:
                if retries == 0:
                    sleep(random.uniform(1, 5))
                elif 1 <= retries <= 2:
                    sleep(random.uniform(5, 10))  
                elif 3 <= retries <= 5:
                    sleep(random.uniform(10, 20))  
                elif 6 <= retries <= 7:
                    sleep(random.uniform(20, 60))  
                elif 8 <= retries <= 10:
                    sleep(random.uniform(60, 3000))     
                else:  # retries >= 11
                    sleep(random.uniform(3000, 6000))
 


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


    def sanitize_filename(filename):
        """Replaces invalid characters in the filename with underscores."""
        return re.sub(r'[<>:"/\\|?*]', '_', filename)

    def fetch_and_save_html_with_validation(titles_vjks_urls, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        for title, vjk, url in titles_vjks_urls:
            user_agent = random.choice(user_agents)
            print(f"Processing: {title}")

            html_content = fetch_and_retry_until_valid(url, user_agent)

            if html_content:
                sleep(random.uniform(1, 30))
                # Cleaning
                sanitized_title = sanitize_filename(title.replace(" ", "_"))
                file_name = f"{output_dir}/{sanitized_title}_{vjk}.html"

                try:
                    with open(file_name, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    print(f"Valid HTML saved: {file_name}")
                except OSError as e:
                    print(f"Error saving file {file_name}: {e}")
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

    def get_url(position, location, start):
        # URL base por defecto para 'United States'
        base_url = 'https://www.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14'
        
        # Modificar la URL base según el país
        location_urls = {
            "spain": 'https://es.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14',
            "colombia": 'https://co.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14',
            "united kingdom": 'https://uk.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14',
            "canada": 'https://ca.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14',
            "germany": 'https://de.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14',
            "australia": 'https://au.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14',
            "singapore": 'https://sg.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14',
            "india": 'https://in.indeed.com/jobs?q={}&l={}&start={}&sort=date&fromage=14'
        }
        
        # Actualizar la URL base si el país está en el diccionario
        base_url = location_urls.get(location.lower(), base_url)

        return base_url.format(position.replace(' ', '+'), location.replace(' ', '+'), start)


    start = 0
    today = date.today().isoformat()
    while True:
        url = get_url(role, location, start)
        soup = extract(url)

        if not soup:
            print("Could not extract valid content.")
            break

        next_page = soup.find('a', {'aria-label': 'Next Page'})

        output_dir = os.path.join("html_data", f"{today}_{location.replace(' ', '_')}_{role.replace(' ', '_')}_{start}")

        # Crear el directorio si no existe
        os.makedirs(output_dir, exist_ok=True)

        output_dir = f"{today}_{location.replace(' ', '_')}_{role.replace(' ', '_')}_{start}"
        titles_vjks_urls = transform_and_build_unique_urls(soup, url)
        fetch_and_save_html_with_validation(titles_vjks_urls, output_dir)

        if next_page:
            sleep(random.uniform(60, 300))
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
