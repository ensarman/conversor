#!/usr/bin/env python

from django.urls import reverse
from xlstoxlsx.models import ConversionRecord
import os
import sys
import django

# Configurar Django
sys.path.insert(0, '/mnt/extra/varios/dev/conversiones')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conversiones.settings')
django.setup()


def test_download():
    print("=== Prueba de funcionalidad de descarga ===")

    # Obtener todos los registros de conversión exitosos
    successful_records = ConversionRecord.objects.filter(
        conversion_successful=True).order_by('-created_at')

    print(f"Registros exitosos encontrados: {successful_records.count()}")

    # Solo los primeros 5
    for i, record in enumerate(successful_records[:5], 1):
        print(f"\n{i}. ID: {record.id}")
        print(f"   Archivo original: {record.original_filename}")
        print(f"   Archivo convertido: {record.converted_filename}")
        print(f"   Creado: {record.created_at}")
        print(f"   Éxito: {record.conversion_successful}")

        # Verificar si el archivo convertido existe
        if record.converted_file and hasattr(record.converted_file, 'path'):
            file_path = record.converted_file.path
            exists = os.path.exists(file_path)
            print(f"   Archivo existe: {exists}")
            if exists:
                size = os.path.getsize(file_path)
                print(f"   Tamaño: {size} bytes")
        else:
            print(f"   Sin archivo convertido asociado")

        # Generar URL de descarga
        try:
            download_url = record.get_download_url()
            print(f"   URL de descarga: {download_url}")
        except Exception as e:
            print(f"   Error generando URL: {e}")


if __name__ == "__main__":
    test_download()
