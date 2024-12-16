import os
import random
import subprocess
from bs4 import BeautifulSoup

# Lista de User-Agents
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.198 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.126 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.5563.111 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Safari/537.36"]

def fetch_and_retry_until_valid(url, user_agent, max_retries=50):
    retries = 0
    while retries < max_retries:
        # Configurar el comando curl
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
            # Ejecutar el comando curl
            result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

            if result.returncode == 0:
                content = result.stdout

                # Verificar el tamaño del contenido
                if len(content) < 20240:  # Menos de 20 KB
                    print("Respuesta demasiado pequeña, posible CAPTCHA. Reintentando...")
                # Verificar patrones específicos en el contenido
                elif "Just a moment..." in content or "cf_chl_opt" in content:
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

def extract():
    # URL de ejemplo (actualizar según sea necesario)
    url = "https://es.indeed.com/jobs?q=Software+Engineer&l=Spain&start=0&sort=date&fromage=14"
    user_agent = random.choice(user_agents)

    print("Iniciando extracción principal...")
    html_content = fetch_and_retry_until_valid(url, user_agent)

    if html_content:
        print("Extracción principal exitosa.")
        return BeautifulSoup(html_content, 'html.parser')
    else:
        print("No se pudo obtener contenido válido en la extracción principal.")
        return None

def fetch_and_save_html_with_validation(titles_vjks_urls):
    os.makedirs("job_pages_validated", exist_ok=True)

    for title, vjk, url in titles_vjks_urls:
        user_agent = random.choice(user_agents)
        print(f"Procesando: {title}")

        # Intentar obtener un HTML válido
        html_content = fetch_and_retry_until_valid(url, user_agent)

        if html_content:
            # Guardar el HTML válido
            sanitized_title = title.replace(" ", "_").replace("/", "_")
            file_name = f"job_pages_validated/{sanitized_title}_{vjk}.html"

            with open(file_name, "w", encoding="utf-8") as file:
                file.write(html_content)
            print(f"HTML válido guardado: {file_name}")
        else:
            print(f"No se pudo obtener HTML válido para: {title}")

def transform_and_build_unique_urls(soup, base_url):
    titles_vjks_urls = set()  # Usamos un conjunto para evitar duplicados
    if soup:
        divs = soup.find_all('div', class_='job_seen_beacon')  # Clase para encontrar los trabajos
        for item in divs:
            # Extraer el título del trabajo
            title_element = item.find('h2', class_='jobTitle')
            title = title_element.text.strip() if title_element else "Título no encontrado"

            # Extraer el identificador `vjk`
            vjk_element = title_element.find('a', {'data-jk': True}) if title_element else None
            vjk = vjk_element['data-jk'] if vjk_element else None

            if vjk:
                # Construir la nueva URL
                new_url = f"{base_url}&vjk={vjk}"
                # Añadir al conjunto para evitar duplicados
                titles_vjks_urls.add((title, vjk, new_url))
            else:
                print(f"Título: {title}, vjk no encontrado")
    else:
        print("No se pudo obtener contenido válido.")
    return list(titles_vjks_urls)  # Convertimos el conjunto de vuelta a lista



# Función para generar la URL de búsqueda
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


# URL base
#base_url = "https://es.indeed.com/jobs?q=Software+Engineer&l=Spain&start=0&sort=date&fromage=14"
base_url = get_url("Data Analyst", "Spain",0)


# Extraer contenido inicial
soup_content = extract()

# Generar URLs únicas
titles_vjks_urls = transform_and_build_unique_urls(soup_content, base_url)

# Descargar HTML validado para cada URL única
fetch_and_save_html_with_validation(titles_vjks_urls)



