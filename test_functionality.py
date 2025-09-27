#!/usr/bin/env python

import requests
import time


def test_complete_functionality():
    print("=== Prueba Completa de Funcionalidad ===")

    base_url = "http://localhost:8004"

    # 1. Verificar que la página principal carga
    print("\n1. Probando página principal...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✓ Página principal carga correctamente")
        else:
            print(f"✗ Error en página principal: {response.status_code}")
    except Exception as e:
        print(f"✗ Error conectando al servidor: {e}")
        return

    # 2. Probar descarga de un archivo existente
    print("\n2. Probando descarga de archivo...")
    download_url = "/download/OPERACION-CAMPO-SEGUIMIENTO-VARIACIONES-CENSALES%20(26092025%201610)_converted.xlsx"
    try:
        response = requests.get(f"{base_url}{download_url}")
        if response.status_code == 200:
            content_length = len(response.content)
            print(f"✓ Descarga exitosa - {content_length} bytes")

            # Verificar que es un archivo Excel válido
            # Los archivos .xlsx son ZIP
            if response.content.startswith(b'PK'):
                print("✓ El archivo descargado parece ser un Excel válido")
            else:
                print("⚠ El archivo descargado podría no ser un Excel válido")

        else:
            print(f"✗ Error en descarga: {response.status_code}")
            print(f"Contenido de respuesta: {response.text[:200]}")
    except Exception as e:
        print(f"✗ Error en descarga: {e}")

    # 3. Probar descarga de un archivo inexistente
    print("\n3. Probando descarga de archivo inexistente...")
    try:
        response = requests.get(
            f"{base_url}/download/archivo_que_no_existe.xlsx")
        if response.status_code == 404:
            print("✓ Error 404 devuelto correctamente para archivo inexistente")
        else:
            print(f"⚠ Código de respuesta inesperado: {response.status_code}")
    except Exception as e:
        print(f"✗ Error en prueba de archivo inexistente: {e}")


if __name__ == "__main__":
    test_complete_functionality()
