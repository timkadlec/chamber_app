from flask import render_template, make_response, url_for
from weasyprint import HTML
from .. import settings_bp
from datetime import datetime
from chamber_app.decorators import module_required
from chamber_app.models.structure import Teacher
from chamber_app.models.ensemble import Ensemble


@settings_bp.route('/console')
@module_required('Export')
def export_console():
    return render_template('export_console.html')


@settings_bp.route('/teacher-ensembles-pdf', methods=['POST'])
@module_required('Export')
def export_teacher_ensembles():
    teachers = Teacher.query.order_by(Teacher.name).all()
    # Render HTML template to a string
    html_content = render_template('export_teacher_ensembles.html', content="Hello, PDF!", teachers=teachers)

    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()

    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"HAMU_teacher_ensembles_{today_date}.pdf"

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@settings_bp.route('/active-teachers-pdf', methods=['POST'])
@module_required('Export')
def export_active_teachers():
    teachers = Teacher.query.order_by(Teacher.name).all()
    # Render HTML template to a string
    html_content = render_template('export_active_teachers.html', content="Hello, PDF!", teachers=teachers)

    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()

    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"HAMU_active_teachers_{today_date}.pdf"

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response


@settings_bp.route('/ensembles-pdf', methods=['POST'])
@module_required('Export')
def export_ensembles():
    ensembles = Ensemble.query.filter_by(ended=None).order_by(Ensemble.name).all()
    logo = url_for('static', filename='HAMU.jpg')

    print(logo)
    # Render HTML template to a string
    html_content = render_template('export_ensembles.html', logo=logo, ensembles=ensembles)

    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()

    today_date = datetime.now().strftime("%Y-%m-%d")
    filename = f"HAMU_ensembles_{today_date}.pdf"

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'

    return response
