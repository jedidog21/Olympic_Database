import os

import psycopg
from dotenv import load_dotenv
from flask import Flask, request
from flask_login import (LoginManager, UserMixin, current_user,
                         login_required, login_user, logout_user)
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
import requests
import logging

load_dotenv()
conn_str = os.environ["DATABASE_URL"]

app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

login_manager = LoginManager()
login_manager.init_app(app)


logging.basicConfig(
    filename="./Olympic_Database/app.log",
    level=logging.WARNING,
    format="%(asctime)s %(levelname)s %(message)s",
)

logging.info("Server start")

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
                cur.execute(f"SELECT Name FROM Athletes WHERE Name = %s", (name, ))
            elif (column == "Team"):
                cur.execute(f"SELECT Team FROM Events WHERE Team = %s'", (name, ))
            if (column == "NOC"):
                cur.execute(f"SELECT NOC FROM Events WHERE NOC = %s", (name, ))
            if (cur.fetchone() == None):
                return False
            return True

@app.route("/api/get_team/<string:name>")
#@login_required
def get_team(name):
    try:
        if (not check_in_database("Team", name)):
            logging.exception(f"Failed to find name with the name {name}")
            return {"error": "Could not load data"}, 500
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT DISTINCT e.Team, e.NOC FROM Events e LEFT JOIN Athletes a ON a.ID = e.ID WHERE a.Name = %s", (name, ));

                data = cur.fetchall()
                
                team = {"Info":{"Team": data[0][0], "NOC": data[0][1]}}

                return(team)
    except Exception:
        logging.exception(f"Failed to find name with the name {name}")
        return {"error": "Could not load data"}, 500

@app.route("/api/get_athletes/<string:column>/<string:name>")
#@login_required
def get_athletes(column, name):
    try:
        if (not check_in_database(column, name)):
            logging.exception(f"Failed to find name with the name {name}")
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(f"Select Athletes.ID, Name, Sex, Age, Height, Weight FROM Athletes LEFT JOIN Events e ON e.ID = Athletes.ID WHERE e.{column} = %s GROUP BY Athletes.ID, Name, Sex, Age, Height, Weight ORDER BY Athletes.ID", (name, ));

                data = cur.fetchall()

                id = data[0][0]

                athletes = {'Athletes':{
                                id:{
                                    'ID':0,
                                    'Name':"",
                                    'Gender':"",
                                    'Age':0,
                                    'Height':0.0,
                                    'Weight':0.0
                                    }
                                }
                            }
                a = athletes['Athletes']

                for row in data:
                    id = row[0]
                    a.update({id:{'ID': row[0]}})
                    a[id].update({'Name': row[1]})
                    a[id].update({'Gender': row[2]})
                    a[id].update({'Age': row[3]})
                    a[id].update({'Height': row[4]})
                    a[id].update({'Weight': row[5]})

                athletes['Athletes'] = a

                return(athletes)
    except Exception:
        logging.exception(f"Failed to find name with the name {name}")
        return {"error": "Could not load data"}, 500



@app.route("/api/participate/<string:column>/<string:name>")
#@login_required
def get_games(column,name):
    try:
        if (not check_in_database(column, name)):
            logging.exception(f"Failed to find column with the name {name}")
            return {"error": "Could not load data"}, 500
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
                        "Info":{
                            "Games":[row[0] for row in data],
                            "Sports":[row[1] for row in data],
                            "Events":[row[2] for row in data]
                            }
                        }

                i = games['Info']
                
                for row in data:
                    i['Games'].append(row[0])
                    i['Sports'].append(row[1])
                    i['Events'].append(row[2])

                games['Info'] = i

                return(games)
    except Exception:
        logging.exception(f"Failed to find column with the name {column}")
        return {"error": "Could not load data"}, 500

@app.route("/api/medals/<string:column>/<string:name>")
#@login_required
def get_medals(column,name):
    try:
        if (not check_in_database(column, name)):
            logging.exception(f"Failed to find column with the name {name}")
            return {"error": "Could not load data"}, 500
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                if (column in ["Name"]):
                    if (not check_in_database(name)):
                        return ("Nobody with that name in database")
                    cur.execute(f"SELECT Games, Medal, City FROM Events e LEFT JOIN Athletes a on a.ID = e.ID WHERE {column} = %s AND e.Medal != 'NA'", (name, ))
                elif (column in ["NOC", "Team"]):
                    cur.execute(f"SELECT DISTINCT Games, Medal, Event FROM Events WHERE {column} = %s;", (name, ))

                else:
                    return (f"No column named {column}")

                data = cur.fetchall()

                medal = {
                    'Info':{
                        'Medals':{
                            'Gold':0,
                            'Silver':0,
                            'Bronze':0,
                            'NA':0,
                            'Total Medals':0
                            },
                        }
                    }

                i = medal['Info']
                
                for row in data:
                    if (row[1] == 'Gold'):
                        i['Medals']['Gold'] += 1
                    elif (row[1] == 'Silver'):
                        i['Medals']['Silver'] += 1
                    if (row[1] == 'Bronze'):
                        i['Medals']['Bronze'] += 1
                    if (row[1] == 'NA'):
                        i['Medals']['NA'] += 1

            
                i['Medals']['Total Medals'] = i['Medals']['Gold'] + i['Medals']['Silver'] + i['Medals']['Bronze']

                medal['Info'] = i

                return(medal)
    except Exception:
        logging.exception(f"Failed to find column with the name {column}")
        return {"error": "Could not load data"}, 500

