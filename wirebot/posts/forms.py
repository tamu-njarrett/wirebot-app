from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired


class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    picture = FileField('Choose Picture to Upload', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Post')

#### Find fix for MultipleFileField #####
class PictureForm(FlaskForm):
    picture_list = FileField('Select All Pictures to Upload', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Upload')