from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm # A biblioteca WTForms serve para usar formulários na Flask.
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import DataRequired
import os
from pdf_modifier import modify_pdf  

app = Flask(__name__)
app.config['SECRET_KEY'] = '89877889'
app.config['UPLOAD_FOLDER'] = './uploads/'

class CPFInputForm(FlaskForm): # O formulário pedirá ao usuário um CPF, uma posição, um código de cor e um arquivo a ser enviado.
    cpf = StringField('CPF', validators=[DataRequired()])
    position = SelectField('Position',
                           choices=[
                               ('top-left', 'Top Left'),
                               ('top-right', 'Top Right'),
                               ('bottom-left', 'Bottom Left'),
                               ('bottom-right', 'Bottom Right')
                           ])
    submit = SubmitField('Submit')
    color = StringField('Color', validators=[DataRequired()])


@app.route("/", methods=["GET", "POST"]) # Quando uma solicitação POST é recebida
def upload_file():
    form = CPFInputForm()
    if form.validate_on_submit():
        if 'file' not in request.files:
            flash('Arquivo não incluido')
            return redirect(request.url)
        file = request.files['file']
        
        if file.filename == '':
            flash("Arquivo não selecionado")
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # Salva o arquivo no diretório de upload, extrai as informações do formulário e tenta modificar o PDF

            cpf = form.cpf.data
            position = form.position.data
            color = form.color.data

            try:
                modify_pdf(filename, cpf, position, color,
                           app.config["UPLOAD_FOLDER"])
                return send_file(os.path.join(app.config['UPLOAD_FOLDER'],
                                              filename), as_attachment=True)
            except Exception as e:
                flash("Erro no envio do arquivo" + str(e))
                return redirect(request.url)

    return render_template('index.html', form=form)