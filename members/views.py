from django.shortcuts import render
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from django.utils import timezone
from datetime import date
from .models import Member, PrayerRequest, Talent
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render, get_object_or_404


def dashboard(request):
    """Homepage dashboard showing key church statistics."""

    today = date.today()
    current_month = today.month

    # Member statistics
    total_members = Member.objects.count()
    baptized_members = Member.objects.filter(is_baptized=True).count()

    # Birthdays this month
    birthdays_this_month = Member.objects.filter(
        date_of_birth__month=current_month
    ).order_by('date_of_birth__day')

    # Prayer requests
    total_prayers = PrayerRequest.objects.count()
    pending_prayers = PrayerRequest.objects.filter(status='pending').count()
    answered_prayers = PrayerRequest.objects.filter(status='answered').count()
    recent_prayers = PrayerRequest.objects.filter(
        status__in=['pending', 'ongoing']
    ).order_by('-date_submitted')[:5]

    # Talents
    total_talents = Talent.objects.count()
    available_talents = Talent.objects.filter(is_available_for_ministry=True).count()

    context = {
        'today': today,
        'total_members': total_members,
        'baptized_members': baptized_members,
        'birthdays_this_month': birthdays_this_month,
        'total_prayers': total_prayers,
        'pending_prayers': pending_prayers,
        'answered_prayers': answered_prayers,
        'recent_prayers': recent_prayers,
        'total_talents': total_talents,
        'available_talents': available_talents,
    }
    return render(request, 'dashboard.html', context)
def members_pdf(request):
    """Generate a PDF directory of all church members."""

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="zbc_members.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        textColor=colors.HexColor('#1565C0'),
        fontSize=20,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#6C757D'),
        fontSize=10,
        spaceAfter=20,
    )

    # Header
    elements.append(Paragraph("Zion Baptist Church", title_style))
    elements.append(Paragraph(
        f"Member Directory — Generated {timezone.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))

    # Table data
    members = Member.objects.all().order_by('last_name', 'first_name')
    data = [['#', 'Full Name', 'Gender', 'Phone', 'Occupation', 'Baptized']]

    for i, m in enumerate(members, start=1):
        data.append([
            str(i),
            f"{m.first_name} {m.last_name}",
            m.get_gender_display() or '—',
            m.phone or '—',
            m.occupation or '—',
            'Yes' if m.is_baptized else 'No',
        ])

    # Table styling
    table = Table(data, colWidths=[1*cm, 4.5*cm, 1.5*cm, 3*cm, 4*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F7FA')]),
    ]))
    elements.append(table)

    # Footer
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Total Members: {members.count()}",
        styles['Normal']
    ))

    doc.build(elements)
    return response


def prayer_requests_pdf(request):
    """Generate a PDF of active prayer requests."""

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="zbc_prayers.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        textColor=colors.HexColor('#1B5E20'),
        fontSize=20,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#6C757D'),
        fontSize=10,
        spaceAfter=20,
    )

    elements.append(Paragraph("Zion Baptist Church", title_style))
    elements.append(Paragraph(
        f"Active Prayer Requests — Generated {timezone.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))

    prayers = PrayerRequest.objects.filter(
        status__in=['pending', 'ongoing']
    ).order_by('-date_submitted')

    data = [['Date', 'Member', 'Request', 'Status']]

    for p in prayers:
        data.append([
            p.date_submitted.strftime('%b %d'),
            str(p.member),
            Paragraph(p.request[:200], styles['Normal']),
            p.get_status_display(),
        ])

    table = Table(data, colWidths=[2*cm, 4*cm, 8*cm, 2.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B5E20')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F7FA')]),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Total Active Prayer Requests: {prayers.count()}",
        styles['Normal']
    ))

    doc.build(elements)
    return response


