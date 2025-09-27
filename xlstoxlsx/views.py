from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, View
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.core.files.base import ContentFile
from django.conf import settings
import os
import json
import xlrd
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
import tempfile
import logging
from bs4 import BeautifulSoup
import re
from urllib.parse import unquote

from .models import ConversionRecord

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
    """Vista principal para mostrar el formulario de conversión"""
    template_name = 'xlstoxlsx/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['recent_conversions'] = ConversionRecord.objects.filter(
            conversion_successful=True
        )[:5]  # Últimas 5 conversiones exitosas
        return context


class ConvertView(View):
    """Vista para manejar la conversión de archivos XLS a XLSX"""

    def post(self, request):
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se ha seleccionado ningún archivo'
            }, status=400)

        file = request.FILES['file']

        # Validar que sea un archivo XLS
        if not file.name.lower().endswith('.xls'):
            return JsonResponse({
                'success': False,
                'error': 'El archivo debe tener extensión .xls'
            }, status=400)

        # Validar tamaño del archivo (máximo 50MB)
        if file.size > 50 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': 'El archivo es demasiado grande. Máximo 50MB permitido.'
            }, status=400)

        try:
            # Crear registro de conversión
            conversion_record = ConversionRecord.objects.create(
                original_file=file,
                original_filename=file.name,
                file_size=file.size
            )

            # Detectar el formato del archivo
            file_format = self.detect_format(conversion_record)

            # Realizar la conversión según el formato detectado
            if file_format == 'html':
                converted_filename = self.convert_html_xls_to_xlsx(
                    conversion_record)
                format_message = 'Archivo HTML convertido exitosamente'
            elif file_format == 'xls':
                converted_filename = self.convert_xls_to_xlsx(
                    conversion_record)
                format_message = 'Archivo XLS convertido exitosamente'
            else:
                return JsonResponse({
                    'success': False,
                    'error': 'Formato de archivo no soportado. Debe ser XLS o HTML con extensión .xls'
                }, status=400)

            if converted_filename:
                conversion_record.converted_filename = converted_filename
                conversion_record.conversion_successful = True
                conversion_record.save()

                return JsonResponse({
                    'success': True,
                    'message': format_message,
                    'download_url': conversion_record.get_download_url(),
                    'converted_filename': converted_filename,
                    'file_format': file_format
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': conversion_record.error_message or 'Error durante la conversión'
                }, status=500)

        except Exception as e:
            logger.error(f"Error durante la conversión: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': f'Error inesperado: {str(e)}'
            }, status=500)

    def detect_format(self, conversion_record):
        """Detecta si el archivo es realmente XLS o HTML con extensión .xls"""
        try:
            with open(conversion_record.original_file.path, 'rb') as f:
                # Leer los primeros bytes del archivo
                header = f.read(1024)

                # Intentar decodificar como texto para buscar HTML
                try:
                    header_text = header.decode('utf-8', errors='ignore')
                    # Buscar indicadores de HTML
                    if any(tag in header_text.lower() for tag in ['<html', '<!doctype', '<meta', '<table']):
                        return 'html'
                except:
                    pass

                # Verificar si es un archivo XLS real (comienza con la signatura de OLE)
                if header[:8] == b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1':
                    return 'xls'

                # Si no es ninguno, intentar abrir con xlrd para estar seguro
                try:
                    xlrd.open_workbook(conversion_record.original_file.path)
                    return 'xls'
                except:
                    # Si falla xlrd, probablemente sea HTML
                    return 'html'

        except Exception as e:
            logger.error(f"Error detectando formato: {str(e)}")
            return 'unknown'

    def convert_html_xls_to_xlsx(self, conversion_record):
        """Convierte un archivo HTML con extensión XLS a XLSX"""
        try:
            # Leer el contenido HTML
            with open(conversion_record.original_file.path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Parsear el HTML
            soup = BeautifulSoup(html_content, 'html.parser')

            # Buscar la tabla principal
            table = soup.find('table')
            if not table:
                raise Exception(
                    "No se encontró ninguna tabla en el archivo HTML")

            # Crear un nuevo workbook XLSX
            workbook_xlsx = Workbook()
            sheet_xlsx = workbook_xlsx.active
            sheet_xlsx.title = "Datos Convertidos"

            # Lista para almacenar información de fusión de celdas
            merge_ranges = []

            # Extraer datos de la tabla
            rows = table.find_all('tr')
            current_row = 1

            # Primera pasada: escribir datos y recopilar información de fusión
            for row_idx, row in enumerate(rows):
                cells = row.find_all(['td', 'th'])
                current_col = 1

                for cell_idx, cell in enumerate(cells):
                    # Obtener el texto de la celda
                    cell_text = cell.get_text(strip=True)

                    # Manejar colspan y rowspan
                    colspan = int(cell.get('colspan', 1))
                    rowspan = int(cell.get('rowspan', 1))

                    # Escribir el valor en la celda solo si no está fusionada
                    try:
                        excel_cell = sheet_xlsx.cell(
                            row=current_row, column=current_col, value=cell_text)

                        # Aplicar formato si es header (th o primera fila)
                        if cell.name == 'th' or row_idx == 0:
                            excel_cell.font = Font(bold=True, color="FFFFFF")
                            excel_cell.fill = PatternFill(
                                start_color="0065A9", end_color="0065A9", fill_type="solid")
                            excel_cell.alignment = Alignment(
                                horizontal="center", vertical="center")

                        # Aplicar estilos basados en el background-color del HTML
                        style_attr = cell.get('style', '')
                        if 'background:' in style_attr or 'background-color:' in style_attr:
                            # Extraer color de fondo
                            bg_match = re.search(
                                r'background(?:-color)?:\s*([^;]+)', style_attr)
                            if bg_match:
                                bg_color = bg_match.group(1).strip()
                                if '#' in bg_color:
                                    # Convertir color hex para openpyxl
                                    hex_color = bg_color.replace('#', '')
                                    if len(hex_color) == 6:
                                        excel_cell.fill = PatternFill(
                                            start_color=hex_color, end_color=hex_color, fill_type="solid")

                        # Agregar información de fusión si es necesario
                        if colspan > 1 or rowspan > 1:
                            end_row = current_row + rowspan - 1
                            end_col = current_col + colspan - 1
                            merge_ranges.append(
                                (current_row, current_col, end_row, end_col))

                    except Exception as e:
                        logger.warning(
                            f"Error escribiendo celda en fila {current_row}, columna {current_col}: {str(e)}")

                    # Avanzar columna por el colspan
                    current_col += colspan

                current_row += 1

            # Segunda pasada: aplicar fusiones de celdas
            for start_row, start_col, end_row, end_col in merge_ranges:
                try:
                    if end_row > start_row or end_col > start_col:
                        sheet_xlsx.merge_cells(
                            start_row=start_row,
                            start_column=start_col,
                            end_row=end_row,
                            end_column=end_col
                        )
                except Exception as e:
                    logger.warning(
                        f"Error fusionando celdas ({start_row},{start_col})-({end_row},{end_col}): {str(e)}")

            # Ajustar ancho de columnas de forma segura
            self._adjust_column_widths(sheet_xlsx)

            # Generar nombre del archivo convertido
            base_name = os.path.splitext(
                conversion_record.original_filename)[0]
            converted_filename = f"{base_name}_converted.xlsx"

            # Crear directorio si no existe
            converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
            os.makedirs(converted_dir, exist_ok=True)

            # Guardar el archivo convertido
            converted_path = os.path.join(converted_dir, converted_filename)
            workbook_xlsx.save(converted_path)

            # Actualizar el registro con el archivo convertido
            with open(converted_path, 'rb') as f:
                conversion_record.converted_file.save(
                    converted_filename,
                    ContentFile(f.read()),
                    save=False
                )

            return converted_filename

        except Exception as e:
            error_msg = f"Error en la conversión HTML: {str(e)}"
            conversion_record.error_message = error_msg
            conversion_record.save()
            logger.error(error_msg)
            return None

    def _adjust_column_widths(self, sheet):
        """Ajusta el ancho de las columnas de forma segura, evitando problemas con MergedCells"""
        try:
            from openpyxl.cell.cell import MergedCell

            for col_idx in range(1, sheet.max_column + 1):
                max_length = 0
                column_letter = sheet.cell(row=1, column=col_idx).column_letter

                # Revisar todas las celdas de la columna
                for row_idx in range(1, sheet.max_row + 1):
                    cell = sheet.cell(row=row_idx, column=col_idx)

                    # Solo procesar celdas normales, no MergedCells
                    if not isinstance(cell, MergedCell) and cell.value is not None:
                        try:
                            cell_length = len(str(cell.value))
                            if cell_length > max_length:
                                max_length = cell_length
                        except Exception:
                            continue

                # Establecer ancho ajustado
                adjusted_width = min(max(max_length + 2, 10), 50)
                sheet.column_dimensions[column_letter].width = adjusted_width

        except Exception as e:
            logger.warning(f"Error ajustando ancho de columnas: {str(e)}")
            # Si falla, establecer un ancho por defecto
            try:
                for col_idx in range(1, sheet.max_column + 1):
                    column_letter = sheet.cell(
                        row=1, column=col_idx).column_letter
                    sheet.column_dimensions[column_letter].width = 15
            except Exception:
                pass

    def convert_xls_to_xlsx(self, conversion_record):
        """Convierte un archivo XLS real a XLSX"""
        try:
            # Leer el archivo XLS
            workbook_xls = xlrd.open_workbook(
                conversion_record.original_file.path)

            # Crear un nuevo workbook XLSX
            workbook_xlsx = Workbook()
            # Remover la hoja por defecto
            workbook_xlsx.remove(workbook_xlsx.active)

            # Convertir cada hoja
            for sheet_index in range(workbook_xls.nsheets):
                sheet_xls = workbook_xls.sheet_by_index(sheet_index)
                sheet_xlsx = workbook_xlsx.create_sheet(title=sheet_xls.name)

                # Copiar datos celda por celda
                for row in range(sheet_xls.nrows):
                    for col in range(sheet_xls.ncols):
                        cell_value = sheet_xls.cell_value(row, col)

                        # Manejar diferentes tipos de datos
                        if sheet_xls.cell_type(row, col) == xlrd.XL_CELL_DATE:
                            # Convertir fecha
                            import datetime
                            date_value = xlrd.xldate_as_datetime(
                                cell_value, workbook_xls.datemode)
                            cell_value = date_value

                        # Escribir en la nueva hoja (las celdas en openpyxl son 1-indexadas)
                        sheet_xlsx.cell(row=row+1, column=col +
                                        1, value=cell_value)

            # Generar nombre del archivo convertido
            base_name = os.path.splitext(
                conversion_record.original_filename)[0]
            converted_filename = f"{base_name}_converted.xlsx"

            # Crear directorio si no existe
            converted_dir = os.path.join(settings.MEDIA_ROOT, 'converted')
            os.makedirs(converted_dir, exist_ok=True)

            # Guardar el archivo convertido
            converted_path = os.path.join(converted_dir, converted_filename)
            workbook_xlsx.save(converted_path)

            # Actualizar el registro con el archivo convertido
            with open(converted_path, 'rb') as f:
                conversion_record.converted_file.save(
                    converted_filename,
                    ContentFile(f.read()),
                    save=False
                )

            return converted_filename

        except Exception as e:
            error_msg = f"Error en la conversión XLS: {str(e)}"
            conversion_record.error_message = error_msg
            conversion_record.save()
            logger.error(error_msg)
            return None


class DownloadView(View):
    """Vista para descargar archivos convertidos"""

    def get(self, request, filename):
        try:
            # Decodificar el nombre del archivo en caso de que esté URL-encoded
            decoded_filename = unquote(filename)

            logger.info(
                f"Buscando archivo: original='{filename}', decoded='{decoded_filename}'")

            # Buscar el registro de conversión con ambos nombres por si acaso
            conversion_record = None

            # Primero intentar con el nombre decodificado (tomar el más reciente si hay múltiples)
            try:
                conversion_record = ConversionRecord.objects.filter(
                    converted_filename=decoded_filename,
                    conversion_successful=True
                ).order_by('-created_at').first()
            except Exception:
                conversion_record = None

            if not conversion_record:
                # Si no se encuentra, intentar con el nombre original
                try:
                    conversion_record = ConversionRecord.objects.filter(
                        converted_filename=filename,
                        conversion_successful=True
                    ).order_by('-created_at').first()
                except Exception:
                    conversion_record = None

            if not conversion_record:
                logger.error(
                    f"No se encontró registro para: '{filename}' ni '{decoded_filename}'")
                raise Http404("Archivo no encontrado")

            if not conversion_record.converted_file:
                logger.error(
                    f"Registro encontrado pero sin archivo: {conversion_record.id}")
                raise Http404("Archivo no encontrado")

            # Preparar la respuesta de descarga
            response = HttpResponse(
                conversion_record.converted_file.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            # Usar el nombre decodificado para la descarga
            safe_filename = decoded_filename.replace('"', '\\"')
            response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'

            logger.info(f"Descarga exitosa: {safe_filename}")
            return response

        except Http404:
            raise
        except Exception as e:
            logger.error(f"Error en descarga: {str(e)}")
            raise Http404("Archivo no encontrado")
