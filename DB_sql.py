import mysql.connector as con
from werkzeug.security import generate_password_hash
from datetime import datetime
from bson import ObjectId
from user import User
from miscfunc import create_id
from DB import *

cur = con.connect(host='localhost', user='root', password='BEST3012', database='NorCha')
mycursor = cur.cursor()
mycursor.execute("set sql_safe_updates=0")


def save_user_sql(username, email, password):
    """
    Saves the user in the database(SQL and mongoDB)
    :param username:
    :param email:
    :param password:
    :return: None
    """
    password_hash = generate_password_hash(password)
    insert = "insert into users values(%s,%s,%s)"
    values = (username, email, password_hash)
    mycursor.execute(insert, values)
    cur.commit()
    save_user(username, email, password)


def get_user_sql(username):
    """
    Gets the credentials for the specified user
    :param username:
    :return: True or None
    """
    user_data_lst = []
    values = []
    keys = ['_id', 'email', 'password']
    query = "select * from users where ID = '{}'".format(username)
    mycursor.execute(query)
    for i in mycursor:
        for j in i:
            values.append(j)
    for key, value in zip(keys, values):
        user_data_lst.append((key, value))
    user_data = dict(user_data_lst)
    return User(user_data['_id'], user_data['email'], user_data['password']) if user_data else None


def save_room_sql(room_name, created_by):
    """
    Saves the created room and the creator as Room Admin
    :param room_name:
    :param created_by:
    :return: ID (24 char hex string)
    """
    ID = create_id()
    query = "insert into rooms values('{}','{}','{}','{}' )".format(ObjectId(ID), room_name, created_by, datetime.now())
    mycursor.execute(query)
    cur.commit()
    add_room_member_sql(ID, room_name, created_by, created_by, is_room_admin=True)
    save_room(room_name, created_by, ID)
    return ID


def update_room_sql(room_id, room_name):
    """
    Changes the room name for the given room
    :param room_id:
    :param room_name:
    :return: None
    """
    query = "update rooms set Name='{}' where ID='{}'".format(room_name, room_id)
    query2 = "update room_members set Room_Name='{}' where ID='{}'".format(room_name, room_id)
    mycursor.execute(query)
    cur.commit()
    mycursor.execute(query2)
    cur.commit()
    update_room(room_id, room_name)


def get_room_sql(room_id):
    """
    Returns the Room specifications
    :param room_id:
    :return: Dictionary storing the room data
    """
    room_lst = []
    values = []
    keys = ['_id', 'name', 'created_by', 'created_at']
    query = "select * from rooms where ID='{}'".format(room_id)
    mycursor.execute(query)
    for i in mycursor:
        for j in i:
            values.append(j)
    for key, value in zip(keys, values):
        room_lst.append((key, value))
    room_dict = dict(room_lst)
    return room_dict


def add_room_member_sql(room_id, room_name, username, added_by, is_room_admin=False):
    """
    Adds a member in the specified room
    :param room_id:
    :param room_name:
    :param username:
    :param added_by:
    :param is_room_admin:
    :return: None
    """
    query = "insert into room_members values('{}','{}','{}','{}','{}','{}')".format(ObjectId(room_id), username,
                                                                                    room_name, added_by, datetime.now(),
                                                                                    is_room_admin)
    mycursor.execute(query)
    cur.commit()


def add_room_members_sql(room_id, room_name, usernames, added_by):
    """
    Adds many members into a room
    :param room_id:
    :param room_name:
    :param usernames:
    :param added_by:
    :return: None
    """
    for username in usernames:
        query = "insert into room_members values('{}','{}','{}','{}','{}','{}')".format(ObjectId(room_id), username,
                                                                                        room_name, added_by,
                                                                                        datetime.now(), 'False')
        mycursor.execute(query)
        cur.commit()
    add_room_members(room_id, room_name, usernames, added_by)


def remove_room_members_sql(room_id, usernames):
    """
    Removes a specified members from the room
    :param room_id:
    :param usernames:
    :return: None
    """
    for username in usernames:
        query = "DELETE FROM room_members WHERE ID='{}' and username='{}' ".format(
            ObjectId(room_id), username)
        mycursor.execute(query)
        cur.commit()
        remove_room_members(room_id, usernames)


def get_room_members_sql(room_id):
    """
    Get's the room members in a room
    :param room_id:
    :return: List of usernames in a room
    """
    username_lst = []
    query = "select username from room_members where ID='{}'".format(room_id)
    mycursor.execute(query)
    for i in mycursor:
        for j in i:
            username_lst.append(j)
    return username_lst


def is_room_member_sql(room_id, username):
    """
    Checks if the user specified is a room members of the specified room ot not
    :param room_id:
    :param username:
    :return: True or False
    """
    query1 = "select count(*) from room_members where ID='{}' and username='{}'".format(room_id, username)
    mycursor.execute(query1)
    for i in mycursor:
        for j in i:
            if j == 1:
                return True
            elif j == 0:
                return False


def is_room_admin_sql(room_id, username):
    """
    Checks if the specified user is an room admin for the specified room
    :param room_id:
    :param username:
    :return: True or False
    """
    query = "select count(*) from room_members where ID='{}' and username='{}' and Is_Room_Admin='true'".format(room_id,
                                                                                                                username)
    mycursor.execute(query)
    for i in mycursor:
        for j in i:
            if j == 1:
                return True
            elif j == 0:
                return False


def save_message_sql(room_id, text, sender):
    """
    Saves a message sent in a room
    :param room_id:
    :param text:
    :param sender:
    :return: None
    """
    query = "insert into messages values('{}','{}','{}','{}','{}')".format(room_id, room_id, text, sender,
                                                                           datetime.now())
    mycursor.execute(query)
    cur.commit()
    save_message(room_id, text, sender)


def delete_room_sql(room_id):
    """
    Delets all the related data to a specified room
    :param room_id:
    :return: None
    """
    query1 = "delete from room_members where ID='{}'".format(room_id)
    query2 = "delete from rooms where ID='{}'".format(room_id)
    query3 = "delete from messages where ID='{}'".format(room_id)
    mycursor.execute(query1)
    mycursor.execute(query2)
    mycursor.execute(query3)
    cur.commit()
    delete_room(room_id)
