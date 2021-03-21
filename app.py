from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
# ----------userLogin,Logout ,register libraries----------------
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Email, Length
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
# from flask_user import roles_required
# from flask_admin import admin
from base64 import b64encode

# uygulama konfigerasyonlar (ayarlari)-----------
app = Flask(__name__)

# veritabani ile baglanma kodu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

app.config['SECRET_KEY'] = 'thisisasecret'

# ne yapiyor bu belki tum telefon ayarlari yapar
Bootstrap(app)

# veri yapani baglanti kurmak
db = SQLAlchemy(app)

# bunlar hesapa giris yapildinda hesabi tutar ve kim oldugunu belirlenir
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# --------------------------------------------------------

# Flask-Login integration
# NOTE: is_authenticated, is_active, and is_anonymous
# are methods in Flask-Login < 0.3.0
# @property
# def is_authenticated(self):
#     return True
#
#
# @property
# def is_active(self):
#     return True
#
#
# @property
# def is_anonymous(self):
#     return False
#
#
# def get_id(self):
#     return self.id
#
#
# # Required for administrative interface
# def __unicode__(self):
#     return self.username

# login class -----------------------------------------------------------------------------
class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=7, max=30)])
    remember = BooleanField('remember me')


# login sayfasi ------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('indexuser'))

        return '<h2>Invalid username or password </h2>'
    return render_template('login.html', form=form)


# ----------------------------------------------------------------------------------------

# register class ----------------------------------------------------------------------------------------
class RegisterForm(FlaskForm):
    # string email first name .. vs bunlar ekranda label seklinde gosterilecektir
    email = StringField('Email :', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    FirstName = StringField('First Name :', validators=[InputRequired(), Length(min=1, max=20)])
    LastName = StringField('Last Name :', validators=[InputRequired(), Length(min=1, max=25)])
    username = StringField('Username :', validators=[InputRequired(), Length(min=7, max=30)])
    password = PasswordField('Password :', validators=[InputRequired(), Length(min=8, max=80)])


# register syfasi -----
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        #username fname ...vs bunlar veritabanideki ayni adilar olmasi lazim dikkat hata verir !!!
        yeni_kullanci = User(username=form.username.data, fname=form.FirstName.data, lname=form.LastName.data,email=form.email.data, password=hashed_password)
        db.session.add(yeni_kullanci)
        db.session.commit()
        # eger olustu ise login sayfasina yonla beni
        flash('Thanks for registering')
        # eger olustu ise login sayfasina yonla beni
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)


# -------------------------------------------------------------------------------------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# @login_required kelimesi bu sayifa acilmak icin giris yapmalisin demektir

# logout---------------------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# --------------------------------------------------------

# ORM`ler ile oluşturlan tablolar--------------------------
class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ev_adresi = db.Column(db.String(50))
    oda_sayisi = db.Column(db.String(50))
    fiyat = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    aciklama = db.Column(db.Text)


# user mixin ekliyoruz user kim oldugunu belirtlemek icin
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80), nullable=False)
    fname = db.Column(db.String(20), nullable=True)
    lname = db.Column(db.String(25), nullable=True)
    fnumber = db.Column(db.String(20), nullable=True)
    photo = db.Column(db.LargeBinary, nullable=True)


# img
class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    person_id = db.Column(db.Integer, db.ForeignKey('User.id'),
                          nullable=False)


# admin
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    email = db.Column(db.String(40), unique=True)
    password = db.Column(db.String(100))


# --------------------------------------------------------
@app.route('/upload', methods=['POST'])
def upload():
    pic = request.files['pic']
    if not pic:
        return 'No pic uploaded!', 400

    filename = secure_filename(pic.filename)
    mimetype = pic.mimetype
    if not filename or not mimetype:
        return 'Bad upload!', 400

    img = Img(img=pic.read(), name=filename, mimetype=mimetype ,person_id=current_user.id)
    db.session.add(img)
    db.session.commit()
    img= Img.query.filter_by(person_id=current_user.id).one()
    flash('Img Uploaded!', 200)

    return render_template('profile.html',userimg= img)


@app.route('/<int:id>')
def get_img(id):
    img = Img.query.filter_by(id=id).first()
    if not img:
        return 'Img Not Found!', 404

    return Response(img.img, mimetype=img.mimetype)


# okuma kodu --------------------------------------------
@app.route('/')
def index():
    posts1 = Blogpost.query \
        .order_by(Blogpost.date_posted.desc()).all()

    return render_template('index.html', posts=(posts1))


@app.route('/indexAdmin')
@login_required
def indexAdmin():
    posts1 = Blogpost.query \
        .order_by(Blogpost.date_posted.desc()).all()

    return render_template('admin/indexAdmin.html', posts=(posts1))

