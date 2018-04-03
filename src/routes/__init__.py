'''Routes'''

import calendar
from functools import wraps
from flask import jsonify, render_template, request, redirect, url_for, flash, session
from sqlalchemy import text
from core_app import app, db
from models import Happiness, User, Login

def get_friends(user_id):
    friend_id_list = set()
    sql_query = 'select friend_id, user_id from friends where friend_id = :user_id or user_id = :user_id'
    for item in db.engine.execute(sql_query, user_id=user_id):
        if user_id != item.friend_id:
            friend_id_list.add(item.friend_id)
        if user_id != item.user_id:
            friend_id_list.add(item.user_id)

    return User.query.filter(User.id.in_(friend_id_list)).all()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('logged_in') is None:
            flash('Login first!')
            return redirect(url_for('login_route', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/init')
def init():
    db.create_all()
    return jsonify({'message': 'DB Created'})


@app.route('/register', methods=['POST', 'GET'])
def register_route():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        user = User(name=username, email=email)
        db.session.add(user)
        db.session.commit()
        login = Login(user_id=user.id, password=password)
        db.session.add(login)
        db.session.commit()
        flash('User created')
        return redirect(url_for('login_route'))
    return render_template('register.html', hide_logout=True)

@app.route('/api/friend', methods=['POST'])
def api_add_friend():
    '''Toggle friends'''

    user_id = session.get('user_id')
    friend_id = request.get_json(silent=True).get('friendId')

    user = User.query.get(user_id)
    friend = User.query.get(friend_id)

    #import pdb; pdb.set_trace()
    if friend in user.friends:
        user.friends.remove(friend)
        message = 'Unfriended'
    elif friend in user.users:
        user.users.remove(friend)
        message = 'Unfriended'
    else:
        message = 'Friend added'
        user.friends.append(friend)
    db.session.commit()

    return jsonify({'message': message}), 200

@app.route('/delete')
def delete_all():
    db.drop_all()
    return jsonify({'message': 'DB Deleted!'})

@app.route('/query', methods=['post'])
def query_users_by_name():
    '''
    Queries the user table and gets a single user based on the user input.
    Expected input data type: json
    Expected input data structure:
    {
        "name": <userinput>
    }
    '''

    # user json input
    name = request.get_json(silent=True).get('name')

    # sql query with user input
    sql_query = "SELECT id, name, email FROM user WHERE name = :name;"

    # logs the sql query for debuging
    app.logger.info(sql_query)

    # raw results from database
    raw_results = db.engine.execute(sql_query, name=name)

    # re-format the raw_results to proper json output format
    output = [
        {
            'id': item.id,
            'name': item.name,
            'email': item.email
        } for item in raw_results
    ]

    # renders the output as json
    return jsonify({'data': output})

@app.route('/')
@login_required
def index_route():
    user_id = session.get('user_id')
    name = session.get('name')
    all_users = User.query.filter(User.id != user_id).all()

    friend_list = [friend.id for friend in get_friends(user_id)]
    return render_template('index.html', name=name, data=all_users, friend_list=friend_list)

@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(name=username).first()
        #if username == 'sami' and password == 'sami':
        if user and user.check_pw(password):
            flash('You logged in!')
            session['logged_in'] = True
            session['user_id'] = user.id
            session['name'] = user.name
            return redirect(url_for('index_route'))
        else:
            flash('Invalid credentials')

    return render_template('login.html', hide_logout=True)

@app.route('/logout', methods=['GET'])
@login_required
def logout_route():
    session.clear()
    flash('You logged out!')
    return redirect(url_for('login_route'))

@app.route('/api/happiness/all')
def api_get_happiness():
    data = Happiness.query.all()
    if not data:
        return jsonify({'message': 'No data'})
    return jsonify([item.as_dict() for item in data])

@app.route('/api/friends')
def api_get_friends():
    user_id = session.get('user_id')
    friends = [friend.as_dict() for friend in get_friends(user_id)]
    return jsonify(friends)

@app.route('/api/happiness')
def api_get_happiness_for_user():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    c_user = User.query.get(user_id)
    friends = get_friends(user_id)
    output = []
    for user in [user, *friends]:
        obj = {
            'name': user.name,
            'data': []
        }
        for datapoint in user.happiness:
            unixtime = calendar.timegm(datapoint.date_time.date().timetuple())
            obj['data'].append([int(unixtime)*1000, datapoint.happiness])
        output.append(obj)

    return jsonify(output)

@app.route('/api/happiness', methods=['POST'])
def api_post_happiness():
    req = request.get_json(silent=True)
    data = {
        'user_id': session.get('user_id'),
        'happiness': req.get('happiness'),
        'description': req.get('description')
    }
    app.logger.info(data)
    data_point = Happiness(**data)
    db.session.add(data_point)
    db.session.commit()
    return jsonify(data_point.as_dict()), 201

@app.route('/api/users')
def api_get_users():
    data = User.query.all()
    if not data:
        return jsonify({'message': 'No data'})
    return jsonify([item.as_dict() for item in data])

@app.route('/api/users', methods=['POST'])
def api_post_user():
    user = User(**request.get_json(silent=True))
    db.session.add(user)
    db.session.commit()
    return jsonify(user.as_dict()), 201

@app.errorhandler(500)
def internal_error(error):
    return str(error)
