import os
from django.conf import settings
from django.utils import timezone
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

EXCEL_FILE_PATH = os.path.join(settings.MEDIA_ROOT, 'contacts', 'murojaatlar.xlsx')

HEADERS = [
    "ID",
    "F.I.Sh",
    "Telefon",
    "Email",
    "Murojaat turi",
    "Mavzu",
    "Xabar matni",
    "Holati",
    "Admin javobi",
    "IP manzil",
    "Yuborilgan sana va vaqt"
]


def sync_contact_to_excel(contact):
    """
    Appends or updates a contact entry into the master Excel file.
    Always maintains a synchronized murojaatlar.xlsx file on disk.
    """
    try:
        export_all_contacts_to_excel()
    except Exception as e:
        print(f"Error syncing contact to excel: {e}")


def export_all_contacts_to_excel(queryset=None):
    """
    Generates and saves a clean, styled Excel workbook containing all contacts.
    Returns the absolute path to the generated Excel file.
    """
    from apps.contacts.models import Contact

    if queryset is None:
        queryset = Contact.objects.all().order_by('-created_at')

    os.makedirs(os.path.dirname(EXCEL_FILE_PATH), exist_ok=True)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Murojaatlar"

    # Header styling
    header_fill = PatternFill(start_color="1E1B4B", end_color="1E1B4B", fill_type="solid")
    header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    ws.append(HEADERS)
    ws.row_dimensions[1].height = 26

    for col_num in range(1, len(HEADERS) + 1):
        cell = ws.cell(row=1, column=col_num)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment
        cell.border = thin_border

    status_colors = {
        'new': 'FEE2E2',      # light red
        'read': 'FEF3C7',     # light yellow
        'replied': 'D1FAE5',  # light green
        'closed': 'F3F4F6',   # light gray
    }

    for contact in queryset:
        created_str = contact.created_at.strftime('%Y-%m-%d %H:%M') if contact.created_at else ''
        ws.append([
            contact.id,
            contact.full_name,
            contact.phone or '-',
            contact.email or '-',
            contact.get_contact_type_display(),
            contact.subject,
            contact.message,
            contact.get_status_display(),
            contact.admin_reply or '-',
            contact.ip_address or '-',
            created_str
        ])

    # Styling content rows
    for r_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, min_col=1, max_col=len(HEADERS)), start=2):
        ws.row_dimensions[r_idx].height = 22
        for cell in row:
            cell.font = Font(name="Calibri", size=10)
            cell.border = thin_border
            if cell.column in [1, 3, 5, 8, 10, 11]:
                cell.alignment = Alignment(horizontal="center", vertical="center")
            else:
                cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)

    # Auto-adjust column widths
    for col in ws.columns:
        max_len = 0
        col_letter = get_column_letter(col[0].column)
        for cell in col:
            val = str(cell.value or '')
            if len(val) > max_len:
                max_len = len(val)
        ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 50)

    ws.freeze_panes = "A2"
    wb.save(EXCEL_FILE_PATH)
    return EXCEL_FILE_PATH