@app.route('/indexuser')
@login_required
def indexuser():
    userData = User.query.filter_by(id=current_user.id).one()

    posts1 = Blogpost.query \
        .order_by(Blogpost.date_posted.desc()).all()

    return render_template('user/indexuser.html', userData=userData,posts=(posts1))

@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)


@app.route('/profile')
@login_required
def profile():
    userData = User.query.filter_by(id=current_user.id).one()
    return render_template('profile.html', userData=userData)


@app.route('/adminprofile')
@login_required
def adminprofile():
    userData = User.query.filter_by(id=current_user.id).one()
    return render_template('admin/adminprofile.html', userData=userData)


# profile edit
@app.route('/profile_update', methods=['POST'])
@login_required
def profile_update():
    fname = request.form['fname']
    lname = request.form['lname']
    fnumber = request.form['fnumber']
    email = request.form['email']
    username = request.form['username']

    db.session.query(User) \
        .filter(User.id == current_user.id) \
        .update({User.fname: fname \
                    , User.lname: lname \
                    , User.fnumber: fnumber \
                    , User.email: email \
                    , User.username: username})

    db.session.commit()

    return redirect(url_for('adminboard'))


# ------------------------------------------------------
# ekleme kodu ------------------------------------------
@app.route('/add')
@login_required
def add():
    return render_template('admin/add.html')


@app.route('/addpost', methods=['POST'])
def addpost():
    ev_adresi = request.form['ev_adresi']
    oda_sayisi = request.form['oda_sayisi']
    fiyat = request.form['fiyat']
    aciklama = request.form['aciklama']

    post = Blogpost(ev_adresi=ev_adresi \
                    , oda_sayisi=oda_sayisi \
                    , fiyat=fiyat \
                    , aciklama=aciklama \
                    , date_posted=datetime.now())

    db.session.add(post)
    db.session.commit()

    return redirect(url_for('indexAdmin'))


# -----------------------------------------------------
# silme kodu ------------------------------------------
@app.route('/delete')
@login_required
def delete():
    return render_template('admin/ilansil.html')


@app.route('/deletepost', methods=['POST'])
def deletepost():
    ilan_no = request.form['id']

    ev_sil = db.session.query(Blogpost) \
        .filter(Blogpost.id == ilan_no).first()
    db.session.delete(ev_sil)
    db.session.commit()

    return redirect(url_for('indexAdmin'))


# -----------------------------------------------------
# güncelleme kodu ----------------------------------------
@app.route('/update')
@login_required
def update():
    return render_template('admin/update.html')


@app.route('/updatepost', methods=['POST'])
@login_required
def updatepost():
    ilan_no = request.form['id']
    fiyat = request.form['fiyat']
    ev_adresi = request.form['ev_adresi']
    oda_sayisi = request.form['oda_sayisi']
    aciklama = request.form['aciklama']

    db.session.query(Blogpost) \
        .filter(Blogpost.id == ilan_no) \
        .update({Blogpost.fiyat: fiyat \
                    , Blogpost.ev_adresi: ev_adresi \
                    , Blogpost.oda_sayisi: oda_sayisi \
                    , Blogpost.aciklama: aciklama \
                    , Blogpost.fiyat: fiyat})

    db.session.commit()

    return redirect(url_for('indexAdmin'))


# yonetme sayfasi-----------------------------
@app.route('/adminboard')
@login_required
# @roles_required('Admin')
def adminboard():
    # veritabanidaki kullancilari listeliyor
    users = User.query.all()
    admins = Admin.query.all()
    imgs=Img.query.all()

    # burda name degiskeni html kodu icinde tanimlanan degeri alip oraya atiyor
    # users veritanindan alip o sayfaya atiyor
    return render_template("admin/adminboard.html", imgs=imgs, admins=admins, users=users, name=current_user.username)


# -------------------------------------------------------------

@app.route('/adminlog', methods=['GET', 'POST'])
def adminlog():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin:
            if check_password_hash(admin.password, form.password.data):
                login_user(admin, remember=form.remember.data)
                return redirect(url_for('adminboard'))

        return '<h2>Invalid username or password </h2>'
    return render_template('admin/adminLogin.html', form=form)


# register admin -----
@app.route('/adminsignup', methods=['GET', 'POST'])
def adminsignup():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        yeni_kullanci = Admin(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(yeni_kullanci)
        db.session.commit()
        flash('Thanks for registering')
        # eger olustu ise login sayfasina yonla beni
        return redirect(url_for('adminlog'))

    return render_template('admin/adminsignup.html', form=form)


# ------------------------------------------------------


# ******************************************************


if __name__ == '__main__':
    app.run()
