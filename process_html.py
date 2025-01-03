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

def create_output_directory(subdir_name, output_root):
    """
    Crea un subdirectorio en el directorio de salida basado en el nombre del subdirectorio de origen.
    """
    # Eliminar el sufijo "_x" del nombre del subdirectorio
    base_name = "_".join(subdir_name.split("_")[:-1])
    output_subdir_path = os.path.join(output_root, base_name)
    os.makedirs(output_subdir_path, exist_ok=True)
    return output_subdir_path

def process_html_files_to_array(input_subdir):
    """
    Procesa los archivos HTML de un subdirectorio y devuelve un array de información procesada.
    """
    job_list = []

    for filename in os.listdir(input_subdir):
        if filename.endswith(".html"):
            html_path = os.path.join(input_subdir, filename)
            with open(html_path, 'r', encoding='utf-8') as file:
                html_content = file.read()

            # Extraer información del HTML
            job_info = extract_job_info(html_content)
            job_list.append(job_info)

    return job_list

def process_main_directory(main_dir):
    """
    Procesa todos los subdirectorios en el directorio principal.
    """
    # Ruta de salida al mismo nivel que el directorio `html_data`
    output_root = os.path.join(os.path.dirname(main_dir), "json_output")
    os.makedirs(output_root, exist_ok=True)

    for subdir_name in os.listdir(main_dir):
        subdir_path = os.path.join(main_dir, subdir_name)

        # Procesar solo directorios
        if os.path.isdir(subdir_path):
            # Crear el subdirectorio de salida
            output_subdir = create_output_directory(subdir_name, output_root)

            # Procesar archivos HTML en el subdirectorio
            job_array = process_html_files_to_array(subdir_path)

            # Generar nombre del archivo JSON de salida
            output_filename = os.path.join(output_subdir, f"{subdir_name}.json")

            # Guardar el array en el archivo JSON
            with open(output_filename, 'w', encoding='utf-8') as json_file:
                json.dump(job_array, json_file, ensure_ascii=False, indent=4)

            print(f"Archivo JSON creado: {output_filename}")

# Ruta del directorio principal que contiene los subdirectorios con HTML
main_dir = os.path.join(os.getcwd(), "html_data")
process_main_directory(main_dir)


if __name__ == "__main__":
    # Ruta del directorio principal que contiene los subdirectorios con HTML
    main_dir = os.path.join(os.getcwd(), "html_data")
    process_main_directory(main_dir)