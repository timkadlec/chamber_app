#  Copyright (c) 2024. Lorem ipsum dolor sit amet, consectetur adipiscing elit.
#  Morbi non lorem porttitor neque feugiat blandit. Ut vitae ipsum eget quam lacinia accumsan.
#  Etiam sed turpis ac ipsum condimentum fringilla. Maecenas magna.
#  Proin dapibus sapien vel ante. Aliquam erat volutpat. Pellentesque sagittis ligula eget metus.
#  Vestibulum commodo. Ut rhoncus gravida arcu.

from flask import render_template, make_response, request, redirect, url_for, jsonify, abort, flash
from weasyprint import HTML
from . import export_bp
from chamber_app.models.library import (
    Composer,
    Composition,
    Instrument,
    Player,
    composition_player
)
from chamber_app.models.structure import Teacher
from chamber_app.forms import ComposerForm, CompositionForm
from chamber_app.extensions import db
import os
from datetime import datetime
import pandas as pd
from werkzeug.utils import secure_filename
from urllib.parse import urlencode


@export_bp.route('/download-pdf')
def download_pdf():

    teachers = Teacher.query.order_by(Teacher.name).all()
    # Render HTML template to a string
    html_content = render_template('teacher_chamber_ensembles.html', content="Hello, PDF!", teachers=teachers)

    # Generate PDF
    pdf = HTML(string=html_content).write_pdf()

    # Create a response to download the PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename="export.pdf"'

    return response