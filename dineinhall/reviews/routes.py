from flask import render_template, Blueprint, redirect, url_for, flash
from sqlalchemy import create_engine
from datetime import datetime
from pytz import timezone
from dineinhall.models import Rating
from flask_login import current_user, login_required
from .forms import ReviewForm
from dineinhall import db
import os
try:
    SQLALCHEMY_DATABASE_URI = os.environ["SQLALCHEMY_DATABASE_URI"]  # URI from Heroku
except Exception:
    from ..creds import SQLALCHEMY_DATABASE_URI  # local URI

review = Blueprint('review', __name__)

engine = create_engine(SQLALCHEMY_DATABASE_URI)


@review.route("/newReview/<food_id>", methods=['GET', 'POST'])
@login_required
def newReview(food_id):
    form = ReviewForm()
    if form.validate_on_submit():
        user_id = current_user.user_id
        stars = form.stars.data
        description = form.description.data.strip()
        description = description if description else None
        timestamp = datetime.now(timezone('US/Eastern'))  # EST timezone
        timestamp = timestamp.strftime("%Y-%m-%d %H:%M:%S")
        rating = Rating(user_id=user_id, food_id=food_id, stars=stars, description=description, timestamp=timestamp)
        try:
            db.session.add(rating)
            db.session.commit()
            flash('Succesfully reviewed', 'success')
        except Exception:
            flash('Error in submitting review', 'danger')
    return render_template('newRating.html', title='New Review', form=form)


@review.route("/reviews")
def reviews():
    return redirect(url_for('review.foodReview', food_id=-1))


@review.route("/reviews/<food_id>")
def foodReview(food_id):
    if int(food_id) == -1:
        food_id = True
    else:
        food_id = f'food_id = {food_id}'
    with engine.connect() as con:
        reviews = con.execute("select * "
                              f"from food join rating using (food_id) "
                              f"join user using (user_id) "
                              f"where not isnull(description) and {food_id} "
                              f"order by timestamp desc")
    reviews = list(reviews)
    size = len(reviews)
    if size == 0:
        flash('No reviews for this food item', 'danger')
    else:
        flash(f'Found {size} reviews!', 'success')

    return render_template('reviews.html', title='Ratings', reviews=reviews)