#!/usr/bin/env python
"""
Script de debug para revisar los registros de conversión en la base de datos
"""

from xlstoxlsx.models import ConversionRecord
import os
import sys
import django

# Configurar Django
sys.path.append('/mnt/extra/varios/dev/conversiones')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conversiones.settings')
django.setup()


def debug_conversions():
    print("=== REGISTROS DE CONVERSIÓN ===")

    conversions = ConversionRecord.objects.all().order_by('-created_at')

    if not conversions.exists():
        print("No hay registros de conversión.")
        return

    for i, conv in enumerate(conversions, 1):
        print(f"\n{i}. ID: {conv.id}")
        print(f"   Original: {conv.original_filename}")
        print(f"   Convertido: {conv.converted_filename}")
        print(f"   Exitoso: {conv.conversion_successful}")
        print(f"   Fecha: {conv.created_at}")
        print(f"   Archivo existe: {bool(conv.converted_file)}")
        if conv.converted_file:
            print(f"   Ruta archivo: {conv.converted_file.name}")
        if conv.error_message:
            print(f"   Error: {conv.error_message}")

        # Generar URL de descarga
        if conv.conversion_successful and conv.converted_file:
            try:
                download_url = conv.get_download_url()
                print(f"   URL descarga: {download_url}")
            except Exception as e:
                print(f"   Error generando URL: {e}")

    print(f"\nTotal: {conversions.count()} registros")


if __name__ == '__main__':
    debug_conversions()
