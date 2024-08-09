from django.contrib import admin
from django.urls import path
from django.utils.html import format_html

# Register your models here.
from .models import Label
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Label, Barcode
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.barcode import code128  # Import the barcode generator
from reportlab.lib.units import mm

admin.site.site_header = "Accropoly Admin"
admin.site.site_title = "Powered By Zapuza"
admin.site.index_title = "Welcome to Accropoly Ninomiya Industries"
@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('productName', 'productCode', 'unit', 'qty', 'print_label_button')
    actions = ['print_selected_labels']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'print-label/<int:label_id>/',
                self.admin_site.admin_view(self.print_label),
                name='print-label',
            ),
        ]
        return custom_urls + urls

    def print_label_button(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Print Label</a>',
            reverse('admin:print-label', args=[obj.pk])
        )

    def print_label(self, request, label_id, *args, **kwargs):
        label = Label.objects.get(pk=label_id)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="label.pdf"'

        buffer = io.BytesIO()
        label_width = 63 * 2.83
        label_height = 10 * 2.83

        p = canvas.Canvas(buffer, pagesize=(label_width, label_height))

        # Draw the label with the required spacing
        self.draw_label(p, label, 0, 0, label_width, label_height)

        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    def print_selected_labels(self, request, queryset):
        # Response for the PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="selected_labels.pdf"'

        buffer = io.BytesIO()

        label_width = 63 * 2.83
        label_height = 10 * 2.83
        spacing_between_labels = 1 * 2.83
        page_width = label_width
        total_height = label_height + spacing_between_labels
        page_height = (label_height + spacing_between_labels) * queryset.count()

        p = canvas.Canvas(buffer, pagesize=(page_width, page_height))

        for index, label in enumerate(queryset):
            y_position = page_height - (index * total_height) - label_height
            self.draw_label(p, label, 0, y_position, label_width, label_height)

        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def draw_label(self, p, label, x, y, width, height):
        p.setLineWidth(0.5)
        p.rect(x, y, width, height)

        p.setFont("Helvetica-Bold", 6)
        p.drawCentredString(width / 2, y + height - 7, "Accropoly Ninomiya Industries")

        p.setFont("Helvetica", 4)

        y_offset = y + height - 14

        p.drawString(x + 5, y_offset, f"Name: {label.productName}")
        y_offset -= 4
        p.drawString(x + 5, y_offset, f"Code: {label.productCode}")
        y_offset -= 4
        p.drawString(x + 5, y_offset, f"Unit: {label.unit}")
        y_offset -= 4
        p.drawString(x + 5, y_offset, f"Quantity: {label.qty}")

@admin.register(Barcode)
class BarcodeAdmin(admin.ModelAdmin):
    list_display = ('value', 'print_barcode_button')
    actions = ['print_selected_barcodes']

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'print-barcode/<int:barcode_id>/',
                self.admin_site.admin_view(self.print_barcode),
                name='print-barcode',
            ),
        ]
        return custom_urls + urls

    def print_barcode_button(self, obj):
        return format_html(
            '<a class="button" href="{}" target="_blank">Print Barcode</a>',
            reverse('admin:print-barcode', args=[obj.pk])
        )
    print_barcode_button.short_description = 'Print Barcode'
    print_barcode_button.allow_tags = True

    def print_barcode(self, request, barcode_id, *args, **kwargs):
        barcode = Barcode.objects.get(pk=barcode_id)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="barcode.pdf"'

        buffer = io.BytesIO()
        barcode_width = 63 * mm
        barcode_height = 10 * mm

        p = canvas.Canvas(buffer, pagesize=(barcode_width, barcode_height * 2))  # Double the height for 2 copies

        for copy in range(2):
            y_position = (2 - copy) * barcode_height - barcode_height
            self.draw_barcode(p, barcode, 0, y_position, barcode_width, barcode_height)

        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    def print_selected_barcodes(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="selected_barcodes.pdf"'

        buffer = io.BytesIO()

        barcode_width = 63 * mm
        barcode_height = 10 * mm
        spacing_between_barcodes = 2 * mm
        page_width = barcode_width
        total_height = (barcode_height + spacing_between_barcodes) * queryset.count() * 2
        page_height = total_height

        p = canvas.Canvas(buffer, pagesize=(page_width, page_height))

        for index, barcode in enumerate(queryset):
            for copy in range(2):
                y_position = page_height - (index * 2 + copy) * (barcode_height + spacing_between_barcodes) - barcode_height
                self.draw_barcode(p, barcode, 0, y_position, barcode_width, barcode_height)

        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    def draw_barcode(self, p, barcode, x, y, width, height):
        p.setLineWidth(0.5)
        p.rect(x, y, width, height)

        barcode_width = width - 10 * mm
        barcode_height = 6 * mm

        barcode_value = code128.Code128(
            barcode.value,
            barWidth=0.4 * mm,
            barHeight=barcode_height
        )

        barcode_x = x + (width - barcode_value.width) / 2
        barcode_y = y + (height - barcode_height + 2) / 2

        barcode_value.drawOn(p, barcode_x, barcode_y)

        p.setFont("Helvetica", 6)

        text_y = barcode_y - 2 * mm
        p.drawCentredString(x + width / 2, text_y, barcode.value)
