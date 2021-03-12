from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash
from user import User
from miscfunc import create_id

client = MongoClient("mongodb+srv://test:BEST3012@chat-app.pa6mb.mongodb.net/test?retryWrites=true&w=majority")

chat_db = client.get_database("Chat-AppDB")
users_collection = chat_db.get_collection("users")
rooms_collection = chat_db.get_collection("rooms")
room_members_collection = chat_db.get_collection("room_members")
messages_collection = chat_db.get_collection("messages")


def save_user(username, email, password):  # USERS
    """
    saves the data provided by the user in while signing up in the database
    :param username:
    :param email:
    :param password:
    :return: None
    """
    password_hash = generate_password_hash(password)
    users_collection.insert_one({'_id': username, 'email': email, 'password': password_hash})


def get_user(username):  # USERS
    """
    gets the user data from the database
    :param username:
    :return: user data from the database
    """
    user_data = users_collection.find_one({'_id': username})
    print(user_data)
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None


def save_room(room_name, created_by, room_id):  # ROOMS
    """
    saves the room info created by the user in the database
    :param room_name:
    :param created_by:
    :return: room_id created by the computer
    """
    rooms_collection.insert_one({'_id':ObjectId(room_id),'name': room_name, 'created_by': created_by, 'created_at': datetime.now()})
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)


def update_room(room_id, room_name):  # ROOMS
    """
    updates the info for a specific room while the user edits a room
    :param room_id:
    :param room_name:
    :return: None
    """
    rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    room_members_collection.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': room_name}})


def get_room(room_id):  # ROOMS
    """
    gets the room for a user
    :param room_id:
    :return: Room specified
    """
    return rooms_collection.find_one({'_id': ObjectId(room_id)})


def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):  # ROOM_MEMEBERS
    """
    adds a memeber in the specified room by the user in the database
    :param room_id:
    :param room_name:
    :param username:
    :param added_by:
    :param is_room_admin:
    :return: None
    """
    room_members_collection.insert_one(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
         'added_at': datetime.now(), 'is_room_admin': is_room_admin})


def add_room_members(room_id, room_name, usernames, added_by):  # ROOM_MEMEBERS
    """
    adds many members in a room specified by the user in the database
    :param room_id:
    :param room_name:
    :param usernames:
    :param added_by:
    :return: None
    """
    room_members_collection.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
          'added_at': datetime.now(), 'is_room_admin': False} for username in usernames])


def remove_room_members(room_id, usernames):  # ROOM_MEMBERS
    """
    removes a member for the specified room from the database specified by the user
    :param room_id:
    :param usernames:
    :return: None
    """
    room_members_collection.delete_many(
        {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})


def get_room_members(room_id):  # ROOM_MEMBERS
    """
    gets the room members for a room from the database
    :param room_id:
    :return: list of members in a room
    """
    return list(room_members_collection.find({'_id.room_id': ObjectId(room_id)}))


def get_rooms_for_user(username):  # ROOMS_MEMBERS                                                                      #####DONE
    """
    gets the available rooms for a specified user
    :param username:
    :return: list of rooms in which a user is in the room
    """
    return list(room_members_collection.find({'_id.username': username}))


def is_room_member(room_id, username):  # ROOM_MEMBERS
    """
    checks in the database if the user specified is in the room or not
    :param room_id:
    :param username:
    :return: rooms in which a user is in
    """
    return room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})


def is_room_admin(room_id, username):  # ROOM_MEMBERS
    """
    checks the database if the specified user in an admin for a specified room
    :param room_id:
    :param username:
    :return: checks if the user is a room admin
    """
    return room_members_collection.count_documents(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})


def save_message(room_id, text, sender):  # MESSAGES
    """
    saves the messages sent in a room to the database
    :param room_id:
    :param text:
    :param sender:
    :return: None
    """
    messages_collection.insert_one({'room_id': room_id, 'text': text, 'sender': sender, 'sent_at': datetime.now()})


max_message_fetch_limit = 3


def get_messages(room_id, page=0):  # MESSAGES
    """
    gets the most recent 3 messages for a room from the database
    :param room_id:
    :param page:
    :return: most recent 3 messages
    """
    offset = page * max_message_fetch_limit
    messages = list(
        messages_collection.find({'room_id': room_id}).sort('_id', DESCENDING).limit(max_message_fetch_limit).skip(
            offset))
    for message in messages:
        message['sent_at'] = message['sent_at'].strftime("%d %b, %H:%M")
    return messages[::-1]


def delete_room(room_id):
    """
    Delets all the room data for a given room from the database(room messages, room and room members)
    :param room_id:
    :return:
    """
    rooms_collection.delete_one({'_id': ObjectId(room_id)})
    room_members_collection.delete_many({'_id.room_id': ObjectId(room_id)})
    messages_collection.delete_many({'room_id': room_id})
