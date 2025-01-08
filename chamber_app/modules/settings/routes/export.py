#  Copyright (c) 2024. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from flask import render_template, make_response, url_for
from weasyprint import HTML
from .. import settings_bp
from datetime import datetime

from chamber_app.models.structure import Teacher
from chamber_app.models.ensemble import Ensemble


@settings_bp.route('/console')
def export_console():
    return render_template('export_console.html')

@settings_bp.route('/teacher-ensembles-pdf', methods=['POST'])
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


@settings_bp.route('/ensembles-pdf', methods=['POST'])
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
