import io

from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
# Register your models here.
from django.urls import reverse
from django.utils.html import format_html
from reportlab.graphics.barcode import code128  # Import the barcode generator
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from .models import Label, Barcode

admin.site.site_header = "Accropoly Admin"
admin.site.site_title = "Powered By Zapuza"
admin.site.index_title = "Welcome to Accropoly Ninomiya Industries"


@admin.register(Label)
class LabelAdmin(admin.ModelAdmin):
    list_display = ('productName', 'productCode', 'unit', 'qty', 'print_label_button')
    actions = ['print_selected_labels']
    search_fields = ['productCode']

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
        # Create a response for PDF download
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="selected_labels.pdf"'

        buffer = io.BytesIO()

        # Label dimensions in mm
        label_width = 63 * mm  # approximately 63 mm
        label_height = 10 * mm  # approximately 10 mm

        # Create a PDF canvas with custom dimensions for each label page
        p = canvas.Canvas(buffer, pagesize=(label_width, label_height))

        # Loop through each label in queryset and print it on a separate page
        for label in queryset:
            # Draw label content on a new page
            self.draw_label(p, label, 0, 0, label_width, label_height)
            # Move to a new page after each label
            p.showPage()

        # Save the PDF content to the buffer
        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response

    def draw_label(self, p, label, x, y, width, height):
        # Draw label content with proper formatting
        p.setFont("Helvetica-Bold", 8)
        p.drawCentredString(x + width / 2, y + height - 7, "ANIPL")  # Centered ANIPL at top

        p.setFont("Helvetica", 6)  # Smaller font for product details
        y_offset = y + height - 14  # Start below the header

        # Print each piece of label information
        p.drawString(x + 5, y_offset, f"Desc: {label.productName}")
        y_offset -= 6  # Move down for next line
        p.drawString(x + 5, y_offset, f"Part No.: {label.productCode}")
        y_offset -= 6
        p.drawString(x + 5, y_offset, f"Dispatch Date: {label.unit}")
        p.drawString(x + 100, y_offset, f"| Quantity: {label.qty}")


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
        # Retrieve the single Barcode object
        barcode = Barcode.objects.get(pk=barcode_id)

        # Create a queryset that only includes this barcode
        queryset = Barcode.objects.filter(pk=barcode_id)

        # Call print_selected_barcodes with the single-item queryset
        return self.print_selected_barcodes(request, queryset)

    def print_selected_barcodes(self, request, queryset):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="selected_barcodes.pdf"'

        buffer = io.BytesIO()

        # Set the custom page size to fit two copies of the barcode vertically
        barcode_width = 63 * mm
        barcode_height = 10 * mm
        page_height = barcode_height * 2  # Double the height to fit two copies on each page

        p = canvas.Canvas(buffer, pagesize=(barcode_width, page_height))
        duplicated_barcodes = [barcode for barcode in queryset for _ in range(2)]
        for barcode in duplicated_barcodes:
            # Print two consecutive pages for each barcode
            for copy in range(1):
                y_position = (2 - copy) * barcode_height - barcode_height
                self.draw_barcode(p, barcode, 0, y_position, barcode_width, barcode_height)

            p.showPage()

        p.save()
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)

        return response

    def draw_barcode(self, p, barcode, x, y, width, height):
        barcode_width = width - 10 * mm
        barcode_height = height + 10  # Adjust to make the barcode height dynamic

        barcode_value = code128.Code128(
            barcode.value,
            barWidth=0.4 * mm,
            barHeight=barcode_height
        )

        barcode_x = x + (width - barcode_value.width) / 2
        barcode_y = y + (height - barcode_height) / 3 - 15  # Centering the barcode vertically

        barcode_value.drawOn(p, barcode_x, barcode_y)

        p.setFont("Helvetica", 6)

        text_y = barcode_y - 2 * mm
        p.drawCentredString(x + width / 2, text_y, barcode.value)

# ANIPL, Part Number, Desc, Qty, Dispatch Date
