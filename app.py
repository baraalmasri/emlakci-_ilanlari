from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# veritabani ile baglanma kodu
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
db = SQLAlchemy(app)


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


# okuma kodu --------------------------------------------
@app.route('/')
def index():
    posts1 = Blogpost.query \
        .order_by(Blogpost.date_posted.desc()).all()

    return render_template('index.html', posts=(posts1))


@app.route('/post/<int:post_id>')
def post(post_id):
    post = Blogpost.query.filter_by(id=post_id).one()

    return render_template('post.html', post=post)


# ------------------------------------------------------
# ekleme kodu ------------------------------------------
@app.route('/add')
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

    return redirect(url_for('index'))


# -----------------------------------------------------
# silme kodu ------------------------------------------
@app.route('/delete')
def delete():
    return render_template('ilansil.html')


@app.route('/deletepost', methods=['POST'])
def deletepost():
    ilan_no = request.form['id']

    ev_sil = db.session.query(Blogpost) \
        .filter(Blogpost.id == ilan_no).first()
    db.session.delete(ev_sil)
    db.session.commit()

    return redirect(url_for('index'))


# -----------------------------------------------------
# güncelleme kodu ----------------------------------------
@app.route('/update')
def update():
    return render_template('update.html')


@app.route('/updatepost', methods=['POST'])
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

    return redirect(url_for('index'))


# -------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True)
