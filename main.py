import os
import random
import subprocess
from bs4 import BeautifulSoup


def get_data_from_indeed(role, location):
    # Lista de User-Agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36"
    ]

    def fetch_and_retry_until_valid(url, user_agent, max_retries=50):
        retries = 0
        while retries < max_retries:
            command = [
                "curl",
                "-L",  # Seguir redirecciones
                "-A", user_agent,  # User-Agent
                "-s",  # Descargar en silencio
                "--compressed",  # Permitir compresión
                "--max-time", "10",  # Limitar el tiempo de la solicitud
                url
            ]

            try:
                result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

                if result.returncode == 0:
                    content = result.stdout

                    # Verificar patrones específicos en el contenido
                    if "Just a moment..." in content or "cf_chl_opt" in content:
                        print("Se detectó un CAPTCHA en la respuesta. Reintentando...")
                    else:
                        return content  # HTML válido
                else:
                    print(f"Error en la solicitud: {result.stderr}")

            except Exception as e:
                print(f"Error: {e}")

            retries += 1
            print(f"Reintento {retries}/{max_retries}...")

        print("Se alcanzó el máximo de reintentos. No se pudo obtener un HTML válido.")
        return None

    def extract(url):
        user_agent = random.choice(user_agents)
        print(f"Extrayendo datos de: {url}")
        html_content = fetch_and_retry_until_valid(url, user_agent)

        if html_content:
            return BeautifulSoup(html_content, 'html.parser')
        else:
            return None

    def fetch_and_save_html_with_validation(titles_vjks_urls):
        os.makedirs("job_pages_validated", exist_ok=True)

        for title, vjk, url in titles_vjks_urls:
            user_agent = random.choice(user_agents)
            print(f"Procesando: {title}")

            html_content = fetch_and_retry_until_valid(url, user_agent)

            if html_content:
                sanitized_title = title.replace(" ", "_").replace("/", "_")
                file_name = f"job_pages_validated/{sanitized_title}_{vjk}.html"

                with open(file_name, "w", encoding="utf-8") as file:
                    file.write(html_content)
                print(f"HTML válido guardado: {file_name}")
            else:
                print(f"No se pudo obtener HTML válido para: {title}")

    def transform_and_build_unique_urls(soup, base_url):
        titles_vjks_urls = set()
        if soup:
            divs = soup.find_all('div', class_='job_seen_beacon')
            for item in divs:
                title_element = item.find('h2', class_='jobTitle')
                title = title_element.text.strip() if title_element else "Título no encontrado"

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
    while True:
        url = get_url(role, location, start)
        soup = extract(url)

        if not soup:
            print("No se pudo extraer contenido válido.")
            break

        next_page = soup.find('a', {'aria-label': 'Next Page'})
        titles_vjks_urls = transform_and_build_unique_urls(soup, url)
        fetch_and_save_html_with_validation(titles_vjks_urls)

        if next_page:
            start += 10
        else:
            print("No hay más páginas disponibles.")
            break

get_data_from_indeed("Data Analyst", "United States")
