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
        # Fetch the specific label by its ID
        label = Label.objects.get(pk=label_id)

        # Create a queryset with just this label to pass to the print_selected_labels function
        queryset = Label.objects.filter(pk=label_id)

        # Call the print_selected_labels method, passing the queryset containing only this label
        return self.print_selected_labels(request, queryset)

    def print_selected_labels(self, request, queryset):
        # Create a response for PDF download
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'inline; filename="selected_labels.pdf"'

        buffer = io.BytesIO()

        # Label dimensions in mm (2 inches x 1 inch)
        label_width = 50.8 * mm  # 2 inches
        label_height = 25.4 * mm  # 1 inch

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
        # Set title font and center at the top
        p.setFont("Helvetica-Bold", 10)
        title = "ANIPL"
        p.drawCentredString(x + width / 2, y + height - 10, title)  # Title centered at the top

        # Set smaller font for other details and center each line
        p.setFont("Helvetica", 8)

        # Calculate the total height for the content (leave some space between lines)
        total_text_height = 5 * 10  # 5 lines of text, each with 10 units of height as an estimate
        vertical_spacing = (height - total_text_height) / 25  # Distribute the remaining space

        y_offset = y + height - 25  # Start below the title

        # Left-align each piece of label information
        p.drawString(x + 5, y_offset, f"Desc: {label.productName}")
        y_offset -= (10 + vertical_spacing)  # Move down for the next line

        p.drawString(x + 5, y_offset, f"Part No.: {label.productCode}")
        y_offset -= (10 + vertical_spacing)

        p.drawString(x + 5, y_offset, f"Dispatch Date: {label.unit}")
        y_offset -= (10 + vertical_spacing)

        p.drawString(x + 5, y_offset, f"Quantity: {label.qty}")
        y_offset -= (10 + vertical_spacing)

        # Add random string after Part No. (you can replace with dynamic data)
        random_string = f"PO: {label.poNumber}"
        p.drawString(x + 5, y_offset, random_string)


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
