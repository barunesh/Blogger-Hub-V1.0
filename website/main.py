from flask import Flask, render_template,flash,redirect,url_for, session,request, logging, make_response
#from data import Articles
from prediction import Predictions
import random
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps


app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'B@runesh97'
app.config['MYSQL_DB'] = 'website'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

#Articles = Articles()
image_list = ['Laptop','Laptop cover','Laptop skins','Mobile','Mobile Covers','Earphone','Ipod Charger','Ipod','Laptop Charger','Mobile Charger']
def select_image(predicted='0', img='None'):
    folder='img/'
    image=[]
    list=[]
    if predicted == '1' and img != 'None':
        list = Predictions(img)
    else:
        list = image_list
    for img in list:
        img = random.choice(list)
        img = folder+img+'.jpg'
        image.append(img)
    return image

class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm Password')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=200)])
    body = TextAreaField('Body', [validators.Length(min=30)])

@app.route('/')
def index():
    resp = make_response(render_template('home.html',image=select_image()))
    resp.set_cookie('_predict', '0')
    resp.set_cookie('_img','None')
    return resp

@app.route('/dashboard')
@is_logged_in
def dashboard():
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles WHERE author = %s", [session['username']])

    articles = cur.fetchall()

    if result > 0:
        return render_template('dashboard.html', articles=articles, image=image)
    else:
        msg = 'No Articles Found'
        return render_template('dashboard.html', msg=msg, image=image)

    cur.close()


@app.route('/about')
def about():
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)
    return render_template('about.html',image=image)

@app.route('/contact')
def contact():
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)
    return render_template('contact.html',image=image)

@app.route('/articles')
def articles():
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM articles")

    articles = cur.fetchall()

    if result > 0:
        return render_template('articles.html', articles=articles, image=image)
    else:
        msg = 'No Articles Found'
        return render_template('articles.html', msg=msg, image=image)

    cur.close()


@app.route('/article/<string:id>/')
def article(id):
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)
    cur = mysql.connection.cursor()


    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    return render_template('article.html' , article=article, image=image)

@app.route('/edit_article/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def edit_article(id):
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)

    cur = mysql.connection.cursor()


    result = cur.execute("SELECT * FROM articles WHERE id = %s", [id])

    article = cur.fetchone()
    cur.close()

    form = ArticleForm(request.form)


    form.title.data = article['title']
    form.body.data = article['body']

    if request.method == 'POST' and form.validate():
        title = request.form['title']
        body = request.form['body']


        cur = mysql.connection.cursor()
        app.logger.info(title)

        cur.execute ("UPDATE articles SET title=%s, body=%s WHERE id=%s",(title, body, id))

        mysql.connection.commit()


        cur.close()

        flash('Article Updated', 'success')

        return redirect(url_for('dashboard'))

    return render_template('edit_article.html', form=form, image=image)

@app.route('/delete_article/<string:id>', methods=['POST'])
@is_logged_in
def delete_article(id):

    cur = mysql.connection.cursor()


    cur.execute("DELETE FROM articles WHERE id = %s", [id])


    mysql.connection.commit()


    cur.close()

    flash('Article Deleted', 'success')

    return redirect(url_for('dashboard'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))


        cur = mysql.connection.cursor()


        cur.execute("INSERT INTO users(name, email, username, password) VALUES(%s, %s, %s, %s)", (name, email, username, password))


        mysql.connection.commit()


        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form, image=image)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = RegisterForm(request.form)
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)
    if request.method == 'POST':

        username = request.form['username']
        password_candidate = request.form['password']


        cur = mysql.connection.cursor()


        result = cur.execute("SELECT * FROM users WHERE username = %s", [username])

        if result > 0:

            data = cur.fetchone()
            password = data['password']


            if sha256_crypt.verify(password_candidate, password):

                session['logged_in'] = True
                session['username'] = username

                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error, image=image)

            cur.close()
        else:
            error = 'Username not found'
            return render_template('login.html', error=error, image=image)

    return render_template('login.html', image=image)


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/add_article', methods=['GET', 'POST'])
@is_logged_in
def add_article():
    predicted = request.cookies.get('_predict')
    img = request.cookies.get('_img')
    image=[]
    image = select_image(predicted, img)
    form = ArticleForm(request.form)
    if request.method == 'POST' and form.validate():
        title = form.title.data
        body = form.body.data


        cur = mysql.connection.cursor()


        cur.execute("INSERT INTO articles(title, body, author) VALUES(%s, %s, %s)",(title, body, session['username']))


        mysql.connection.commit()

        
        cur.close()

        flash('Article Created', 'success')

        return redirect(url_for('dashboard'))

    return render_template('add_article.html', form=form, image=image)

if __name__ == '__main__':
    app.secret_key = 'secret123'
    app.run(debug=True)