@app.route("/api/athlete_info/<string:name>")
#@login_required
def get_info(name):
    try:
        if (not check_in_database("Name", name)):
            logging.exception(f"Failed to find column with the name {name}")
            return {"error": "Could not load data"}, 500
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                cur.execute(f"SELECT e.Event, a.Sex, a.Age, a.Height, a.Weight, e.Team, e.Games, e.Sport, e.Medal FROM Athletes a LEFT JOIN Events e ON a.ID = e.ID WHERE a.Name = %s;", (name, ))

                data = cur.fetchall()

                info = {'Info':{
                            'Events':[],
                            'Gender':data[0][1],
                            'Age':data[0][2],
                            'Height':data[0][3],
                            'Weight':data[0][4],
                            'Team':data[0][5],
                            'Games':[],
                            'Sports':[],
                            'Medals':{
                                'Gold':0,
                                'Silver':0,
                                'Bronze':0,
                                'NA':0,
                                'Total Medals':0
                                }
                            }
                        }

                i = info['Info']
                
                for row in data:
                    i['Events'].append(row[0])
                    i['Games'].append(row[6])
                    i['Sports'].append(row[7])
                    if (row[8] == 'Gold'):
                        i['Medals']['Gold'] += 1
                    elif (row[8] == 'Silver'):
                        i['Medals']['Silver'] += 1
                    if (row[8] == 'Bronze'):
                        i['Medals']['Bronze'] += 1
                    if (row[8] == 'NA'):
                        i['Medals']['NA'] += 1

                
                i['Games'] = list(set(i['Games']))
                i['Sports'] = list(set(i['Sports']))
                i['Events'] = list(set(i['Events']))
                i['Medals']['Total Medals'] = i['Medals']['Gold'] + i['Medals']['Silver'] + i['Medals']['Bronze']

                info['Info'] = i

                return(info)
    except Exception:
        logging.exception(f"Failed to find name with the name {name}")
        return {"error": "Could not load data"}, 500
        
@app.route("/api/team_info/<string:column>/<string:name>")
#@login_required
def get_team_info(column, name):
    try:
        if (not check_in_database(column, name)):
            logging.exception(f"Failed to find column with the name {name}")
            return {"error": "Could not load data"}, 500
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                if (column in ['Team', 'NOC']):
                    cur.execute(f"SELECT NOC, Games, Sport, Event, Medal, Team, a.ID, AVG(a.Age) OVER() FROM Events LEFT JOIN Athletes a ON a.ID = Events.id WHERE {column} = %s;", (name, ))

                data = cur.fetchall()

                info = {'Info':{
                            'NOC':data[0][0],
                            'Games':[],
                            'Sports':[],
                            'Events':[],
                            'Medals':{
                                'Gold':0,
                                'Silver':0,
                                'Bronze':0,
                                'NA':0,
                                'Total Medals':0
                                },
                            'Team':data[0][5],
                            'Number of Athletes':[],
                            'Average Age (All Time)':float(round(data[0][7],2))
                            }
                        }

                i = info['Info']
                
                for row in data:
                    i['Games'].append(row[1])
                    i['Sports'].append(row[2])
                    i['Events'].append(row[3])
                    if (row[4] == 'Gold'):
                        i['Medals']['Gold'] += 1
                    elif (row[4] == 'Silver'):
                        i['Medals']['Silver'] += 1
                    if (row[4] == 'Bronze'):
                        i['Medals']['Bronze'] += 1
                    if (row[4] == 'NA'):
                        i['Medals']['NA'] += 1
                    i['Number of Athletes'].append(row[6])

                
                i['Games'] = list(set(info['Info']['Games']))
                i['Sports'] = list(set(info['Info']['Sports']))
                i['Events'] = list(set(info['Info']['Events']))
                i['Medals']['Total Medals'] = i['Medals']['Gold'] + i['Medals']['Silver'] + i['Medals']['Bronze']
                i['Number of Athletes'] = len(set(info['Info']['Number of Athletes']))

                info['Info'] = i
                
                return(info)
    except Exception:
        logging.exception(f"Failed to find column with the name {column}")
        return {"error": "Could not load data"}, 500


@app.after_request
def log_request(response):
    user = current_user.id if current_user.is_authenticated else "anonymous"
    logging.info("%s %s -> %s (user: %s)",
                 request.method, request.path, response.status_code, user)
    return response

@app.errorhandler(500)
def server_error(e):
    logging.exception("Unhandled server error")
    return {"error": "Something went wrong on our end"}, 500



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
    app.run(debug=False, host='0.0.0.0', port=5000)
