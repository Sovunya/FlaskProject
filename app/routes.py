from datetime import datetime
from flask_mail import Mail, Message
from flask import render_template, flash, redirect, url_for, request, current_app, redirect
from flask_login import login_user, logout_user, current_user, login_required
from flask_mail import Message
from app import db, login_manager, app
from app.models import User, Feedback, Tour, CartItem
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ChangePasswordForm, ContactForm, FeedbackForm, TourForm, SearchForm, AddToCartForm
from werkzeug.utils import secure_filename
import os

mail = Mail(app)

current_year = datetime.now().year

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', current_year=current_year)

@app.route('/about')
def about():
    return render_template('about.html', title='About Us', current_year=current_year)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        # Отправка почты
        msg = Message('Обратная связь - EventHub', sender=app.config['MAIL_USERNAME'], recipients=[form.email.data])
        msg.body = f'Имя: {form.name.data}\nEmail: {form.email.data}\nСообщение: {form.message.data}'
        mail.send(msg)
        
        flash('Ваше сообщение отправлено успешно!', 'info')
        return redirect(url_for('contact'))
    return render_template('contact.html', title='Contact Us', form=form, current_year=current_year)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неверное имя пользователя или пароль', 'error')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        flash('Вход выполнен успешно!', 'info')
        return redirect(url_for('index'))
    return render_template('login.html', title='Вход в аккаунт', form=form, current_year=current_year)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Поздравляем, вы зарегистрированы!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form, current_year=current_year)

@app.route('/user')
@login_required
def user():
    return render_template('user.html', title='Личный кабинет', user=current_user, current_year=current_year)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Информация о профиле обновлена!', 'info')
        return redirect(url_for('user'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Редактировать профиль', form=form, current_year=current_year)

@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash('Пароль изменен!', 'info')
            return redirect(url_for('user'))
        else:
            flash('Неверный текущий пароль', 'error')
    return render_template('change_password.html', title='Изменить пароль', form=form, current_year=current_year)

@app.route('/catalog', methods=['GET', 'POST'])
def catalog():
    form = SearchForm()
    results = []

    search_term = request.args.get('search', '')  # Получаем параметр search из запроса
    if search_term:
        # Выполняем поиск только если search_term не пустой
        results = Tour.query.filter(Tour.title.contains(search_term)).all()
        print(f"Search term: {search_term}")
        print(f"Results: {results}")

    tours = Tour.query.all()

    return render_template('catalog.html', form=form, tours=tours, results=results)

@app.route('/tour/<tour_id>', methods=['GET', 'POST'])
def tour(tour_id):
    tour = Tour.query.get(tour_id)
    form = AddToCartForm()

    if form.validate_on_submit():
        # Обработка отправки формы
        if current_user.is_authenticated:
            cart_item = CartItem(user_id=current_user.id, tour_id=tour.id)
            db.session.add(cart_item)
            db.session.commit()
            flash('Tour added to your cart!', 'success')
            return redirect(url_for('catalog'))
        else:
            flash('You need to log in to add tours to your cart.', 'warning')
            return redirect(url_for('login'))

    return render_template('tour.html', tour=tour, form=form)

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    tours = [Tour.query.get(item.tour_id) for item in cart_items]  # используйте tour_id

    total_price = sum([item.price for item in tours])

    return render_template('cart.html', tours=tours, total_price=total_price)

@app.route('/add_to_cart/<int:tour_id>', methods=['POST'])
@login_required
def add_to_cart(tour_id):
    tour = Tour.query.get(tour_id)
    if current_user.is_authenticated:
        current_user.add_to_cart(tour)
        db.session.commit()  # Затем добавляем тур в корзину и снова коммитим
        flash('Тур добавлен в корзину.')
        return redirect(url_for('tour', tour_id=tour_id))
    else:
        flash('You need to log in to add tours to your cart.', 'warning')
        return redirect(url_for('login'))

@app.route('/add_tour', methods=['GET', 'POST'])
def add_tour():
    form = TourForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        price = form.price.data
        image = form.image.data  # Получение файла из формы

        # Сохранение файла на сервере
        filename = secure_filename(image.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        image.save(filepath)

        # Сохранение информации о туре в базе данных
        tour = Tour(title=title, description=description, price=price, image=filename)
        db.session.add(tour)
        db.session.commit()

        flash('Tour added successfully!', 'success')
        return redirect(url_for('index'))

    print(form.errors)

    return render_template('add_tour.html', title='Add Tour', form=form)

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    user = current_user
    cart_items = user.cart_items

    if not cart_items:
        flash('Корзина пуста. Добавьте туры перед оформлением заказа.', 'warning')
        return redirect(url_for('cart'))

    # Подготовка чека для пользователя
    user_email = user.email
    subject_user = 'Ваш заказ на TravelBoard'
    body_user = f'Спасибо за заказ!\n\nВаши туры:\n'
    total_price = 0

    for cart_item in cart_items:
        tour = Tour.query.get(cart_item.tour_id)
        body_user += f'{tour.title} - ${tour.price}\n'
        total_price += tour.price

    body_user += f'\nОбщая стоимость: ${total_price}'
    msg = Message('Обратная связь - EventHub', sender=app.config['MAIL_USERNAME'], recipients=[user_email])
    msg.body = body_user
    mail.send(msg)

    # Подготовка уведомления для администратора
    admin_email = 'senior.nikita1@yandex.ru'
    subject_admin = 'Оформлен заказ на TravelBoard'
    body_admin = f'Поступил новый заказ!\n\nТуры:\n'

    for cart_item in cart_items:
        tour = Tour.query.get(cart_item.tour_id)
        body_admin += f'{tour.title} - ${tour.price}\n'

    body_admin += f'\nОбщая стоимость: ${total_price}\n\nКонтакты заказавшего:\n'
    body_admin += f'Имя: {user.username}\nEmail: {user.email}'

    msg = Message('Обратная связь - EventHub', sender=app.config['MAIL_USERNAME'], recipients=[admin_email])
    msg.body = body_admin
    mail.send(msg)
    # Очистка корзины пользователя
    for cart_item in cart_items:
        db.session.delete(cart_item)

    db.session.commit()

    flash('Заказ успешно оформлен. Подтверждение отправлено на вашу почту.', 'success')
    return redirect(url_for('index'))
