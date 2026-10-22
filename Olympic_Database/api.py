import os

import psycopg
from dotenv import load_dotenv
from flask import Flask, request
from flask_login import (LoginManager, UserMixin, current_user,
                         login_required, login_user, logout_user)
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import requests

load_dotenv()
conn_str = os.environ["DATABASE_URL"]

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role


@login_manager.user_loader
def load_user(user_id):
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, username, role FROM app_user WHERE user_id = %s",
                (int(user_id),),
            )
            row = cur.fetchone()
    if row is None:
        return None
    return User(row[0], row[1], row[2])


@login_manager.unauthorized_handler
def unauthorized():
    return {"error": "You must log in first"}, 401


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return {"error": "username and password are required"}, 400

    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT user_id, username, role, password_hash FROM app_user WHERE username = %s",
                (data["username"],),
            )
            row = cur.fetchone()


    if row is None or not check_password_hash(str(row[3]), str(data["password"])):
        return {"error": f"Wrong username or password, {row[3], data["password"]}"}, 401

    login_user(User(row[0], row[1], row[2]))
    return {"message": f"Logged in as {row[1]}", "role": row[2]}


@app.route("/api/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return {"message": "Logged out"}










def check_in_database(column, name):
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            if (column == "Name"):
                cur.execute(f"SELECT Name FROM Athletes WHERE Name = %s", (name))
            elif (column == "Team"):
                cur.execute(f"SELECT Team FROM Events WHERE Team = %s'", (name))
            if (column == "NOC"):
                cur.execute(f"SELECT NOC FROM Events WHERE NOC = %s", (name))
            if (cur.fetchone() == None):
                return False
            return True

@app.route("/api/<string:column>/<string:name>")
@login_required
def get_team(column,name):
    if (not check_in_database(column, name)):
        return ("Nobody with that name in database")
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            if (column in ["NOC","Team"]):
                name = " ".join(name.split("_"))
                cur.execute(f"SELECT DISTINCT e.{column} FROM Events e LEFT JOIN Athletes a ON a.ID = e.ID WHERE a.Name = %s", (name, ));
            
            else:
                return (f"No column named {column}")
            c = {"Info":{column: cur.fetchone()[0]}}
            return(c)

@app.route("/api/participate/<string:column>/<string:name>")
@login_required
def get_games(column,name):
    if (not check_in_database(column, name)):
        return ("Nobody with that name in database")
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            if (column in ["Name"]):
                cur.execute(f"SELECT DISTINCT e.Games, e.Sport, e.Event FROM Events e LEFT JOIN Athletes a on a.ID = e.ID WHERE {column} = %s", (name, ));
            elif (column in ["NOC", "Team"]):
                cur.execute(f"SELECT DISTINCT Games, Sport, Event FROM Events WHERE {column} = %s;", (name, ))

            else:
                return (f"No column named {column}")

            data = cur.fetchall()

            games = {
                    "Games":{
                        "Years":[row[0] for row in data],
                        "Sports":[row[1] for row in data],
                        "Event":[row[2] for row in data]
                        }
                    }
            return(games)

@app.route("/api/medals/<string:column>/<string:name>")
@login_required
def get_medals(column,name):
    if (not check_in_database(column, name)):
        return ("Nobody with that name in database")
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            if (column in ["Name"]):
                if (not check_in_database(name)):
                    return ("Nobody with that name in database")
                cur.execute(f"SELECT Games, Medal, City FROM Events e LEFT JOIN Athletes a on a.ID = e.ID WHERE {column} = %s AND e.Medal != 'NA'", (name, ))
            elif (column in ["NOC", "Team"]):
                cur.execute(f"SELECT DISTINCT ON (Games, Sport, Event) Games, Medal, City, Sport FROM Events WHERE {column} = %s AND Medal != 'NA'", (name, ))

            else:
                return (f"No column named {column}")

            data = cur.fetchall()

            medal = {
                'Info':{
                    'Medals':{
                        'Gold':len([row[1] for row in data if row[1] == 'Gold']),
                        'Silver':len([row[1] for row in data if row[1] == 'Silver']),
                        'Bronze':len([row[1] for row in data if row[1] == 'Bronze'])
                        },
                    }
                }

            return(medal)

@app.route("/api/athlete_info/<string:name>")
@login_required
def get_info(name):
    if (not check_in_database(name)):
        return ("Nobody with that name in database")
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(f"SELECT DISTINCT e.Event, a.Sex, a.Age, a.Height, a.Weight, e.Team, e.Games, e.Sport, e.Medal FROM Athletes a LEFT JOIN Events e ON a.ID = e.ID WHERE a.Name = %s;", (name))

            data = cur.fetchall()

            info = {'Info':{
                        'Events':list(set([row[0] for row in data])),
                        'Gender':data[0][1],
                        'Age':data[0][2],
                        'Height':data[0][3],
                        'Weight':data[0][4],
                        'Team':data[0][5],
                        'Games':list(set([row[6] for row in data])),
                        'Sport':list(set([row[7] for row in data])),
                        'Medals':{
                            'Gold':len([row[8] for row in data if row[8] == 'Gold']),
                            'Silver':len([row[8] for row in data if row[8] == 'Silver']),
                            'Bronze':len([row[8] for row in data if row[8] == 'Bronze']),
                            'NA':len([row[8] for row in data if row[8] == 'NA'])
                            }
                        }
                    }

            return(info)
        
@app.route("/api/team_info/<string:column>/<string:name>")
@login_required
def get_team_info(column, name):
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            if (column in ['Team', 'NOC']):
                cur.execute(f"SELECT NOC, Games, Sport, Event, Medal, Team FROM Events WHERE {column} = %s;", (name, ))

            data = cur.fetchall()

            info = {'Info':{
                        'NOC':data[0][0],
                        'Games':list(set([row[1] for row in data])),
                        'Sport':list(set([row[2] for row in data])),
                        'Events':list(set([row[3] for row in data])),
                        'Medals':{
                            'Gold':len([row[4] for row in data if row[4] == 'Gold']),
                            'Silver':len([row[4] for row in data if row[4] == 'Silver']),
                            'Bronze':len([row[4] for row in data if row[4] == 'Bronze']),
                            'NA':len([row[4] for row in data if row[4] == 'NA'])
                            },
                        'Team':data[0][5]
                        }
                    }
            
            return(info)


@app.route("/api/signup", methods = ["POST"])
def sign_up():
    data = requests.get_json()
    if not data or "username" not in data or "password" not in data:
        return {"error": "username and password are required"}, 400

    username, password = data['username'], data['password']
    
    with psycopg.connect(conn_str) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO app_user (username, password_hash, role) VALUES (%s, %s, %s)",
                (username, generate_password_hash(password), 'viewer'),
            )

    print(f"Added {data['role']} {data['username']}")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)