def birthdays_pdf(request):
    """Generate a PDF of birthdays for the current month."""

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="zbc_birthdays.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            leftMargin=2*cm, rightMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        textColor=colors.HexColor('#1565C0'),
        fontSize=20,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        textColor=colors.HexColor('#6C757D'),
        fontSize=10,
        spaceAfter=20,
    )

    today = timezone.now().date()
    month_name = today.strftime('%B')

    elements.append(Paragraph("Zion Baptist Church", title_style))
    elements.append(Paragraph(
        f"Birthdays in {month_name} {today.year}",
        subtitle_style
    ))

    birthdays = Member.objects.filter(
        date_of_birth__month=today.month
    ).order_by('date_of_birth__day')

    data = [['Day', 'Full Name', 'Phone']]

    for m in birthdays:
        data.append([
            m.date_of_birth.strftime('%B %d'),
            f"{m.first_name} {m.last_name}",
            m.phone or '—',
        ])

    table = Table(data, colWidths=[3*cm, 8*cm, 5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DDDDDD')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F7FA')]),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        f"Total Birthdays: {birthdays.count()}",
        styles['Normal']
    ))

    doc.build(elements)
    return response
def member_list(request):
    """Public directory of all active church members."""

    # Base queryset — only active members
    members = Member.objects.filter(is_active=True).order_by('last_name', 'first_name')

    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        members = members.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(member_id__icontains=search_query)
        )

    # Filters
    organ_filter = request.GET.get('organ', '').strip()
    if organ_filter:
        members = members.filter(organ=organ_filter)

    gender_filter = request.GET.get('gender', '').strip()
    if gender_filter:
        members = members.filter(gender=gender_filter)

    baptized_filter = request.GET.get('baptized', '').strip()
    if baptized_filter == 'yes':
        members = members.filter(is_baptized=True)
    elif baptized_filter == 'no':
        members = members.filter(is_baptized=False)

    # Pagination — 12 members per page
    paginator = Paginator(members, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_members': members.count(),
        'search_query': search_query,
        'organ_filter': organ_filter,
        'gender_filter': gender_filter,
        'baptized_filter': baptized_filter,
        'organ_choices': Member.ORGAN_CHOICES,
        'gender_choices': Member.GENDER_CHOICES,
    }
    return render(request, 'member_list.html', context)

