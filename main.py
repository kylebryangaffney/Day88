from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, URL
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')
Bootstrap5(app)

# CREATE DB
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///cafes.db"
db = SQLAlchemy(app)

class Cafe(db.Model):
    __tablename__ = 'cafe'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    has_bathroom = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_outlets = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

with app.app_context():
    db.create_all()

class CafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    map_url = StringField('Location', validators=[DataRequired(), URL()])
    img_url = StringField('Image URL', validators=[DataRequired(), URL()])
    location = StringField('Neighborhood', validators=[DataRequired()])
    has_bathroom = BooleanField('Bathroom Available?')
    has_wifi = BooleanField('Does it have WiFi?')
    has_outlets = BooleanField('Are there power outlets available?')
    coffee_price = StringField('Average coffee price', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    return render_template("index.html", cafes=all_cafes)

@app.route("/add-cafe", methods=["GET", "POST"])
def add_cafe():
    add_form = CafeForm()
    if add_form.validate_on_submit():
        new_cafe = Cafe(
            name=add_form.name.data,
            map_url=add_form.map_url.data,
            img_url=add_form.img_url.data,
            location=add_form.location.data,
            has_bathroom=add_form.has_bathroom.data,
            has_wifi=add_form.has_wifi.data,
            has_outlets=add_form.has_outlets.data,
            coffee_price=add_form.coffee_price.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template('add.html', form=add_form)

@app.route("/delete")
def delete():
    cafe_id = request.args.get('id')
    cafe_to_delete = db.get_or_404(Cafe, cafe_id)
    db.session.delete(cafe_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/edit/<int:cafe_id>', methods=["GET", "POST"])
def edit_cafe(cafe_id):
    cafe = db.get_or_404(Cafe, cafe_id)
    edit_form = CafeForm(
        name=cafe.name,
        map_url=cafe.map_url,
        img_url=cafe.img_url,
        location=cafe.location,
        has_bathroom=cafe.has_bathroom,
        has_wifi=cafe.has_wifi,
        has_outlets=cafe.has_outlets,
        coffee_price=cafe.coffee_price
    )
    if edit_form.validate_on_submit():
        cafe.name = edit_form.name.data
        cafe.map_url = edit_form.map_url.data
        cafe.img_url = edit_form.img_url.data
        cafe.location = edit_form.location.data
        cafe.has_bathroom = edit_form.has_bathroom.data
        cafe.has_wifi = edit_form.has_wifi.data
        cafe.has_outlets = edit_form.has_outlets.data
        cafe.coffee_price = edit_form.coffee_price.data
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("add.html", form=edit_form, is_edit=True)

if __name__ == '__main__':
    app.run(debug=True)
