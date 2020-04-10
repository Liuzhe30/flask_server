from flask import Blueprint
from flask_mail import Mail
from flask_mail import Message
from flask import Flask
from flask import render_template
from flask_bootstrap import Bootstrap
from flask import request
from flask_wtf import FlaskForm
from flask_uploads import UploadSet, configure_uploads
from wtforms import StringField, SubmitField, BooleanField, SelectField, TextAreaField, FileField
from wtforms.validators import Required, Email
from wtforms.fields import core
from flask_wtf.file import FileField, FileAllowed, FileRequired
from time import sleep
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(2)
from flask import send_file, send_from_directory
# from pyecharts.constants import DEFAULT_HOST
import element
import uuid
import os
from Predictor import Predict, Outputs
import pathlib
from werkzeug.utils import secure_filename
from getTrainnedModel import get_trained_model, predict
from readUserTxt import load_data
from UBPspred import Feature, Test, Output
import numpy as np

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['MAIL_SERVER'] = 'smtp.126.com'  # this is email server
app.config['MAIL_PORT'] = 25  # this is the port of email server
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USE_TLS'] = False
app.config['UPLOADED_FASTAS_DEST'] = os.getcwd()
app.config['MAIL_USERNAME'] = 'nenubiodata@126.com'
# app.config['MAIL_PASSWORD'] = 'abcdefg'
app.config['MAIL_PASSWORD'] = 'tanxian123'  # this is email password
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['SECRET_KEY'] = 'nenu204'
mail = Mail(app)
mail.init_app(app)

FASTAS = tuple('fasta fa'.split())
fastas = UploadSet('fastas', FASTAS)
configure_uploads(app, fastas)


class FastaForm(FlaskForm):
    m_fasta = TextAreaField('Input protein sequence', validators=[],
                            render_kw={'class': 'text-body', 'rows': 13, 'columns': 30,
                                       'placeholder': u"Input Sequence\ne.g. >4n6h_A\nDLEDNWETLNDNLKVIEKADNAAQVKDALTKMRAAALDAQKATPPKLEDKSPDSPEMKDFRHGFDILVGQIDDALKLANEGKVKEAQAAAEQLKTTRNAYIQKYLGSPGARSASSLALAIAITALYSAVCAVGLLGNVLVMFGIVRYTKMKTATNIYIFNLALADALATSTLPFQSAKYLMETWPFGELLaKAVLSIDYYNMFTSIFTLTMMSVDRYIAVCHPVKALDFRTPAKAKLINICIWVLASGVGVPIMVMAVTRPRDGAVVaMLQFPSPSWYWDTVTKICVFLFAFVVPILIITVCYGLMLLRLRSVRLLSGSKEKDRSLRRITRMVLVVVGAFVVCWAPIHIFVIVWTLVDIDRRDPLVVAALHLCIALGYANSSLNPVLYAFLDENFKRCFRQLCRKPCG\n"})

    file = FileField('Upload file',
                     # validators=[FileRequired(), FileAllowed(['fasta', 'fa'], 'fasta only!')]
                     validators=[FileAllowed(fastas, 'fasta only!')]
                     )
    email = StringField('Email', [Required(),
                                  Email(message=u'That\'s not a valid email address.')])
    submit = SubmitField('Submit')


# ---------------------The_First_Class_Page----------------------
@app.route('/')
def Index():
    return render_template('Index.html')


