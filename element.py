from flask_wtf import FlaskForm
from flask_uploads import UploadSet, configure_uploads
from wtforms import StringField, SubmitField, BooleanField,SelectField,TextAreaField,FileField
from wtforms.validators import Required,Email
from wtforms.fields import core
from flask_wtf.file import FileField, FileAllowed, FileRequired
class NewForm(FlaskForm):
    name = StringField('Please Enter A Gene ID', validators=[Required()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    s_fasta = TextAreaField('Single sequence prediction', validators=[Required()])
    submit = SubmitField('Submit')

class AdvancedForm(FlaskForm):
    m_fasta = TextAreaField('Input protein sequence', validators=[], render_kw={'class': 'text-body', 'rows': 13, 'columns':30 , 'placeholder': u"Input Sequence\ne.g. >4n6h_A\nDLEDNWETLNDNLKVIEKADNAAQVKDALTKMRAAALDAQKATPPKLEDKSPDSPEMKDFRHGFDILVGQIDDALKLANEGKVKEAQAAAEQLKTTRNAYIQKYLGSPGARSASSLALAIAITALYSAVCAVGLLGNVLVMFGIVRYTKMKTATNIYIFNLALADALATSTLPFQSAKYLMETWPFGELLaKAVLSIDYYNMFTSIFTLTMMSVDRYIAVCHPVKALDFRTPAKAKLINICIWVLASGVGVPIMVMAVTRPRDGAVVaMLQFPSPSWYWDTVTKICVFLFAFVVPILIITVCYGLMLLRLRSVRLLSGSKEKDRSLRRITRMVLVVVGAFVVCWAPIHIFVIVWTLVDIDRRDPLVVAALHLCIALGYANSSLNPVLYAFLDENFKRCFRQLCRKPCG\n"})
    # file = FileField('Upload file',validators=[
    #     FileRequired(),
    #     FileAllowed(['jpg', 'png'], 'Images only!')
    # ])
    file = FileField('Upload file',
                    #validators=[FileRequired(), FileAllowed(['fasta', 'fa'], 'fasta only!')]
                     )
    # Ligand = core.RadioField (
    #     label="Ligand Types",
    #     choice=(
    #         ("m1",'I do not know the ligand'),
    #         ("m2",'I know the ligand types'),
    #         ("m3", 'durg-like compound'),
    #         ("m4", 'metal'),
    #         ("m5", 'biomaromolecule'),
    #     ),
    #     default="m1"
    # )
    # Ligand_label = StringField('Ligand Types')
    # Ligand = core.RadioField(
    #     label="Ligand Types",
    #     choices=(
    #                 # ("m2",'I know the ligand types'),
    #                 ("m1", 'durg-like compound'),
    #                 ("m2", 'metal'),
    #                 ("m3", 'biomaromolecule'),
    #                 ("m4", 'I do not know the ligand'),
    #     ),
    #     default="m4"
    #     # coerce=int  
    # )
    email = StringField('Email', [Required(),
        Email(message=u'That\'s not a valid email address.')])
    submit = SubmitField('Submit')
