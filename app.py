from flask import Flask, render_template, request, redirect, url_for
from flask_login import current_user, login_user, login_required, logout_user, LoginManager
from flask_socketio import SocketIO, join_room, leave_room
from pymongo.errors import DuplicateKeyError
from mysql.connector.errors import IntegrityError
from datetime import datetime
from time import sleep
from bson.json_util import dumps
import random

from DB_sql import save_user_sql, get_user_sql, save_room_sql, update_room_sql, get_room_sql, add_room_members_sql, remove_room_members_sql, get_room_members_sql, is_room_member_sql, is_room_admin_sql,save_message_sql, delete_room_sql
from DB import get_rooms_for_user, get_messages

app = Flask(__name__)
app.secret_key = "LOLMYSECRETKEY"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)


@app.route('/')
def home():
    """
    :return: template for home page
    """
    rooms = []
    if current_user.is_authenticated:
        rooms = get_rooms_for_user(current_user.username)
    return render_template('index.html', rooms=rooms, )


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    login function
    :return template for login or home if the user is already logged in:
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user_sql(username)

        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = 'Login Failed!'
    return render_template('login.html',
                           message=message)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    signup function
    :return: template for signup or home if user is already logged in
    """
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        print(f"username={username}, password={password}, email={email}")
        if username == '' or email == '' or password == '':
            message = "All fields are required!"
            return render_template('signup.html', message=message)
        else:
            try:
                save_user_sql(username, email, password)
                print("### DONE ###")
                return render_template('login.html', message="Signup successful")
            except IntegrityError or DuplicateKeyError:
                message = "User already exists!"
    return render_template('signup.html', message=message)


@app.route("/logout/")
@login_required
def logout():
    """
    logout function
    :return: logout the user if logged in
    """
    logout_user()
    return redirect(url_for('home'))


@app.route('/create-room/', methods=['GET', 'POST'])
@login_required
def create_room():
    """
    creates a room
    :return: creates a room for the user and the people he added
    """
    message = ''
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        usernames = [username.strip() for username in request.form.get('members').split(',')]
        print(f"Room Name={room_name} Members={usernames}")
        if len(room_name) and len(usernames):
            room_id = save_room_sql(room_name, current_user.username)
            if current_user.username in usernames:
                usernames.remove(current_user.username)
            add_room_members_sql(room_id, room_name, usernames, current_user.username)
            print("### DONE ###")
            return redirect(url_for('view_room',
                                    room_id=room_id))
        else:
            message = "Failed to create room"
    return render_template('create_room.html',
                           message=message)


@app.route('/rooms/<room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    """
    edits a room for a user if he is room admin for that room
    :param room_id:
    :return: edit room
    """
    room = get_room_sql(room_id)
    if room and is_room_admin_sql(room_id, current_user.username):
        existing_room_members = [member for member in get_room_members_sql(room_id)]
        room_members_str = ",".join(existing_room_members)
        message = ''
        if request.method == 'POST':
            room_name = request.form.get('room_name')
            room['name'] = room_name
            update_room_sql(room_id, room_name)

            new_members = [username.strip() for username in request.form.get('members').split(',')]
            members_to_add = list(set(new_members) - set(existing_room_members))
            members_to_remove = list(set(existing_room_members) - set(new_members))

            if len(members_to_add):
                add_room_members_sql(room_id, room_name, members_to_add, current_user.username)

            if len(members_to_remove):
                remove_room_members_sql(room_id, members_to_remove)
            message = 'Room edited successfully'
            room_members_str = ",".join(new_members)
            return redirect(url_for('view_room', room_id=room_id))
        return render_template('edit_room.html',
                               room=room,
                               room_members_str=room_members_str,
                               message=message)
    else:
        return "Room not found", 404


@app.route('/rooms/<room_id>/')
@login_required
def view_room(room_id):
    """
    main chat room
    :param room_id:
    :return: chat room to talk
    """
    room = get_room_sql(room_id)
    if room and is_room_member_sql(room_id, current_user.username):
        room_members = get_room_members_sql(room_id)
        messages = get_messages(room_id)
        return render_template('view_room.html',
                               username=current_user.username,
                               room=room, room_members=room_members,
                               messages=messages)
    else:
        return "Room not found", 404


@app.route('/rooms/<room_id>/messages/')
@login_required
def get_older_messages(room_id):
    """
    shows the older messages for that room
    :param room_id:
    :return: old messages
    """
    room = get_room_sql(room_id)
    if room and is_room_member_sql(room_id, current_user.username):
        page = int(request.args.get('page', 0))
        messages = get_messages(room_id, page)
        return dumps(messages)
    else:
        return "Room Not Found", 404


@app.route('/room')
@login_required
def rooms():
    """
    function for showing rooms available for a user
    :return:
    """
    message = ''
    rooms = []
    if current_user.is_authenticated:
        rooms = get_rooms_for_user(current_user.username)
        if len(rooms) == 0:
            message = "No Rooms available for you (sigh TT) Maybe create one :)"
        else:
            message = "Available Rooms :"
        return render_template('rooms.html', rooms=rooms, message=message)


@app.route('/delete_room/<room_id>/')
@login_required
def remove_room(room_id):
    """
    function for for removing all the data for a room
    :param room_id:
    :return:
    """
    if current_user.is_authenticated and is_room_admin_sql(room_id, current_user.username):
        delete_room_sql(room_id)
        return redirect(url_for('home'))
    else:
        return "You Are Not A Admin for this room", 404


@app.route('/aboutus')
def about_us():
    """
    lol just an about us page
    :return:
    """
    return render_template('aboutus.html')


@socketio.on('send_message')
def handle_send_message_event(data):
    """
    handles the connection for sending messages
    :param data:
    :return: messages
    """
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    data['sent_at'] = datetime.now().strftime("%d %b0, %H:%M")
    save_message_sql(data['room'], data['message'], data['username'])
    socketio.emit('receive_message', data, room=data['room'])


@socketio.on('join_room')
def handle_join_room_event(data):
    """
    handles the event when a user joins a room
    :param data:
    :return: {user} joined the room
    """
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])


@socketio.on('leave_room')
def handle_leave_room_event(data):
    """
    handles the event when a user exits a room
    :param data:
    :return: {user} left the room
    """
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])


@login_manager.user_loader
def load_user(username):
    """
    gives the info about the user if available in the database
    :param username:
    :return: data for a specific user
    """
    return get_user_sql(username)


if __name__ == '__main__':
    socketio.run(app, debug=False)