def member_card_pdf(request, member_id):
    """Generate a single-page PDF profile card for one member."""

    member = get_object_or_404(Member, pk=member_id)
    family = getattr(member, 'family', None)
    children = family.children.all() if family else []
    talents = member.talents.all()

    response = HttpResponse(content_type='application/pdf')
    filename = f"ZBC_{member.member_id}_{member.last_name}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'

    doc = SimpleDocTemplate(
        response, pagesize=A4,
        leftMargin=1.5*cm, rightMargin=1.5*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    header_style = ParagraphStyle(
        'Header', parent=styles['Heading1'],
        textColor=colors.HexColor('#1565C0'),
        fontSize=22, spaceAfter=4, alignment=1
    )
    sub_header_style = ParagraphStyle(
        'SubHeader', parent=styles['Normal'],
        textColor=colors.HexColor('#6C757D'),
        fontSize=11, spaceAfter=20, alignment=1
    )
    section_style = ParagraphStyle(
        'Section', parent=styles['Heading2'],
        textColor=colors.HexColor('#1B5E20'),
        fontSize=14, spaceBefore=14, spaceAfter=8
    )
    field_label_style = ParagraphStyle(
        'FieldLabel', parent=styles['Normal'],
        textColor=colors.HexColor('#6C757D'),
        fontSize=10, fontName='Helvetica-Bold'
    )
    field_value_style = ParagraphStyle(
        'FieldValue', parent=styles['Normal'],
        textColor=colors.HexColor('#1A1A1A'),
        fontSize=11, spaceAfter=6
    )

    # Header
    elements.append(Paragraph("Zion Baptist Church", header_style))
    elements.append(Paragraph(
        "Bonaberi — Douala, Cameroon",
        sub_header_style
    ))

    # Title
    elements.append(Paragraph("Member Profile", section_style))
    elements.append(Spacer(1, 6))

    # --- PHOTO + BASIC INFO ROW ---
    photo_cell = ""
    if member.photo:
        try:
            from reportlab.platypus import Image as RLImage
            img = RLImage(member.photo.path, width=4*cm, height=4*cm)
            photo_cell = img
        except Exception:
            photo_cell = Paragraph("Photo available", styles['Normal'])
    else:
        photo_cell = Paragraph(
            f"<b>{member.first_name[0].upper()}</b>",
            ParagraphStyle('Init', parent=styles['Normal'],
                          fontSize=48, alignment=1,
                          textColor=colors.HexColor('#1565C0'))
        )

    basic_info = [
        [Paragraph("Full Name", field_label_style),
         Paragraph(f"{member.first_name} {member.last_name}", field_value_style)],
        [Paragraph("Member ID", field_label_style),
         Paragraph(f"<b>{member.member_id}</b>", field_value_style)],
        [Paragraph("Gender", field_label_style),
         Paragraph(member.get_gender_display() or '—', field_value_style)],
        [Paragraph("Age", field_label_style),
         Paragraph(f"{member.age() or '—'} years", field_value_style)],
        [Paragraph("Organ / Fellowship", field_label_style),
         Paragraph(member.get_organ_display() or '—', field_value_style)],
        [Paragraph("Baptized", field_label_style),
         Paragraph('Yes' if member.is_baptized else 'No', field_value_style)],
    ]

    info_table = Table(basic_info, colWidths=[4*cm, 6*cm])
    info_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
    ]))

    header_row = Table([[photo_cell, info_table]], colWidths=[5*cm, 11*cm])
    header_row.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), 12),
    ]))
    elements.append(header_row)

    # --- PERSONAL INFO ---
    elements.append(Paragraph("Personal Information", section_style))

    personal_data = [
        ['Date of Birth', member.date_of_birth.strftime('%B %d, %Y') if member.date_of_birth else '—'],
        ['Marital Status', member.get_marital_status_display() or '—'],
        ['Occupation', member.occupation or '—'],
        ['Phone', member.phone or '—'],
        ['Email', member.email or '—'],
        ['Address', member.address or '—'],
        ['Joined Date', member.joined_date.strftime('%B %d, %Y') if member.joined_date else '—'],
    ]

    personal_table = Table(personal_data, colWidths=[5*cm, 11*cm])
    personal_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6C757D')),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F5F7FA')]),
        ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E0E0E0')),
    ]))
    elements.append(personal_table)

    # --- FAMILY ---
    if family and (family.spouse_name or children):
        elements.append(Paragraph("Family", section_style))

        family_data = []
        if family.spouse_name:
            family_data.append(['Spouse', family.spouse_name])
        if family.wedding_anniversary:
            family_data.append(['Wedding Anniversary', family.wedding_anniversary.strftime('%B %d, %Y')])

        if family_data:
            ft = Table(family_data, colWidths=[5*cm, 11*cm])
            ft.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#6C757D')),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#F5F7FA')]),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E0E0E0')),
            ]))
            elements.append(ft)

        if children:
            elements.append(Spacer(1, 8))
            elements.append(Paragraph(
                f"Children ({children.count()})",
                field_label_style
            ))
            child_data = [['Name', 'Gender', 'Age']]
            for child in children:
                child_data.append([
                    child.name,
                    child.get_gender_display() or '—',
                    f"{child.age()} years" if child.age() else '—'
                ])
            ct = Table(child_data, colWidths=[8*cm, 4*cm, 4*cm])
            ct.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1565C0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E0E0E0')),
            ]))
            elements.append(ct)

    # --- TALENTS ---
    if talents:
        elements.append(Paragraph("Talents & Ministries", section_style))
        talent_data = [['Talent', 'Category', 'Level', 'Available']]
        for t in talents:
            talent_data.append([
                t.name,
                t.get_category_display(),
                t.get_skill_level_display(),
                'Yes' if t.is_available_for_ministry else 'No',
            ])
        tt = Table(talent_data, colWidths=[6*cm, 5*cm, 3*cm, 2*cm])
        tt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1B5E20')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.25, colors.HexColor('#E0E0E0')),
        ]))
        elements.append(tt)

    # --- FOOTER ---
    elements.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        textColor=colors.HexColor('#999999'),
        fontSize=9, alignment=1
    )
    elements.append(Paragraph(
        f"Generated on {timezone.now().strftime('%B %d, %Y')} — Zion Baptist Church Membership System",
        footer_style
    ))

    doc.build(elements)
    return response
def member_detail(request, member_id):
    """Detailed profile page for a single member."""

    member = get_object_or_404(Member, pk=member_id)

    # Get related data
    family = getattr(member, 'family', None)
    children = family.children.all() if family else []
    talents = member.talents.all()
    prayers = member.prayer_requests.all().order_by('-date_submitted')[:5]

    context = {
        'member': member,
        'family': family,
        'children': children,
        'talents': talents,
        'prayers': prayers,
    }
    return render(request, 'member_detail.html', context)