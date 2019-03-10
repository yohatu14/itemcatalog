from flask import Flask, request,redirect, url_for, redirect, jsonify
from flask import render_template
from flask import session as login_session, flash
from config import DevelopmentConfig
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from models import Base,Users,Catalogs,Items
import httplib2
import forms
import json
import random
import string

app = Flask(__name__)
app.config.from_object(DevelopmentConfig) 
engine = create_engine('sqlite:///database.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

#Fail Page
@app.errorhandler(500)
@app.errorhandler(404)
def pagenofound(e):
    return render_template('pagenf.html', error=e)

#First Page Index
@app.route('/', methods =['GET', 'POST'])
@app.route('/index', methods =['GET', 'POST'])
def index():
    return render_template('index.html')


#Logout
@app.route('/logout')
def logout():
    if 'user' in login_session:
        login_session.pop('user')
    return redirect(url_for('login'))

#Login
@app.route('/login', methods =['GET', 'POST'])
def login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    login_form = forms.LoginForm(request.form)
    return render_template('login.html', form= login_form,STATE=state)


#Register with Facebook
@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token


    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]


    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.8/me"
    '''
        Due to the formatting for the result from the server token exchange we have to
        split the token first on commas and select the first index which gives us the key : value
        for the server access token then we split it on colons to pull out the actual token value
        and replace the remaining quotes with nothing so that it can be used directly in the graph
        api calls
    '''
    token = result.split(',')[0].split(':')[1].replace('"', '')

    url = 'https://graph.facebook.com/v2.8/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['user'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout
    login_session['access_token'] = token

    # Get user picture
    url = 'https://graph.facebook.com/v2.8/me/picture?access_token=%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['user']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    redirect(url_for('index'))
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    return "you have been logged out"

