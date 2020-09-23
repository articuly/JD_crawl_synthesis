from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import URL


class SpiderForm(FlaskForm):
    url = StringField('商品地址：', validators=[URL()], render_kw={'class': 'form-control'})
