from wtforms import Form, StringField, TextField, validators,PasswordField, HiddenField
from wtforms.widgets import TextArea
from wtforms.fields.html5 import EmailField


class CommentForm(Form):
    username= StringField('username', 
                [validators.length(min=4, max=25, message = 'Invalid Username'), validators.Required(message = 'Required Username')])
    mail= EmailField('mail',[validators.Required(message = 'Required Username'), validators.Email(message = 'Invalid mail')])
    comment= TextField('Comment')


class LoginForm(Form):
    user= StringField('Username', 
                [validators.length(min=4, max=25, message = 'Invalid Username'), validators.Required(message = 'Required Username')])
    password= PasswordField('Password',[validators.Required(message = 'Required Password')])

class CreateForm(Form):
    username= StringField('Username', 
                [validators.length(min=4, max=25, message = 'Invalid Username'), validators.Required(message = 'Required Username')])
    email= EmailField('Email',[validators.Required(message = 'Required Username'), validators.Email(message = 'Invalid Email')])
    password= PasswordField('Password',[validators.Required(message = 'Required Password')])

class AddCatalogForm(Form):
    namecat= StringField('Name', 
                [validators.length(min=4, max=25, message = 'Invalid Name'), validators.Required(message = 'Required Name')])

class AddItemForm(Form):
    name= StringField('Name', 
                [validators.length(min=4, max=25, message = 'Invalid Name'), validators.Required(message = 'Required Name')])
    description=StringField(u'Text', widget=TextArea())

class EditItemForm(Form):
    name= StringField('Name', 
                [validators.length(min=4, max=25, message = 'Invalid Name'), validators.Required(message = 'Required Name')])
    description=StringField(u'Text', widget=TextArea())

class RemoveItemForm(Form):
    name= StringField('Name', 
                [validators.length(min=4, max=25, message = 'Invalid Name'), validators.Required(message = 'Required Name')])
    description=StringField(u'Text', widget=TextArea())

class RemoveCatalogForm(Form):
    namecat= StringField('Name', 
                [validators.length(min=4, max=25, message = 'Invalid Name'), validators.Required(message = 'Required Name')])