@app.route('/tmp_ssurface', methods=['GET', 'POST'])
def Index_tmp_ssurface():
    # name = None

    forms = FastaForm()
    if forms.validate_on_submit():
        email = []
        email.append(forms.email.data)
        print(forms.file.data)
        uuid_s = uuid.uuid1()
        print(uuid_s)
        uuid_fasta = '/home/public/%s.fasta' % uuid_s
        # pathlib.Path(uuid_fasta).touch()
        uuid_text = '/home/public/%s.txt' % uuid_s
        uuid_text2 = '/home/public/%s.txt2' % uuid_s
        pathlib.Path(uuid_text).touch()

        if forms.m_fasta.data:
            m_seq = forms.m_fasta.data
            # f = open(uuid_fasta, 'w')
            # f.close()
            with open(uuid_fasta, "w") as ws:
                ws.write(m_seq)

            pre = Predict()
            y_pred = pre.get_result_tmp_ssurface(uuid_fasta)
            out = Outputs()
            out.output_result_tmp_ssurface(uuid_fasta, y_pred, uuid_text)
            out.print_result_tmp_ssurface(uuid_fasta, y_pred, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from ICDtools",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass

            try:
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()
            except OSError:
                pass

            return render_template('Result2_tmp_ssurface.html', message=result2)

        elif forms.file.data:
            # filename = forms.file.data.filename
            filename = fastas.save(forms.file.data, name='home/public/demo.')
            with open(filename) as fn:
                m_seq = fn.read()
                with open(uuid_fasta, "w+") as f:
                    f.write(m_seq)

            pre = Predict()
            y_pred = pre.get_result_tmp_ssurface(uuid_fasta)
            out = Outputs()
            out.output_result_tmp_ssurface(uuid_fasta, y_pred, uuid_text)
            out.print_result_tmp_ssurface(uuid_fasta, y_pred, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from ICDtools",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass
            try:
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()
            except OSError:
                pass
            return render_template('Result2_tmp_ssurface.html', message=result2)
    return render_template('Index_tmp_ssurface.html', forms=forms)
    # return render_template('Index.html', # form=form, forms=forms)

@app.route('/TMP-SSurface-2.0', methods=['GET', 'POST'])
def Index_tmp_ssurface2():
    # name = None

    forms = FastaForm()
    if forms.validate_on_submit():
        email = []
        email.append(forms.email.data)
        print(forms.file.data)
        uuid_s = uuid.uuid1()
        print(uuid_s)
        uuid_fasta = '/home/public/%s.fasta' % uuid_s
        # pathlib.Path(uuid_fasta).touch()
        uuid_text = '/home/public/%s.txt' % uuid_s
        uuid_text2 = '/home/public/%s.txt2' % uuid_s
        pathlib.Path(uuid_text).touch()

        if forms.m_fasta.data:
            m_seq = forms.m_fasta.data
            # f = open(uuid_fasta, 'w')
            # f.close()
            with open(uuid_fasta, "w") as ws:
                ws.write(m_seq)

            pre = Predict()
            zpred = pre.get_result_TMZC(uuid_fasta)
            y_pred = pre.get_result_tmp_ssurface2(uuid_fasta,zpred)
            #print(y_pred)
            out2 = Outputs()
            out2.output_result_tmp_ssurface_2(uuid_fasta, y_pred, uuid_text)
            out2.print_result_tmp_ssurface_2(uuid_fasta, y_pred, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from ICDtools",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass

            try:
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()
            except OSError:
                pass

            return render_template('Result2_tmp_ssurface2.html', message=result2)

        elif forms.file.data:
            # filename = forms.file.data.filename
            filename = fastas.save(forms.file.data, name='home/public/demo.')
            with open(filename) as fn:
                m_seq = fn.read()
                with open(uuid_fasta, "w+") as f:
                    f.write(m_seq)

            pre = Predict()
            zpred = pre.get_result_TMZC(uuid_fasta)
            y_pred = pre.get_result_tmp_ssurface2(uuid_fasta,zpred)
            out = Outputs()
            out.output_result_tmp_ssurface2(uuid_fasta, y_pred, uuid_text)
            out.print_result_tmp_ssurface2(uuid_fasta, y_pred, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from ICDtools",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass
            try:
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()
            except OSError:
                pass
            return render_template('Result2_tmp_ssurface2.html', message=result2)
    return render_template('Index_tmp_ssurface2.html', forms=forms)
    # return render_template('Index.html', # form=form, forms=forms)

@app.route('/TMP-SS', methods=['GET', 'POST'])
def Index_tmp_ssp():
    # name = None

    forms = FastaForm()
    if forms.validate_on_submit():
        email = []
        email.append(forms.email.data)
        print(forms.file.data)
        uuid_s = uuid.uuid1()
        print(uuid_s)
        uuid_fasta = '/home/public/%s.fasta' % uuid_s
        # pathlib.Path(uuid_fasta).touch()
        uuid_text = '/home/public/%s.txt' % uuid_s
        uuid_text2 = '/home/public/%s.txt2' % uuid_s
        pathlib.Path(uuid_text).touch()

        if forms.m_fasta.data:
            m_seq = forms.m_fasta.data
            # f = open(uuid_fasta, 'w')
            # f.close()
            with open(uuid_fasta, "w") as ws:
                ws.write(m_seq)

            pre = Predict()
            zpred = pre.get_result_TMZC(uuid_fasta)
            y_pred = pre.get_result_tmp_ssurface2(uuid_fasta,zpred)
            #print(y_pred)
            out2 = Outputs()
            out2.output_result_tmp_ssurface_2(uuid_fasta, y_pred, uuid_text)
            out2.print_result_tmp_ssurface_2(uuid_fasta, y_pred, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from ICDtools",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass

            try:
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()
            except OSError:
                pass

            return render_template('Result2_tmp_ssp.html', message=result2)

        elif forms.file.data:
            # filename = forms.file.data.filename
            filename = fastas.save(forms.file.data, name='home/public/demo.')
            with open(filename) as fn:
                m_seq = fn.read()
                with open(uuid_fasta, "w+") as f:
                    f.write(m_seq)

            pre = Predict()
            zpred = pre.get_result_TMZC(uuid_fasta)
            y_pred = pre.get_result_tmp_ssurface2(uuid_fasta,zpred)
            out = Outputs()
            out.output_result_tmp_ssurface2(uuid_fasta, y_pred, uuid_text)
            out.print_result_tmp_ssurface2(uuid_fasta, y_pred, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from ICDtools",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass
            try:
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()
            except OSError:
                pass
            return render_template('Result2_tmp_ssp.html', message=result2)
    return render_template('Index_tmp_ssp.html', forms=forms)
    # return render_template('Index.html', # form=form, forms=forms)

@app.route('/mpls_pred', methods=['GET', 'POST'])
def Index_mpls_pred():
    # name = None
    # forms = element.AdvancedForm()
    forms = FastaForm()
    if forms.validate_on_submit():
        email = []
        email.append(forms.email.data)
        print(forms.file.data)
        uuid_s = uuid.uuid1()
        print(uuid_s)
        uuid_fasta = '/home/public/%s.fasta' % uuid_s
        pathlib.Path(uuid_fasta).touch()
        uuid_text = '/home/public/%s.txt' % uuid_s
        pathlib.Path(uuid_text).touch()
        if forms.m_fasta.data:
            #     #
            #     # msg = Message("Result from ICDtools",
            #     #               sender="nenubiodata@126.com",
            #     #               recipients=email)
            #     # msg.html = '111'
            #     # mail.send(msg)
            m_seq = forms.m_fasta.data
            # f = open(uuid_fasta, 'w')
            # f.close()
            with open(uuid_fasta, "w") as ws:
                ws.write(m_seq)
            pre = Predict()
            result_dic, index_dic, required_dic = pre.get_result_mpls_pred(uuid_fasta)
            out = Outputs()
            out.output_result_mpls_pred(required_dic, index_dic, result_dic, uuid_text)
            with open(uuid_text, 'r') as ut:
                result = ut.read()
                msg = Message("Result from ICDtools",
                              sender="nenubiodata@126.com",
                              recipients=email)
                msg.html = result
                mail.send(msg)
            return render_template('Result2_mpls_pred.html')
        elif forms.file.data:
            # filename = forms.file.data.filename
            filename = fastas.save(forms.file.data, name='home/public/demo.')
            with open(filename) as fn:
                m_seq = fn.read()
                with open(uuid_fasta, "w+") as f:
                    f.write(m_seq)

            pre = Predict()
            result_dic, index_dic, required_dic = pre.get_result(uuid_fasta)

            out = Outputs()
            out.output_result(required_dic, index_dic, result_dic, uuid_text)

            with open(uuid_text, 'r') as ut:
                result = ut.read()
                msg = Message("Result from ICDtools",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                msg.html = result
                mail.send(msg)
            return render_template('Result2_mpls_pred.html')
    return render_template('Index_mpls_pred.html', forms=forms)
    # return render_template('Index.html', # form=form, forms=forms)


@app.route('/dmctop', methods=['GET', 'POST'])
def thread_dmctop():
    # name = None
    forms = FastaForm()
    if forms.validate_on_submit():
        uuid_s = uuid.uuid1()
        print(uuid_s)
        uuid_fasta = '/home/public/%s.fasta' % uuid_s
        # pathlib.Path(uuid_fasta).touch()
        uuid_text = '/home/public/%s.txt' % uuid_s
        pathlib.Path(uuid_text).touch()

        if forms.m_fasta.data:
            m_seq = forms.m_fasta.data
            # f = open(uuid_fasta, 'w')
            # f.close()
            with open(uuid_fasta, "w") as ws:
                ws.write(m_seq)
                
            executor.submit(run_dmctop,forms,uuid_fasta,uuid_text)

            return render_template('Result2_dmctop.html')

        elif forms.file.data:
            # filename = forms.file.data.filename
            filename = fastas.save(forms.file.data, name='home/public/demo.')
            with open(filename) as fn:
                m_seq = fn.read()
                with open(uuid_fasta, "w+") as f:
                    f.write(m_seq)
            executor.submit(run_dmctop,forms,uuid_fasta,uuid_text)
            
            return render_template('Result2_dmctop.html')
        
    return render_template('Index_dmctop.html', forms=forms)

def run_dmctop(forms,uuid_fasta,uuid_text):

    email = []
    email.append(forms.email.data)
    
    pre = Predict()
    pre.get_result_dmctop(uuid_fasta)
    out = Outputs()
    out.output_result_dmctop(uuid_fasta, uuid_text)
    #print('okkk')

    with open(uuid_text, 'r') as ut:
        result = ut.read()
        #print(result)
        with app.app_context():
            msg = Message("Result from ICDtools",
                      sender="nenubiodata@126.com",
                      recipients=email)
            print(result)
            msg.html = result
            print('ready')
            mail.send(msg) 
            print('send')

    return render_template('Result3_dmctop.html', message=result2)    

        
            
@app.route('/TM-ZC', methods=['GET', 'POST'])
def Index_TMZC():
    # name = None

    forms = FastaForm()
    if forms.validate_on_submit():
        email = []
        email.append(forms.email.data)
        print(forms.file.data)
        uuid_s = uuid.uuid1()
        print(uuid_s)
        uuid_fasta = '/home/public/%s.fasta' % uuid_s
        # pathlib.Path(uuid_fasta).touch()
        uuid_text = '/home/public/%s.txt' % uuid_s
        uuid_text2 = '/home/public/%s.txt2' % uuid_s
        pathlib.Path(uuid_text).touch()

        if forms.m_fasta.data:
            m_seq = forms.m_fasta.data
            # f = open(uuid_fasta, 'w')
            # f.close()
            with open(uuid_fasta, "w") as ws:
                ws.write(m_seq)

            pre = Predict()
            y_pred = pre.get_result_TMZC(uuid_fasta)
            out = Outputs()
            out.output_result_TMZC(uuid_fasta, y_pred, uuid_text)
            out.print_result_TMZC(uuid_fasta, y_pred, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from TM-ZC",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass

            try:
                with open(uuid_fasta, 'r') as ut2:
                    seq = ut2.read()
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()
            except OSError:
                pass
            return render_template('Result2_TM-ZC.html', sequence=seq, message=result2)

        elif forms.file.data:
            # filename = forms.file.data.filename
            filename = fastas.save(forms.file.data, name='home/public/TM-ZC_file.fatsa')
            with open(filename) as fn:
                m_seq = fn.read()
                with open(uuid_fasta, "w+") as f:
                    f.write(m_seq)

            pre = Predict()
            y_pred = pre.get_result_TMZC(uuid_fasta)
            out = Outputs()
            out.output_result_TMZC(uuid_fasta, y_pred, uuid_text)
            out.print_result_TMZC(uuid_fasta, y_pred, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from TM-ZC",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass
            try:
                with open(uuid_fasta, 'r') as ut2:
                    seq = ut2.read()
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()

            except OSError:
                pass
            return render_template('Result2_TM-ZC.html', sequence=seq, message=result2)
    return render_template('Index_TM-ZC.html', forms=forms)
    # return render_template('Index.html', # form=form, forms=forms)


@app.route('/UBPs-Pred', methods=['GET', 'POST'])
def Index_UBPsPred():
    # name = None

    forms = FastaForm()
    if forms.validate_on_submit():
        email = []
        email.append(forms.email.data)
        print(forms.file.data)
        uuid_s = uuid.uuid1()
        print(uuid_s)
        uuid_fasta = '/home/public/%s.fasta' % uuid_s
        uuid_text = '/home/public/%s.txt' % uuid_s
        uuid_text2 = '/home/public/%s.txt2' % uuid_s
        pathlib.Path(uuid_text).touch()

        if forms.m_fasta.data:
            m_seq = forms.m_fasta.data
            # f = open(uuid_fasta, 'w')
            # f.close()
            with open(uuid_fasta, "w") as ws:
                ws.write(m_seq)

            address = uuid_fasta
            predict = Test()
            result = predict.Prediction(address)
            out = Output()
            out.output_result_UBPsPred(uuid_fasta, result, uuid_text)
            out.print_result_UBPsPred(uuid_fasta, result, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from UBPs-Pred",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass

            try:
                with open(uuid_fasta, 'r') as ut2:
                    seq = ut2.read()
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()
            except OSError:
                pass
            return render_template('Result2_UBPs-Pred.html', sequence=seq, message=result2)
        elif forms.file.data:
            # filename = forms.file.data.filename
            filename = fastas.save(forms.file.data, name='home/public/UBPs-Pred.fatsa')
            with open(filename) as fn:
                m_seq = fn.read()
                with open(uuid_fasta, "w+") as f:
                    f.write(m_seq)

            address = uuid_fasta
            predict = Test()
            result = predict.Prediction(address)
            out = Output()
            out.output_result_UBPsPred(uuid_fasta, result, uuid_text)
            out.print_result_UBPsPred(uuid_fasta, result, uuid_text2)

            try:
                with open(uuid_text, 'r') as ut:
                    result = ut.read()
                    msg = Message("Result from UBPs-Pred",
                                  sender="nenubiodata@126.com",
                                  recipients=email)
                    msg.html = result
                    mail.send(msg)
            except OSError:
                pass
            try:
                with open(uuid_fasta, 'r') as ut2:
                    seq = ut2.read()
                with open(uuid_text2, 'r') as ut2:
                    result2 = ut2.read()

            except OSError:
                pass
            return render_template('Result2_UBPs-Pred.html', sequence=seq, message=result2)
    return render_template('Index_UBPs-Pred.html', forms=forms)


APP_ROOT = os.path.dirname(os.path.abspath(__file__))  # refers to application_top
gsemodel_path = os.path.join(APP_ROOT, 'static/deepcsd/GSEMODEL')  
tsv_path = os.path.join(APP_ROOT, 'static/deepcsd/tsv')  
new_tsv_path = os.path.join(APP_ROOT, 'static/deepcsd/new_tsv')  
new_gsemodel_path = os.path.join(APP_ROOT, 'static/deepcsd/new_model')  

UPLOAD_FOLDER = 'static/deepcsd/new_tsv'  
ALLOWED_EXTENSIONS = {'txt', 'tsv'}  # 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
UPLOAD_FOLDER2 = '/var/www/Flask/static/deepcsd/new_model'  #
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 * 1024



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/deepcsd', methods=['GET', 'POST'])
def Index_deepcsd():
    return render_template('Index_deepcsd.html')


@app.route('/deepcsd/tool1', methods=['GET', 'POST'])
def submit_deepcsd():
    if request.method == "POST":
        # 1.Select the Way of inputing Gene Data and Input it
        database1 = request.values.get("optionsRadios")
        if database1 == "option1":
            choice1 = 'yes'
            if choice1 == 'yes':
                return render_template('Result_deepcsd.html', deep="Sorry,this function is under development.")
            if request.method == 'POST':
                file1 = request.files['myfile1']
                if file1 and allowed_file(file1.filename):
                    filename1 = secure_filename(file1.filename)
                    file1.save(os.path.join(app.config['UPLOAD_FOLDER'], filename1))
                    file_path1 = r"/var/www/Flask/static/deepcsd/new_tsv" + "/" + filename1
                    with open(file_path1, 'r') as f:
                        line1 = f.readline().strip()
        elif database1 == "option2":
            database12 = request.form.get("myselect")
            choice1 = 'no'
        # 2. Select the model you want to use
        database2 = request.values.get("module")
        if database2 == "module1":
            database21 = request.form.get("myselect2")
            choice2 = 'yes'
        elif database2 == "module2":
            if request.method == 'POST':
                choice2 = 'no'
                if choice2 == 'no':
                    return render_template('Result_deepcsd.html', deep="Sorry,this function is under development.")
                # trained data
                file2 = request.files['myfile2']
                if file2 and allowed_file(file2.filename):
                    filename2 = secure_filename(file2.filename)
                    file2.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename2))
                    file_path2 = r"/static/deepcsd/new_model" + "/" + filename2
                    with open(file_path2, 'r') as f:
                        line2 = f.readline().strip()
                # trained label
                file3 = request.files['myfile3']
                if file3 and allowed_file(file3.filename):
                    filename3 = secure_filename(file3.filename)
                    file3.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename3))
                    file_path3 = r"/static/deepcsd/new_model" + "/" + filename3
                    with open(file_path3, 'r') as f:
                        line3 = f.readline().strip()
                database21 = request.form.get("path")  # name
                database22 = request.values.get("numfold")  # k-fold
                file4 = request.files['myfile4']  # test data
                if file4 and allowed_file(file4.filename):
                    filename4 = secure_filename(file4.filename)
                    file4.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename4))
                    file_path4 = r"/static/deepcsd/new_model" + "/" + filename4
                    with open(file_path4, 'r') as f:
                        line4 = f.readline().strip()
                file5 = request.files['myfile5']  # test label
                if file5 and allowed_file(file5.filename):
                    filename5 = secure_filename(file5.filename)
                    file5.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename5))
                    file_path5 = r"/static/deepcsd/new_model" + "/" + filename5
                    print(file_path5)
                    with open(file_path5, 'r') as f:
                        line5 = f.readline().strip()
        # 3.Do you need the parameters of the model?
        database3 = request.values.get("if")
        if database3 == "y":
            choice3 = 'yes'
        elif database3 == "n":
            choice3 = 'no'
        # 4.Choose how to get results
        database4 = request.values.get("way")
        # Wait for the result to be displayed on the page
        if database4 == "way1":
            choice4 = 'yes'
        # Send the result directly to your email
        elif database4 == "way2":
            choice4 = 'no'
            mailname = request.form.get("mymail")

        #     email
        # 1.2+2.1+4.2
        if choice1 == 'no' and choice2 == 'yes' and choice4 == 'no':
            database121 = database12 + "_frma_expression"
            gene_expression = load_data(os.path.join(tsv_path, database121), os.path.join(gsemodel_path, database12))
            try:
                model = get_trained_model(database12.strip())
                result = predict(os.path.join(tsv_path, database121), gene_expression, model)
                mailname = request.form.get("mymail")
                f = open('/var/www/Flask/static/deepcsd/mapresult.txt', 'w+')
                for j in range(len(result)):
                    f.write(result[j])
                    f.write('\n')
                f.close()
                try:
                    message = Message(subject='result of DeepCSD', sender="nenubiodata@126.com", recipients=[mailname],
                                      body="Please check the attached file")

                    if choice3 == 'no':
                        with open("/var/www/Flask/static/deepcsd/mapresult.txt", 'r') as fp:
                            message.attach("mapresult.txt", "/txt", fp.read())
                        fp.close()
                        mail.send(message)
                        os.remove("/var/www/Flask/static/deepcsd/mapresult.txt")
                        return render_template('Result_deepcsd.html', modelname=database12,
                                               deep='The email has been sent successfully. Please check')
                    elif choice3 == 'yes':
                        with open("/var/www/Flask/static/deepcsd/mapresult.txt", 'r') as fp1:
                            message.attach("mapresult.txt", "/txt", fp1.read())
                        # mail.send(message)
                        fp1.close()
                        name12 = database12 + ".h5"
                        h5name = os.path.join(gsemodel_path, name12)
                        with open(h5name, 'rb') as fp2:
                            message.attach(name12, "/h5", fp2.read())
                        fp2.close()
                        mail.send(message)
                        os.remove("/var/www/Flask/static/deepcsd/mapresult.txt")
                        # return render_template('Result_deepcsd.html',modelname=database12)
                        return render_template('Result_deepcsd.html', modelname=database12,
                                               deep='The email has been sent successfully. Please check')
                except Exception as e:
                    return render_template('Result_deepcsd.html',
                                           deep='The email was not successfully sent. Please check whether your email address is filled in correctly')
                # os.remove(os.path.join(new_tsv_path, file_path1))
            except Exception as e:
                print(e)
                return render_template('Result_deepcsd.html', deep='Data Error')
        # 1.2+2.1+4.1
        elif choice1 == 'no' and choice2 == 'yes' and choice4 == 'yes':
            database121 = database12 + "_frma_expression"
            gene_expression = load_data(os.path.join(tsv_path, database121), os.path.join(gsemodel_path, database12))
            try:
                model = get_trained_model(database12.strip())
                result = predict(os.path.join(tsv_path, database121), gene_expression, model)
                if choice3 == 'no':
                    return render_template('Result_deepcsd.html', modelname=database12, deep=result)
                elif choice3 == 'yes':
                    mailname = request.form.get("address")
                    message = Message(subject='the parameters of the model', sender="nenubiodata@126.com",
                                      recipients=[mailname],
                                      body="Please check the attached file")
                    name12 = database21 + ".h5"
                    h5name = os.path.join(gsemodel_path, name12)
                    with open(h5name, 'rb') as fp2:
                        message.attach(name12, "/h5", fp2.read())
                    fp2.close()
                    mail.send(message)
                    return render_template('Result_deepcsd.html', modelname=database12, deep=result)
                # os.remove(os.path.join(new_tsv_path, file_path1))
            except Exception as e:
                print(e)
                return render_template('Result_deepcsd.html', deep='Data error')


# ------------------------Second------------------------------
@app.route('/Guide')
def Guide():
    return render_template('Guide.html')


@app.route('/Document')
def Document():
    return render_template('Document.html')


@app.route('/deepcsd/Document')
def Document_deepcsd():
    return render_template('Document_deepcsd.html')


@app.route('/tmp_ssurface/Document')
def Document_tmp_ssurface():
    return render_template('Document_tmp_ssurface.html')

@app.route('/TMP-SSurface-2.0/Document')
def Document_tmp_ssurface2():
    return render_template('Document_tmp_ssurface2.html')

@app.route('/TMP-SS/Document')
def Document_tmp_ssp():
    return render_template('Document_tmp_ssp.html')

@app.route('/mpls_pred/Document')
def Document_mpls_pred():
    return render_template('Document_mpls_pred.html')


@app.route('/dmctop/Document')
def Document_dmctop():
    return render_template('Document_dmctop.html')


@app.route('/TM-ZC/Document')
def Document_TMZC():
    return render_template('Document_TM-ZC.html')


@app.route('/UBPs-Pred/Document')
def Document_UBPsPred():
    return render_template('Document_UBPs-Pred.html')


@app.route("/download/static/tmp_ssurface_data.zip", methods=['GET'])
def download_tmp_ssurface_data():
    # return app.send_static_file(filepath)
    directory = ""
    filename = "static/tmp_ssurface_data.zip"
    print(directory + filename)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/download/static/tmp_ssurface_project.zip", methods=['GET'])
def download_tmp_ssurface_project():
    # return app.send_static_file(filepath)
    directory = ""
    filename = "static/tmp_ssurface_project.zip"
    print(directory + filename)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/download/static/TMP-SSurface-2.0.zip", methods=['GET'])
def download_tmp_ssurface2_data():
    # return app.send_static_file(filepath)
    directory = ""
    filename = "static/TMP-SSurface-2.0.zip"
    print(directory + filename)
    return send_from_directory(directory, filename, as_attachment=True)

@app.route("/download/static/TM-ZC_data.rar", methods=['GET'])
def download_TMZC_data():
    # return app.send_static_file(filepath)
    directory = ""
    filename = "static/TM-ZC_data.rar"
    print(directory + filename)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route("/download/static/UBPs-Pred_data.rar", methods=['GET'])
def download_UBPsPred_data():
    # return app.send_static_file(filepath)
    directory = ""
    filename = "static/UBPs-Pred_data.rar"
    print(directory + filename)
    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/Downloads')
def Downloads():
    return render_template('Downloads.html')


@app.route("/deepcsd_download/<filename>", methods=['GET', 'POST'])
def deepcsd_download(filename):
    print(filename)
    directory = r"/var/www/Flask/static/deepcsd/GSEMODEL/"

    return send_from_directory(directory, filename, as_attachment=True)


@app.route('/deepcsd/Downloads')
def Downloads_deepcsd():
    return render_template('Downloads_deepcsd.html')


@app.route('/tmp_ssurface/Downloads')
def Downloads_tmp_ssurface():
    return render_template('Downloads_tmp_ssurface.html')

@app.route('/TMP-SSurface-2.0/Downloads')
def Downloads_tmp_ssurface2():
    return render_template('Downloads_tmp_ssurface2.html')

@app.route('/TMP-SS/Downloads')
def Downloads_tmp_ssp():
    return render_template('Downloads_tmp_ssp.html')

@app.route('/mpls_pred/Downloads')
def Downloads_mpls_pred():
    return render_template('Downloads_mpls_pred.html')


@app.route('/dmctop/Downloads')
def Downloads_dmctop():
    return render_template('Downloads_dmctop.html')


@app.route('/TM-ZC/Downloads')
def Downloads_TMZC():
    return render_template('Downloads_TM-ZC.html')


@app.route('/UBPs-Pred/Downloads')
def Downloads_UBPsPred():
    return render_template('Downloads_UBPs-Pred.html')


@app.route('/deepcsd/tool')
def Submit_deepcsd():
    return render_template('submitData_deepcsd.html')


@app.route('/Contact')
def Contact():
    return render_template('Contact.html')


@app.route('/deepcsd/Contact')
def Contact1():
    return render_template('Contact_deepcsd.html')


# -----------------------Error Page---------------------------
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
#


# ------------------------Future-------------------------------
"""
@app.route('/Submit/')
def Submit():
    return render_template('GeneResults.html')
"""
if __name__ == "__main__":
    app.run(threaded=True)
