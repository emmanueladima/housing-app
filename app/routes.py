from flask import Blueprint, render_template, redirect, request, url_for, current_app, flash
import os
from werkzeug.utils import secure_filename
from .models import Listing, User
from . import db
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html', title='Home')

@main.route('/browse')
def browse():
    page = request.args.get('page', 1, type=int)
    per_page = 6  # number of listings per page

    listings = Listing.query

    location = request.args.get('location')
    min_rent = request.args.get('min_rent', type=int)
    max_rent = request.args.get('max_rent', type=int)
    tag = request.args.get('tag')

    if location:
        listings = listings.filter(Listing.location.ilike(f'%{location}%'))
    if min_rent is not None:
        listings = listings.filter(Listing.rent >= min_rent)
    if max_rent is not None:
        listings = listings.filter(Listing.rent <= max_rent)
    if tag:
        listings = listings.filter(Listing.tags.ilike(f'%{tag}%'))

    listings = listings.order_by(Listing.id.desc()).paginate(page=page, per_page=per_page)

    return render_template('browse.html', title='Browse Listings', listings=listings)

@main.route('/post', methods=['GET', 'POST'])
def post():
    if request.method == 'POST':
        title = request.form['title']
        rent = int(request.form['rent'])
        location = request.form['location']
        tags = request.form['tags']
        user_id = current_user.id

        tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]

        image = request.files['image']
        image_filename = None

        if image and image.filename != '':
            filename = secure_filename(image.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(upload_path)
            image_filename = filename

        new_listing = Listing(
            title=title,
            rent=int(rent),
            location=location,
            tags=','.join(tag_list),
            image=image_filename,
            user_id=user_id
            )
        db.session.add(new_listing)
        db.session.commit()
        flash("🎉 Listing posted! View it in your dashboard.", "success")

        return redirect(url_for('main.browse'))
    return render_template('post.html', title='Post a Listing')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.dashboard'))
        else:
            return "Invalid credentials"
    return render_template('login.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/about')
def about():
    return render_template('about.html', title='About')

@main.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    listings = Listing.query.filter_by(user_id=current_user.id)\
                .order_by(Listing.id.desc())\
                .paginate(page=page, per_page=6)
    return render_template('dashboard.html', listings=listings)

@main.route('/delete/<int:listing_id>', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    # Make sure the logged-in user owns the listing
    if listing.user_id != current_user.id:
        flash("You are not authorized to delete this listing.", "error")
        return redirect(url_for('main.dashboard'))

    db.session.delete(listing)
    db.session.commit()
    flash("Listing deleted successfully.", "success")
    return redirect(url_for('main.dashboard'))

from flask_login import login_required, current_user

@main.route('/edit/<int:listing_id>', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    # Make sure the logged-in user owns the listing
    if listing.user_id != current_user.id:
        return "Unauthorized", 403

    if request.method == 'POST':
        listing.title = request.form['title']
        listing.rent = int(request.form['rent'])
        listing.location = request.form['location']
        listing.tags = request.form['tags']

        # Handle optional image update
        image = request.files.get('image')
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(upload_path)
            listing.image = filename

        db.session.commit()
        flash('Listing updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('edit_listing.html', listing=listing)

@main.route('/favorite/<int:listing_id>', methods=['POST'])
@login_required
def favorite(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if not current_user.favorites.filter_by(id=listing.id).first():
        current_user.favorites.append(listing)
        db.session.commit()
        flash('Added to favorites!', 'success')
    else:
        flash('Already in favorites.', 'info')

    return redirect(request.referrer or url_for('main.browse'))

@main.route('/unfavorite/<int:listing_id>', methods=['POST'])
@login_required
def unfavorite(listing_id):
    listing = Listing.query.get_or_404(listing_id)

    if current_user.favorites.filter_by(id=listing.id).first():
        current_user.favorites.remove(listing)
        db.session.commit()
        flash('Removed from favorites.', 'info')

    return redirect(request.referrer or url_for('main.browse'))

@main.route('/favorite', methods=['GET'])
@login_required
def favorites_page():
    listings = current_user.favorites.all()
    return render_template('favorite.html', listings=listings)

@main.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    return render_template('listing_detail.html', listing=listing)