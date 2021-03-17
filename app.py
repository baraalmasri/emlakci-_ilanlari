from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
#----------userLogin,Logout ,register libraries----------------
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField ,PasswordField,BooleanField
from wtforms.validators import InputRequired, Email ,Length
from flask_login import LoginManager,UserMixin ,login_user , login_required, logout_user ,current_user
from werkzeug.security import generate_password_hash, check_password_hash



#uygulama konfigerasyonlar (ayarlari)-----------
app = Flask(__name__)

# veritabani ile baglanma kodu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'

app.config['SECRET_KEY'] = 'thisisasecret'

# ne yapiyor bu belki tum telefon ayarlari yapar
Bootstrap(app)

#veri yapani baglanti kurmak
db = SQLAlchemy(app)

#bunlar hesapa giris yapildinda hesabi tutar ve kim oldugunu belirlenir
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


#--------------------------------------------------------



#login class -----------------------------------------------------------------------------
class LoginForm(FlaskForm):
    username =StringField('username',validators=[InputRequired(),Length(min=4, max=15)])
    password= PasswordField('password',validators=[InputRequired(),Length(min=7,max=30)])
    remember =BooleanField('remember me')

#login sayfasi ------
@app.route('/login',methods=['GET','POST'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('indexAdmin'))

        return '<h2>Invalid username or password </h2>'
    return render_template('login.html',form=form)
#----------------------------------------------------------------------------------------

#register class ----------------------------------------------------------------------------------------
class RegisterForm (FlaskForm):
    email= StringField('mail',validators=[InputRequired(),Email(message='Invalid email'),Length(max=50)])
    username=StringField('username',validators=[InputRequired(),Length(min=7,max=30)])
    password=PasswordField('password',validators=[InputRequired(),Length(min=8,max=80)])

#register syfasi -----
@app.route('/signup' ,methods=['GET','POST'])
def signup():
    form= RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        yeni_kullanci=User(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(yeni_kullanci)
        db.session.commit()
        #eger olustu ise login sayfasina yonla beni
        return '''   <div class="alert alert-primary" role="alert">
    <strong>Well done!</strong> You successfully read this
    important alert message.</div></br>
    <a href="login" class="btn btn-primary btn-lg" role="button" aria-pressed="true">login</a>
</div>'''

    return render_template('signup.html',form=form)
#-------------------------------------------------------------------------------------------------

@login_manager.user_loader
def load_user (user_id):
    return User.query.get(int(user_id))
#@login_required kelimesi bu sayifa acilmak icin giris yapmalisin demektir

#logout---------------------------------------------------
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
#--------------------------------------------------------

# ORM`ler ile oluşturlan tablolar--------------------------
class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ev_adresi = db.Column(db.String(50))
    oda_sayisi = db.Column(db.String(50))
    fiyat = db.Column(db.String(20))
    date_posted = db.Column(db.DateTime)
    aciklama = db.Column(db.Text)


class emlak_sahibi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    adres = db.Column(db.String(150))
    cinsiyet = db.Column(db.String(30))
    yas = db.Column(db.Integer)
    ad = db.Column(db.String(40))

#user mixin ekliyoruz user kim oldugunu belirtlemek icin
class User(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(15),unique=True)
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(80))

#admin
class Admin(UserMixin,db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username=db.Column(db.String(40),unique=True)
    email = db.Column(db.String(40), unique=True)
    password=db.Column(db.String(100))
#--------------------------------------------------------

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

    return render_template('indexAdmin.html', posts=(posts1))


@app.route('/post/<int:post_id>')
@login_required
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)





# ------------------------------------------------------
# ekleme kodu ------------------------------------------
@app.route('/add')
@login_required
def add():
    return render_template('add.html')


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
    return render_template('ilansil.html')


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
    return render_template('update.html')


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
def adminboard():
    # veritabanidaki kullancilari listeliyor
    users= User.query.all()
    admins = Admin.query.all()
    #burda name degiskeni html kodu icinde tanimlanan degeri alip oraya atiyor
    #users veritanindan alip o sayfaya atiyor
    return render_template("adminboard.html", admins=admins,users=users ,name =current_user.username)

# -------------------------------------------------------------

@app.route('/adminlog',methods=['GET','POST'])
def adminlog():

    form=LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin:
            if check_password_hash(admin.password, form.password.data):
                login_user(admin, remember=form.remember.data)
                return redirect(url_for('adminboard'))

        return '<h2>Invalid username or password </h2>'
    return render_template('adminLogin.html',form=form)


#register admin -----
@app.route('/adminsignup' ,methods=['GET','POST'])
def adminsignup():
    form= RegisterForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        yeni_kullanci=Admin(username=form.username.data,email=form.email.data,password=hashed_password)
        db.session.add(yeni_kullanci)
        db.session.commit()
        #eger olustu ise login sayfasina yonla beni
        return '''   <div class="alert alert-primary" role="alert">
    <strong>Well done!</strong> You successfully read this
    important alert message.</div></br>
    <a href="adminboard" class="btn btn-primary btn-lg" role="button" aria-pressed="true">back to dashboard</a>
</div>'''

    return render_template('adminsignup.html',form=form)


if __name__ == '__main__':
    app.run(debug=True)
