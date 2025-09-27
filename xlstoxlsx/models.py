from django.db import models
from django.urls import reverse
import os


def upload_to(instance, filename):
    """Función para definir la ruta donde se guardará el archivo subido"""
    return os.path.join('uploads', filename)


class ConversionRecord(models.Model):
    """Modelo para registrar las conversiones de archivos XLS a XLSX"""

    original_file = models.FileField(
        upload_to=upload_to,
        verbose_name="Archivo Original (.xls)"
    )

    converted_file = models.FileField(
        upload_to='converted/',
        verbose_name="Archivo Convertido (.xlsx)",
        blank=True,
        null=True
    )

    original_filename = models.CharField(
        max_length=255,
        verbose_name="Nombre del archivo original"
    )

    converted_filename = models.CharField(
        max_length=255,
        verbose_name="Nombre del archivo convertido",
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de conversión"
    )

    file_size = models.PositiveIntegerField(
        verbose_name="Tamaño del archivo (bytes)",
        default=0
    )

    conversion_successful = models.BooleanField(
        default=False,
        verbose_name="Conversión exitosa"
    )

    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Mensaje de error"
    )

    class Meta:
        verbose_name = "Registro de Conversión"
        verbose_name_plural = "Registros de Conversiones"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.original_filename} → {self.converted_filename or 'No convertido'}"

    def get_download_url(self):
        """Retorna la URL de descarga del archivo convertido"""
        if self.converted_file and self.conversion_successful:
            return reverse('xlstoxlsx:download', kwargs={'filename': self.converted_filename})
        return None
