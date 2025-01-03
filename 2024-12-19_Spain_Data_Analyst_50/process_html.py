import os
import json
from bs4 import BeautifulSoup

def extract_job_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extraer título
    title_tag = soup.find(string=lambda text: text and '"jobTitle":"' in text)
    title = title_tag.split('"jobTitle":"')[1].split('"')[0] if title_tag else "No especificado"

    # Extraer compañía
    company_tag = soup.find(string=lambda text: text and '"sourceEmployerName":"' in text)
    company = company_tag.split('"sourceEmployerName":"')[1].split('"')[0] if company_tag else "No especificado"

    # Extraer descripción completa del empleo
    description_div = soup.find('div', {'id': 'jobDescriptionText'})
    description = description_div.get_text(strip=True) if description_div else "No especificado"

    # Crear estructura JSON
    return {
        "title": title,
        "company": company,
        "description": description,
        "salary": "No especificado",
        "employment_type": "No especificado"
    }

def process_directory(input_dir):
    jobs = []  # Lista para almacenar todas las ofertas de trabajo

    for filename in os.listdir(input_dir):
        if filename.endswith(".html"):
            with open(os.path.join(input_dir, filename), 'r', encoding='utf-8') as file:
                html_content = file.read()

            job_info = extract_job_info(html_content)
            jobs.append(job_info)

    # Crear el archivo JSON con el nombre del directorio
    output_filename = f"{os.path.basename(input_dir)}.json"
    with open(output_filename, 'w', encoding='utf-8') as json_file:
        json.dump(jobs, json_file, ensure_ascii=False, indent=4)

    print(f"Archivo JSON creado: {output_filename}")

# Cambia 'input_dir' por la ruta del directorio que contiene los HTML
input_dir = input_dir = os.path.join(os.getcwd(), "prueba_html")
process_directory(input_dir)

