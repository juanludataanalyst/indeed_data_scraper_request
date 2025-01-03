import subprocess
import random
from time import sleep
import sys

# Definir las posiciones y las ubicaciones
positions = ["Data Analyst", "Data Engineer"]
locations = ["United Kingdom"]


# Recorre los valores de location y llama al script main.py
for location in locations:
    for position in positions:
        #Utilizamos sys.executable por que si lo hacemos solo con python no carga las librerias del entorno virtual
        command = [sys.executable, "get_data_from_indeed.py", "--role", position, "--location", location]
        print(f"Ejecutando: {' '.join(command)}")
        subprocess.run(command)
        sleep(random.uniform(60, 300))