def createUser(login_session):
    newUser = Users(username=login_session['user'], password='null', email=login_session[
                   'email'])
    session.add(newUser)
    session.commit()
    user = session.query(Users).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(Users).filter_by(email=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(Users).filter_by(email=email).one()
        return user.email
        
    except:
        return None

@app.route('/ajax-login', methods =['POST'])
def ajax_login():
    login_form = forms.LoginForm(request.form)
    if request.method == 'POST' and login_form.validate():
        username=request.form['user']
        password=request.form['password']
        user = session.query(Users).filter_by(username=request.form['user']).first()
        if user is not None:
            if user.verify_password(password):
                login_session['user']=request.form['user']
                response={'success':True, 'redirect':'index'}  
                return json.dumps(response)
            else:
                flash('Error! Incorrect username or password')
                response={'success':False, 'redirect':'login'}
                return json.dumps(response)                
        else:
            flash('User don`t exists!')
            response={'success':False, 'redirect':'login'}
            return json.dumps(response)

#Create new user
@app.route('/create',methods =['GET','POST'])
def create():
    create_form= forms.CreateForm(request.form)
    if 'user' in login_session:
        redirect(url_for('index'))
    else:
        if request.method == 'POST' and create_form.validate():
            username=create_form.username.data
            email=create_form.email.data
            user = session.query(Users).filter_by(username=username).first()
            user2 = session.query(Users).filter_by(email=email).first()
            if user is None and user2 is None :
                user=Users(create_form.username.data, create_form.password.data,create_form.email.data)
                flash('User {} created!'.format(create_form.username.data))
                session.add(user)
                session.commit()
            else:
                flash('Error user alredy exists!')
                redirect(url_for('create'))
    return render_template('create.html', form= create_form)

#Add new Catalog
@app.route('/catalog',methods =['GET','POST'])
def catalog():
    add_catalog_form= forms.AddCatalogForm(request.form)
    if 'user' in login_session:
        if request.method == 'POST' and add_catalog_form.validate():
            name=add_catalog_form.namecat.data
            catalog = session.query(Catalogs).filter_by(namecat=name).first()
            if catalog is None:
                catalog=Catalogs(name)
                flash('Catalog {} created!'.format(add_catalog_form.namecat.data))
                session.add(catalog)
                session.commit()
                return redirect(url_for('index'))
            else:
                flash('Error catalog alredy exists!')
                redirect(url_for('catalog'))
        return render_template('addcatalog.html', form= add_catalog_form)
    else:
        return redirect(url_for('index'))

#Remove Catalog
@app.route('/removecatalog/<namecat>/<int:catalog_id>',methods =['GET','POST'])
def removecatalog(namecat, catalog_id):
    if 'user' in login_session:
        remove_catalog_form= forms.RemoveCatalogForm(request.form)
        remove_catalog_form.namecat.data=namecat
        removeCatalog = session.query(Catalogs).filter_by(id=catalog_id).one()
        if removeCatalog is not None:
            if request.method == 'POST' and remove_catalog_form.validate():
                session.delete(removeCatalog)
                session.commit()
                flash('Catalog {} deleted!'.format(namecat))
                return redirect(url_for('index'))
        else:
            flash('Error item dont exists!')
        return render_template('removecatalog.html', form= remove_catalog_form)
    else:
        return redirect(url_for('index'))


#Add new Item from Catalog
@app.route('/additem/<int:catalog_id>',methods =['GET','POST'])
def additem(catalog_id):
    add_item_form= forms.AddItemForm(request.form)
    if 'user' in login_session:
        if request.method == 'POST' and add_item_form.validate():
            name=add_item_form.name.data
            description=add_item_form.description.data
            catalog_id=catalog_id
            item = session.query(Items).filter_by(name=name).first()
            if item is None:
                item=Items(name,description, catalog_id=catalog_id) 
                flash('Item {} created!'.format(add_item_form.name.data))
                session.add(item)
                session.commit()
            else:
                flash('Error catalog alredy exists!')
        return render_template('additem.html', form= add_item_form)
    else:
        return redirect(url_for('index'))

#Edit Item from Catalog
@app.route('/edititem/<name>/<description>/<int:item_id>',methods =['GET','POST'])
def edititem(name, description, item_id):
    if 'user' in login_session:
        edit_item_form= forms.EditItemForm(request.form)
        editedIem = session.query(Items).filter_by(id=item_id).one()
        if editedIem is not None:
            if request.method == 'POST' and edit_item_form.validate():
                editedIem.name=request.form['name']
                editedIem.description=request.form['description']
                session.add(editedIem)
                session.commit()
                flash('Item {} edited!'.format(name))
        else:
            flash('Error item dont exists!')
        return render_template('edititem.html', name=name, description=description, item_id=item_id, form= edit_item_form)
    else:
        return redirect(url_for('index'))

#Remove Item from Catalog
@app.route('/removeitem/<name>/<description>/<int:item_id>',methods =['GET','POST'])
def removeitem(name, description, item_id):
    if 'user' in login_session:
        remove_item_form= forms.RemoveItemForm(request.form)
        remove_item_form.name.data=name
        remove_item_form.description.data=description
        removeIem = session.query(Items).filter_by(id=item_id).one()
        if removeIem is not None:
            if request.method == 'POST' and remove_item_form.validate():
                session.delete(removeIem)
                session.commit()
                flash('Item {} deleted!'.format(name))
                
        else:
            flash('Error item dont exists!')
        return render_template('removeitem.html', form= remove_item_form)
    else:
        return redirect(url_for('index'))



#Find Items from Catalog
@app.route('/catalog/<int:catalog_id>/')
def items(catalog_id):
    if 'user' in login_session:
        catalog = session.query(Catalogs).filter_by(id=catalog_id).one()
        items = session.query(Items).filter_by(
            catalog_id=catalog_id).all()
        if 'user' not in login_session :
            return render_template('index.html', catalog=catalog)
        else:
            return render_template('items.html', items=items, catalog=catalog)
    else:
        return redirect(url_for('index'))



# JSON API's
@app.route('/catalog/<int:catalog_id>/JSON')
def catalogItemJSON(catalog_id):
    catalog = session.query(Catalogs).filter_by(id=catalog_id).one()
    items = session.query(Items).filter_by(
        catalog_id=catalog_id).all()
    return jsonify(Catalog=[i.serialize for i in items])


@app.route('/items/<int:item_id>/JSON')
def itemJSON(item_id):
    item = session.query(Items).filter_by(id=item_id).one()
    return jsonify(Items=item.serialize)


@app.route('/catalog/JSON')
def catalogJSON():
    catalog = session.query(Catalogs).all()
    return jsonify(catalogs=[r.serialize for r in catalog])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    