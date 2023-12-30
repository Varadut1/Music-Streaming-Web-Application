#here paths are setup

from flask import Flask, request, url_for, redirect, session
from sqlalchemy import func
from flask import render_template
from flask import current_app as app
from application.models import *
from application.database import db
from application.models import Loggers, Admin
from werkzeug.security import generate_password_hash, check_password_hash
import matplotlib.pyplot as plt
import requests, json, os
from application.validation import *
from datetime import datetime
from fuzzywuzzy import fuzz

# isLoggedIn = False
# loggedUser = None
loggedProfile = None
# link = "creator"
# User = None


error_obj = {"existing":["Your username matches with the user which exists already, Please try with some other name!", "register"],
            "unauthenticated": ["You are not authenticated user of BeatX, Please Login OR Register if you haven't!", "welcome"], 
            "incorrecta":["Incorrect username or Password for Administrator, Please try again by clicking below link!", "adminlogin"], 
            "incorrect":["Incorrect username or Password for user, Please try again by clicking below link!", "login"],
            "unregistered":["You are not registered as user, please register to start listening to your favourite songs!", "register"], 
            "unregistereda":["You are not registered as Admin, Please contact to the boards or register yourself as user below!", "register"], 
            "existingsong":["The name of the song could not be given because it already exists please try something new!", "upload"],
            "doesntexist":["This song doesnot exist in database", "track"],
            "norated":["The song with ratings provided doesnot exist", "track"], 
            "notcreator":["You are not creator, you have to be creator in order to make albums", "home"], 
            "nothing":["The searched element doesn't exists in database please try something else", "home"], 
            "norateduser":["The song with ratings provided doesnot exist", "home"]}


def set_routes(app):
    def generate_graphs():
        bestsong = [[], []]
        allsongs = db.session.query(Songs).all()
        for i in allsongs:
            com = db.session.query(Comments).filter(Comments.s_id == i.s_id).all()
            avg = 0
            total = 0
            for j in com:
                if j.rating != None:
                    avg += j.rating
                    total += 1
            if total != 0:
                avg = avg/total
                bestsong[0].append(i.name.split('.')[0])
                bestsong[1].append(avg)

        zipped_lists = zip(bestsong[0], bestsong[1])
        sorted_lists = sorted(zipped_lists)
        sorted_list2, sorted_list1 = zip(*sorted_lists)
        values = sorted_list1[:7]
        names = sorted_list2[:7]
        max_length = 30
        names = [label[:max_length] + '\n' + "" if len(label) > max_length else label for label in names]
        print(names, values)
        plt.figure(figsize=(10, 4))
        plt.bar(names, values, color='skyblue')
        plt.xticks(fontsize=7)
        plt.ylabel('Ratings')
        plt.title('Best song till date')
        file_path = "./static/best.png"
        plt.savefig(file_path)
        plt.close()
        most = db.session.query(Played).order_by(Played.plays.desc()).limit(7).all()
        name = []
        value = []
        for i in most:
            name.append(db.session.query(Songs).filter(Songs.s_id == i.s_id).one().name.split('.')[0])
            value.append(i.plays)
        
        name = [label[:max_length] + '\n' + "" if len(label) > max_length else label for label in name]
        print(name, value)
        plt.figure(figsize=(10, 4))
        plt.bar(name[:7], value[:7], color='skyblue')
        plt.xticks(fontsize=7)
        plt.ylabel('Listens')
        plt.title('Most Listened Song')
        file_path = "./static/most.png"
        plt.savefig(file_path)
        return
        
    @app.route("/", methods=["GET", "POST"])
    def welcome():
        session.clear()
        app.secret_key = app.config.get('SECRET_KEY', 'DefaultSecretKey')
        session['isLoggedIn'] = False
        session['loggedUser'] = None
        session["link"] = 'creator'
        session["profile"] = None
        return render_template("index.html")
    

    @app.route("/register", methods=["GET", "POST"])
    def register():
        session.clear()
        app.secret_key = app.config.get('SECRET_KEY', 'DefaultSecretKey')
        session['isLoggedIn'] = False
        session['loggedUser'] = None
        session["profile"] = None
        if request.method == "GET":
            data = {"log":"Register", "red":"register"}
            return render_template("login.html", data=data)
        elif request.method == "POST":
            username = request.form['name']
            password = request.form['password']
            allnames = [i.username for i in db.session.query(Loggers).all()]
            
            if username in allnames:
               return redirect(url_for("error", token="existing"))
            else:
                newlogger = Loggers(username=username, password=generate_password_hash(password),profile="user")
                db.session.add(newlogger)
                db.session.commit()
                data={"profile":"user", "name":username}
                # global isLoggedIn
                # global loggedProfile
                # global loggedUser
                # global User
                User = newlogger
                loggedUser = username
                session['loggedUser'] = username
                session["profile"] = 'user'
                loggedProfile = data["profile"]
                isLoggedIn = True
                session['isLoggedIn'] = True
                return redirect(url_for("home"))
    

    @app.route("/login", methods=["GET", "POST"])
    def login():
        session.clear()
        app.secret_key = app.config.get('SECRET_KEY', 'DefaultSecretKey')
        session['isLoggedIn'] = False
        session['loggedUser'] = None
        session["profile"] = None
        if request.method == "GET":
            data = {"log":"Login", "red":"login"}
            return render_template("login.html", data=data)
        elif request.method == "POST":
            username = request.form['name']
            password = request.form['password']
            user = db.session.query(Loggers).filter(Loggers.username==username).first()
            if user:
                check = check_password_hash(user.password, password)
                if check:
                    data={"profile":user.profile, "name":user.username}
                    # global User
                    # global isLoggedIn
                    # global loggedProfile
                    # global loggedUser
                    loggedUser = user.username
                    session['loggedUser'] = user.username
                    session["profile"] = 'user'
                    loggedProfile = user.profile
                    isLoggedIn = True
                    session['isLoggedIn'] = True
                    User = user
                    return redirect(url_for("home"))
                else: 
                    return redirect(url_for("error", token="incorrect"))
            else:
                return redirect(url_for("error", token="unregistered"))
            
            

    @app.route("/adminlogin", methods=["GET", "POST"])
    def adminlogin():
        session.clear()
        app.secret_key = app.config.get('SECRET_KEY', 'DefaultSecretKey')
        session['isLoggedIn'] = False
        session['loggedUser'] = None
        session["profile"] = None
        if request.method == "GET":
            data = {"log":"Administrator", "red":"adminlogin"}
            return render_template("login.html", data=data)
        elif request.method == "POST":
            generate_graphs()
            username = request.form['name']
            password = request.form['password']
            user = db.session.query(Admin).filter(Admin.admin_name==username).first()
            if user!=None:
                check = user.password == password
                if check:
                    data={"profile":"admin", "name":user.admin_name}
                    # global User
                    # global isLoggedIn
                    # global loggedProfile
                    # global loggedUser
                    User = user
                    loggedUser = username
                    session['loggedUser'] = username
                    loggedProfile = "Admin"
                    isLoggedIn = True
                    session['isLoggedIn'] = True
                    session["profile"] = "admin"
                    return redirect(url_for("admin"))
                else: 
                    return redirect(url_for("error", token="incorrecta"))
            else:
                return redirect(url_for("error", token="unregistereda"))
            
        
    @app.route("/home", methods=["GET","POST"])
    def home():
        if request.method == "GET":
            # global isLoggedIn
            # global User
            # global link
            if session.get('isLoggedIn') and session.get('profile')=="user":
                User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
                if User==None:
                    return redirect(url_for("error", token="unregistered"))
                print(User.username)
                has_songs = db.session.query(Songs).filter(User.l_id == Songs.l_id).all()
                if has_songs != []:
                    session['link'] = "creatorshome"
                else:
                    session["link"] = "creator"
                for i in db.session.query(Songs).all():
                    songs = db.session.query(Comments).filter(Comments.s_id == i.s_id).all()
                    avg = 0
                    total = 0
                    for j in songs:
                        if j.rating != None:
                            total += 1
                            avg += j.rating
                    if total!=0:
                        avg = avg/total
                    i.rating = str(avg)
                    db.session.add(i)
                    db.session.commit()
                list_of_recommended_songs = [song for song in db.session.query(Songs).filter(Songs.rating != '0').all()]
                playlist = db.session.query(Playlist).filter(User.l_id == Playlist.l_id).all()
                data = {"nav": "prime", "user": User, "e1":['Creator Account', session.get('link')], "e2":['Create Album', 'createalbum'], "e3":['Log Out', 'logout']}
                genre = {}
                components = {"recommended":list_of_recommended_songs, "playlist": playlist, "album": [], "genre": genre}
                list_of_albums = db.session.query(Album).all()
                for i in list_of_albums:
                    components["album"].append(i)
                print(len(components["album"]))
                genres = db.session.query(Genre).all()
                for i in genres:
                    genre[i.genrename] = []
                songs = db.session.query(Songs).all()
                for i in songs:
                    g = db.session.query(Genre).filter(Genre.g_id == i.g_id).one().genrename
                    genre[g].append(i)
                return render_template("home.html", data=data, components=components)
            else: 
                return redirect(url_for("error", token="unauthenticated"))
        elif request.method == "POST":
            if session.get('isLoggedIn') and session.get('profile')=="user":
                User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
                if "hidden" in request.form:
                    id=int(request.form["hidden"])
                    return redirect(url_for("lyrics", id=id))
                if "playlist" in request.form:
                    name = request.form["name"]
                    newplaylist = Playlist(name = name, l_id=db.session.query(Loggers).filter(Loggers.username == session.get('loggedUser')).first().l_id)
                    db.session.add(newplaylist)
                    db.session.commit()
                    id = newplaylist.p_id
                    return redirect(url_for("playlist", id=id))
                if "view" in request.form:
                    id=int(request.form["view"])
                    return redirect(url_for("playlist", id=id))
                if "albumview" in request.form:
                    id = int(request.form["albumview"])
                    return redirect(url_for("album", id=id))
                
                if "submit" in request.form:
                    value = request.form["search"]
                    print(value)

                    #implement search by rating, song name, playlist name, genre
                    #dictionary of data -> songs by rating, all songs with >70 match, playlist as total, all songs by genre as total
                    data = {"nav": "even", "value": value, "user": User, "e1":['Creator Account', session.get('link')], "e2":['Home', 'home'], "e3":['Log Out', 'logout']}
                    data["all"] = {}
                    try:
                        value = float(value)
                        print("this my value", value)
                        songs = db.session.query(Songs).all()
                        alllist = []
                        for i in songs:
                            rating = db.session.query(Comments).filter(Comments.s_id == i.s_id and Comments.rating!=None).all()
                            if rating != []:
                                avg = 0
                                total = 0
                                for j in rating:
                                    if j.rating != None:
                                        avg += j.rating
                                        total += 1
                                if total!=0:
                                    avg = avg/total
                                alllist.append([i, avg])
                        
                        data['all']['ratedaround'] = []
                        for i in alllist:
                            if value+0.3>=i[1]>=value-0.3:
                                data['all']["ratedaround"].append(i[0])
                        print(data['all']['ratedaround'])
                        if data['all']['ratedaround'] == []:
                            return redirect(url_for("error", token = "norateduser"))
                        else:
                            return render_template('find.html',data=data)    
                    except:
                        #Songs
                        value = value+".mp3"
                        print(value)
                        songs = db.session.query(Songs).all()
                        data['all']['songs'] = []
                        for i in songs:
                            similarity_percentage = fuzz.ratio(value.lower(), i.name.lower())
                            if(i.name =="faded"):
                                print(similarity_percentage, "faded")
                            if similarity_percentage > 85:
                                data['all']['songs'].append(i)
                        print(data['all']['songs'])

                        value = value.split(".")[0]

                        #Playlists
                        playlists = db.session.query(Playlist).all()
                        playlists = [playlist for playlist in playlists if fuzz.ratio(value.lower(), playlist.name.lower()) > 85]
                        data['all']["playlists"] = playlists

                        
                        #Albums
                        albums = db.session.query(Album).all()
                        albums = [album for album in albums if fuzz.ratio(value.lower(), album.name.lower()) > 85]
                        data['all']['albums'] = albums
                        
                        #Genres
                        genres = db.session.query(Genre).all()
                        genres = [genre for genre in genres if fuzz.ratio(value.lower(), genre.genrename.lower()) > 85]

                        data['all']['genres'] = {}
                        for i in genres:
                            genresongs = db.session.query(Songs).filter(Songs.g_id == i.g_id).all()
                            data['all']["genres"][i.genrename] = genresongs

                        #Singers Name
                        dbsongs = db.session.query(Songs).all()
                        singers = []
                        for i in dbsongs:
                            names = i.singer.split(", ")
                            for j in names:
                                if(fuzz.ratio(value.lower(), j.lower())) > 85:
                                    singers.append(i)
                        data['all']['singers'] = singers

                        if data['all']["songs"] == [] and data['all']["playlists"] == [] and data['all']["genres"] == {} and data['all']["albums"] == [] and data["all"]["singers"]==[]:
                            return redirect(url_for("error", token="nothing"))
                        else:
                            return render_template('find.html',data=data)
                        
            else:
                return redirect(url_for("error", token="unauthenticated"))

            
    @app.route("/admin", methods=["GET"])
    def admin():
        if session.get('isLoggedIn') and session.get('profile')=="admin":
            if request.method == "GET":
                User = db.session.query(Admin).filter(Admin.admin_name==session.get("loggedUser")).first()
                total = 0
                creator = 0
                users = db.session.query(Loggers).all()
                for i in users:
                    if i.profile == "creator":
                        creator += 1
                    else:
                        total += 1

                track = len(db.session.query(Songs).all())
                album = len(db.session.query(Album).all())
                genre = len(db.session.query(Genre).all())
                data = {"nav": "uneven", "user": User, "e1":['Flagged Songs', 'displayflag'], "e2":['Tracks', url_for('track')], "e3":['Log Out', url_for('logout')], "totaluser": total, "totalcreator": creator, "tracks": track, "albums": album, "genre": genre}
                # bestsong = [[], []]
                # allsongs = db.session.query(Songs).all()
                # for i in allsongs:
                #     com = db.session.query(Comments).filter(Comments.s_id == i.s_id).all()
                #     avg = 0
                #     total = 0
                #     for j in com:
                #         if j.rating != None:
                #             avg += j.rating
                #             total += 1
                #     if total != 0:
                #         avg = avg/total
                #         bestsong[0].append(i.name.split('.')[0])
                #         bestsong[1].append(avg)

                # zipped_lists = zip(bestsong[0], bestsong[1])
                # sorted_lists = sorted(zipped_lists)
                # sorted_list2, sorted_list1 = zip(*sorted_lists)
                # values = sorted_list1[:7]
                # names = sorted_list2[:7]
                # max_length = 30
                # names = [label[:max_length] + '\n' + "" if len(label) > max_length else label for label in names]
                # print(names, values)
                # plt.figure(figsize=(10, 4))
                # plt.bar(names, values, color='skyblue')
                # plt.xticks(fontsize=7)
                # plt.ylabel('Ratings')
                # plt.title('Best song till date')
                # file_path = "./static/best.png"
                # plt.savefig(file_path)
                # plt.close()

                # most = db.session.query(Played).order_by(Played.plays.desc()).limit(7).all()
                # name = []
                # value = []
                # for i in most:
                #     name.append(db.session.query(Songs).filter(Songs.s_id == i.s_id).one().name.split('.')[0])
                #     value.append(i.plays)
                
                # name = [label[:max_length] + '\n' + "" if len(label) > max_length else label for label in name]
                # print(name, value)
                # plt.figure(figsize=(10, 4))
                # plt.bar(name[:7], value[:7], color='skyblue')
                # plt.xticks(fontsize=7)
                # plt.ylabel('Listens')
                # plt.title('Most Listened Song')
                # file_path = "./static/most.png"
                # plt.savefig(file_path)
                # print(data)

                data['best'] = "./static/best.png"
                data['most'] = "./static/most.png"

                latest = db.session.query(Songs).order_by(Songs.doc.desc()).limit(5).all()
                
                data['latest'] = latest
                return render_template("admindashboard.html", data = data)
        else:
            return redirect(url_for("error", token="unauthenticated"))
    

    @app.route("/logout", methods=["GET"])
    def logout():
        if request.method == "GET":
            # global isLoggedIn
            # global loggedProfile
            # global loggedUser
            # loggedUser = None
            # loggedProfile = None
            # isLoggedIn = False
            if os.path.exists("./static/best.png"):
                os.remove("./static/best.png")
                os.remove("./static/most.png")
            session['isLoggedIn'] = False
            session['loggedUser'] = None
            session["profile"] = None
            return redirect(url_for("welcome"))
        

    @app.route("/error/<token>", methods=["GET"])
    def error(token):
        if request.method == "GET":
            return render_template("error.html", data={"msg":error_obj[token][0], "red":error_obj[token][1]})



    @app.route("/creator", methods=["GET", "POST"])
    def creator():
        if session.get('isLoggedIn') and session.get('profile')=="user":
            global loggedProfile
            # global User
            User = db.session.query(Loggers).filter(Loggers.username==session.get("loggedUser")).first()
            if request.method == "GET":
                print(User.username, User.profile)
                if User.profile == "creator":
                    # data = {"nav": "prime", "user": User, "e1":['Creator Account', link], "e2":['Profile', 'profile'], "e3":['Log Out', 'logout'], 'p': "Create new Songs, Albums and much more", "h": "Kickstart your creators journey"}
                    data = {"nav": "prime", "user": User, "e1":['User Account', url_for("home")], "e2":['Upload Songs', url_for('upload')], "e3":['Log Out', 'logout'], 'p': "Create new Songs, Albums and much more", "h": "Kickstart your creators journey"}
                    return render_template("creator.html", data = data)
                else:
                    # data = data = {"nav": "prime", "user": User, "e1":['Creator Account', link], "e2":['Create Album', 'createalbum'], "e3":['Log Out', 'logout'], 'p': "Register as Creator", "h": "Create new Songs, Albums and much more!"}
                    data = data = {"nav": "prime", "user": User, "e1":['User Account', url_for("home")], "e2":['Create Album', 'createalbum'], "e3":['Log Out', 'logout'], 'p': "Register as Creator", "h": "Create new Songs, Albums and much more!"}
                    return render_template("creator.html", data = data)
            
            elif request.method == "POST":
                User = db.session.query(Loggers).filter(Loggers.username==session.get("loggedUser")).first()
                if User.profile == "user":
                    User.profile = "creator"
                    db.session.add(User)
                    db.session.commit()
                    loggedProfile = "creator"
                    return redirect(url_for("creator"))
                else:
                    return redirect(url_for("upload"))
        else:
            return redirect(url_for("error", token="unregistered"))
        

    @app.route("/creatorshome", methods=["GET", "POST"])   #uploaded.html
    def creatorshome():
        if request.method == "GET":
            global loggedProfile
            # global loggedUser
            # global User
            if session.get('isLoggedIn') and session.get('profile')=="user":
                User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
                data = {"nav": "second", "user": User, "e1":['User Account', 'home'], "e2":['Upload Songs', 'upload'], "e3":['Log Out', 'logout']}
                return redirect(url_for("dashboard"))
            else:
                return redirect(url_for("error", token="unauthenticated"))
            


    @app.route("/upload", methods=["GET", "POST"])
    def upload():
        if session.get('isLoggedIn') and session.get('profile')=="user":
            if request.method == "GET":
                User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
                genrelist = [i.genrename for i in db.session.query(Genre).all()]
                data = {"nav": "second", "user": User, "e1":['User Account', url_for('home')], "e2":['Dashboard', url_for('dashboard')], "e3":['Log Out', url_for('logout')], 'genre':genrelist}
                return render_template("upload.html", data=data)
            
            if request.method == "POST":
                name = request.form["name"]
                singer = request.form["singer"]
                doc = datetime.strptime(request.form["doc"], '%Y-%m-%d').strftime('%d-%b-%Y')
                lyrics = request.form["lyrics"] 
                m_file = request.files["m_file"]
                p_file = request.files['p_file']
                genre = request.form["genre"]
                print(name, singer, doc, p_file.filename)
                listofsongs = [i.name.lower() for i in db.session.query(Songs).all()]
                if name in listofsongs:
                    return redirect(url_for("error", token = "existingsong"))
                m_file.save('./static/songs/'+name+'.mp3')
                p_file.save('./static/images/'+name+"."+p_file.filename.split(".")[1])
                User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
                newsong = Songs(name = name+".mp3", singer=singer, doc = str(doc), lyrics=lyrics, l_id = User.l_id, g_id=db.session.query(Genre).filter(Genre.genrename == genre).first().g_id, rating=0)
                db.session.add(newsong)
                db.session.commit()
                if session.get("link") == "creator":
                    session["link"] = "creatorshome"
                return redirect(url_for("creatorshome"))
        else:
            return redirect(url_for("error", token="unauthenticated"))
        
            
                
    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():
        global loggedProfile
        # global loggedUser
        # global User
        if request.method == "GET":
            if session.get('isLoggedIn') and session.get('profile')=="user":
                User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
                title1 = 'Total Songs Uploaded'
                title2 = "Average Rating"
                title3 = "Total Playlist"
                title4 = "Total Albums"
                allsongs = db.session.query(Songs).filter(Songs.l_id == User.l_id).all()
                text1 = len(allsongs)
                sumup = 0
                total = 0
                for i in allsongs:
                    com = db.session.query(Comments).filter(Comments.s_id == i.s_id).all()
                    print(com)
                    for j in com:
                        if j.rating != None:
                            sumup += int(j.rating)
                            total += 1
                if sumup == 0:
                    text2 = 0
                else:
                    text2 = sumup / total
                if (type(text2)!=int):
                    text2 = round(text2, 1)
                text3 = len(db.session.query(Playlist).filter(Playlist.l_id == User.l_id).all())
                text4 = len(db.session.query(Album).filter(Album.By == User.l_id).all())
                data = {"nav": "second", "user": User, "e1":['User Account', 'home'], "e2":['Upload Songs', 'upload'], "e3":['Log Out', 'logout'], "ds":[[title1, text1], [title2, text2], [title3, text3], [title4, text4]], "songs": allsongs}
                print(allsongs)
                return render_template("dashboard.html", data=data)
            else:
                return redirect(url_for("error", token="unauthenticated"))
            
        elif request.method == "POST":
            if session.get('isLoggedIn') and session.get('profile')=="user":
                if "save" in request.form:
                    print("IN EDIT")
                    s_id = request.form["save"]
                    song = db.session.query(Songs).filter(Songs.s_id == s_id).one()
                    os.rename("./static/songs/"+song.name, "./static/songs/"+request.form["name"]+".mp3")
                    filename = song.name.split(".")[0]
                    for file_name in os.listdir('./static/images'):
                        if file_name.split(".")[0] == filename:
                            base_name, extension = os.path.splitext(file_name)
                            os.rename("./static/images/"+file_name, "./static/images/"+request.form["name"]+extension)
                            break
                    song.name = request.form["name"]+".mp3"
                    song.lyrics = request.form["lyrics"]
                    song.singer = request.form["singer"]
                    db.session.add(song)
                    db.session.commit()
                    return redirect(url_for("dashboard"))
                if "delete" in request.form:
                    s_id = request.form["delete"]
                    todelete = db.session.query(Songs).filter(Songs.s_id == s_id).one()
                    db.session.delete(todelete)
                    todelete = db.session.query(Comments).filter(Comments.s_id == s_id).all()
                    for i in todelete:
                        db.session.delete(i)
                    todelete = db.session.query(LoggersPlaylist).filter(LoggersPlaylist.s_id == s_id).all()
                    for i in todelete:
                        db.session.delete(i)
                    todelete = db.session.query(Composer).filter(Composer.s_id == s_id).all()
                    for i in todelete:
                        db.session.delete(i)
                    todelete = db.session.query(Played).filter(Played.s_id == s_id).all()
                    for i in todelete:
                        db.session.delete(i)
                    todelete = db.session.query(S_Album).filter(S_Album.s_id == s_id).all()
                    for i in todelete:
                        db.session.delete(i)
                    todelete = db.session.query(Flag).filter(Flag.s_id == s_id).all()
                    for i in todelete:
                        db.session.delete(i)
                    db.session.commit()
                    return redirect(url_for("dashboard"))
            
            else:
                return redirect(url_for("error", token="unauthenticated"))



        # if request.method == "POST":
        #     render uploaded songlist

    
    @app.route("/about/<int:id>", methods=["GET", "POST"])
    def about(id):
        if session.get('isLoggedIn') and session.get('profile')=="user":
            if request.method == "GET":
                song = db.session.query(Songs).filter(Songs.s_id==id).one().name
                User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
                print(session.get("link"))
                data = {"nav": "even", "user": User, "e1":['Dashboard', url_for(session.get('link'))], "e2":['User Account', url_for('home')], "e3":['Log Out', 'logout']}
                comments = db.session.query(Comments).filter(Comments.s_id == id).all()
                totallikes = 0
                totalcomments = 0
                totalplays = 0
                if comments != []:
                    for i in comments:
                        if i.comment != "":
                            totalcomments+=1
                        if i.liked == 1:
                            totallikes+=1
                tup = db.session.query(Played).filter(Played.s_id == id).first()
                if tup:
                    totalplays = tup.plays

                comments2 = []
                for i in comments:
                    print(i.comment)
                    if i.comment != "":
                        comments2.append([i, db.session.query(Loggers).filter(Loggers.l_id == i.l_id).one()])
                
                print(comments2)
                data['totallikes'] = totallikes
                data['totalcomments'] = totalcomments
                data['totalplays'] = totalplays
                data['comments'] = comments2
                data['song'] = song
                return render_template("about.html", data=data)


    @app.route("/playlist/<int:id>", methods=["GET", "POST"])
    def playlist(id):
        global loggedProfile
        # global loggedUser
        # global User
        if request.method == "GET":
            if session.get('isLoggedIn') and session.get('profile')=="user":
                songs = db.session.query(Playlist).filter(Playlist.p_id == id).one().songlist
                print(songs)
                User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
                data = {"nav": "second", "id":db.session.query(Playlist).filter(Playlist.p_id == id).one(), "songlist":songs, "user": User, "e1":['User Account', url_for("home")], "e2":['Upload Songs', url_for("upload")], "e3":['Log Out', url_for("logout")]}
                return render_template("playlist.html", data=data)
            else:
                return redirect(url_for("error", token="unauthenticated"))
        
        if request.method == "POST":
            if session.get('isLoggedIn') and session.get('profile')=="user":
                if "search" in request.form:
                    song = request.form["song"].lower()
                    songs = db.session.query(Songs).all()
                    matched = []
                    for i in songs:
                        similarity_percentage = fuzz.ratio(song.lower(), i.name.split(".")[0].lower())
                        print(i.name, similarity_percentage)
                        if(i.name =="faded"):
                            print(similarity_percentage, "faded")
                        if similarity_percentage > 90:
                            matched.append(i)
                    print(matched)
                    if (len(matched)!=0):
                        exists = db.session.query(LoggersPlaylist).filter(LoggersPlaylist.p_id==id).filter(LoggersPlaylist.s_id == matched[0].s_id).all()
                        if exists == []:
                            addition = LoggersPlaylist(p_id = id, s_id = matched[0].s_id)
                            db.session.add(addition)
                            db.session.commit()
                            return redirect(url_for("playlist", id=id))
                        else:
                            return redirect(url_for("playlist", id=id))
                    else:
                        return redirect(url_for("error", token="nothing"))
                
                if "delete" in request.form:
                    val = int(request.form["delete"])
                    print(val, id)
                    instance = db.session.query(LoggersPlaylist).filter(LoggersPlaylist.s_id == val).filter(LoggersPlaylist.p_id == id).one()
                    db.session.delete(instance)
                    db.session.commit()
                    return redirect(url_for("playlist", id=id))
                
                if "deletep" in request.form:
                    entries = db.session.query(LoggersPlaylist).filter(LoggersPlaylist.p_id == id).all()
                    print(entries)
                    for i in entries:
                        db.session.delete(i)
                        db.session.commit()
                    db.session.delete(db.session.query(Playlist).filter(Playlist.p_id == id).one())
                    db.session.commit()
                    return redirect(url_for("home"))
                
                if "playlist" in request.form:
                    pl = db.session.query(Playlist).filter(Playlist.p_id == id).one()
                    pl.name = request.form["name"]
                    db.session.add(pl)
                    db.session.commit()
                    return redirect(url_for("playlist", id=id))
            
            else:
                return redirect(url_for("error", token="unauthenticated"))
                


    
    

    @app.route("/lyrics/<int:id>", methods=["GET", "POST"])
    def lyrics(id):
        global link
        global loggedProfile
        # global loggedUser
        # global User
        comment = None
        User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
        if User == None:
            User = db.session.query(Loggers).filter(Admin.admin_name==session.get('loggedUser')).first()
        if request.method == "GET":
            if session.get('isLoggedIn') and session.get('profile')=="user":
                song = db.session.query(Songs).filter(Songs.s_id == id).one()
                play = db.session.query(Played).filter(Played.s_id == song.s_id).all()
                print(play)
                if play == []:
                    newplay = Played(s_id = song.s_id, plays = 1)
                    db.session.add(newplay)
                    db.session.commit()
                else:
                    newplay = play[0]
                    newplay.plays = newplay.plays + 1
                    db.session.add(newplay)
                    db.session.commit()
                comment = db.session.query(Comments).filter(User.l_id == Comments.l_id).filter(Comments.s_id == song.s_id).all()
                print(comment)
                if comment == []:
                    comment = Comments(comment = "", liked=0, s_id = song.s_id, l_id = User.l_id)
                    db.session.add(comment)
                    db.session.commit()
                else:
                    comment = comment[0]
                filename = song.name.split(".")[0]
                for file_name in os.listdir('./static/images'):
                    if file_name.split(".")[0] == filename:
                        base_name, extension = os.path.splitext(file_name)
                        break
                print(base_name + extension)
                data = {"nav": "second", "user": User, 'extension':extension, "e1":['User Account', url_for("home")], "e2":['Upload Songs', url_for("upload")], "e3":['Log Out', url_for("logout")]}
                print(id ,comment.comment, song.name)
                data1 = { "song": song, "comment": comment}
                return render_template("lyrics.html", data1 = data1, data = data)
            else:
                return redirect(url_for("error", token="unauthenticated"))
            
        if request.method == "POST":
            if session.get('isLoggedIn') and session.get('profile')=="user":
                comment = db.session.query(Comments).filter(User.l_id == Comments.l_id).filter(Comments.s_id == id).one()
                if "like" in request.form:
                    if comment.liked == 1:
                        comment.liked = 0
                    else:
                        comment.liked = 1
                    db.session.add(comment)
                    db.session.commit()
                    return redirect(url_for("lyrics", id = comment.s_id))
                if "comment" in request.form:
                    comment.comment = request.form["comment-text"]
                    db.session.add(comment)
                    db.session.commit()
                    return redirect(url_for("lyrics", id = comment.s_id))
                if "rate" in request.form:
                    rating = request.form["exampleRadios"]
                    # print(rating, "thiajdsfoiadsjfdskajfskladfj")
                    comment.rating = int(rating)
                    db.session.add(comment)
                    db.session.commit()
                    return redirect(url_for("lyrics", id = comment.s_id))
            else:
                return redirect(url_for("error", token="unauthenticated"))


    @app.route("/alyrics/<int:id>", methods=["GET"])
    def alyrics(id):
        # global loggedUser
        comment = None
        User = db.session.query(Admin).filter(Admin.admin_name==session.get('loggedUser')).first()
        if request.method == "GET":
            if session.get('isLoggedIn') and session.get('profile')=="admin":
                song = db.session.query(Songs).filter(Songs.s_id == id).one()
                
                filename = song.name.split(".")[0]
                for file_name in os.listdir('./static/images'):
                    if file_name.split(".")[0] == filename:
                        base_name, extension = os.path.splitext(file_name)
                        break
                data = {"nav": "uneven", 'extension':extension, "user": User, "e1":['Tracks', url_for('track')], "e2":['Dashboard', url_for('admin')], "e3":['Log Out', url_for('logout')]}
                data1 = { "song": song}
                return render_template("alyrics.html", data1 = data1, data = data)
            else:
                return redirect('welcome')
            
    @app.route("/track", methods=["GET", "POST"])
    def track():
        # global loggedUser
        comment = None
        User = db.session.query(Admin).filter(Admin.admin_name==session.get('loggedUser')).first()
        if session.get('isLoggedIn') and session.get('profile')=="admin":
            if request.method == "GET":
                data = {"nav": "uneven", "template": 1, "sub":"yes","user": User, "e1":['Dashboard', url_for('admin')],"e2":['Flagged Songs', 'displayflag'],"e3":['Log Out', 'logout']}
                data['genre'] = {}
                genres = db.session.query(Genre).all()
                for i in genres:
                    data['genre'][i.genrename] = []
                songs = db.session.query(Songs).all()
                for i in songs:
                    g_id = i.g_id
                    genre = db.session.query(Genre).filter(Genre.g_id == g_id).one()
                    data['genre'][genre.genrename].append([i, db.session.query(Flag).filter(Flag.s_id == i.s_id).all()==[]])
                # print(data['genre'])
                return render_template("track.html", data = data)

            if request.method == "POST":
                if 'delete' in request.form:
                    s_id = request.form['delete']
                    song = db.session.query(Songs).filter(Songs.s_id == s_id).one()
                    db.session.delete(song)
                    com = db.session.query(Comments).filter(Comments.s_id == s_id).all()
                    for i in com:
                        db.session.delete(i)
                    lp = db.session.query(LoggersPlaylist).filter(LoggersPlaylist.s_id == s_id).all()
                    for i in lp:
                        db.session.delete(i)
                    pl = db.session.query(Played).filter(Played.s_id == s_id).all()
                    for i in pl:
                        db.session.delete(i)
                    comp = db.session.query(Composer).filter(Composer.s_id == s_id).all()    
                    for i in comp:
                        db.session.delete(i)
                    comp = db.session.query(Flag).filter(Flag.s_id == s_id).all()
                    for i in comp:
                        db.session.delete(i)
                    db.session.commit()
                    return redirect(url_for("track"))
                
                if 'flag' in request.form:
                    s_id = request.form['flag']
                    flagged = db.session.query(Flag).filter(Flag.s_id == s_id).all()
                    if flagged == []:
                        newflag = Flag(s_id = s_id)
                        db.session.add(newflag)
                        db.session.commit()
                    else:
                        db.session.delete(flagged[0])
                        db.session.commit()
                    return redirect(url_for("track"))
                
                if 'search' in request.form:
                    data = {"nav": "uneven", "template": 2, "sub":"yes","user": User,"e2":["track", url_for("track")], "e1":['Dashboard', url_for('admin')],"e3":['Log Out', 'logout']}
                    value = request.form['song']
                    try:
                        value = float(value)
                        print("this my value", value)
                        songs = db.session.query(Songs).all()
                        alllist = []
                        for i in songs:
                            rating = db.session.query(Comments).filter(Comments.s_id == i.s_id and Comments.rating!=None).all()
                            if rating != []:
                                avg = 0
                                total = 0
                                for j in rating:
                                    if j.rating != None:
                                        avg += j.rating
                                        total += 1
                                if total!=0:
                                    avg = avg/total
                                alllist.append([i, avg])
                        
                        data['songs'] = []
                        for i in alllist:
                            if value+0.5>=i[1]>=value-0.5:
                                data["songs"].append([i[0], db.session.query(Flag).filter(Flag.s_id == i[0].s_id).all()==[]])
                        print(data['songs'])
                        if data['songs'] == []:
                            return redirect(url_for("error", token = "norated"))
                        else:
                            return render_template('track.html',data=data)    
                    except:
                        value = value+".mp3"
                        print(value)
                        songs = db.session.query(Songs).all()
                        data['songs'] = []
                        for i in songs:
                            similarity_percentage = fuzz.ratio(value.lower(), i.name.split(".")[0].lower())
                            print(i.name, similarity_percentage)
                            if(i.name =="faded"):
                                print(similarity_percentage, "faded")
                            if similarity_percentage > 85:
                                data['songs'].append([i, db.session.query(Flag).filter(Flag.s_id == i.s_id).all()==[]])
                        print(data['songs'])
                        if data['songs'] == []:
                            return redirect(url_for("error", token="doesntexist"))
                        else:
                            return render_template('track.html',data=data)

        else:
            return redirect(url_for("error", token="unauthenticated"))


    @app.route("/createalbum", methods=["GET", "POST"])
    def createalbum():
        # global loggedUser
        User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
        if session.get('isLoggedIn') and session.get('profile')=="user":
            if request.method == "GET":
                data = {"nav": "even", "user": User, "e1":['Creator Account', url_for("creatorshome")], "e2":['Home', url_for('home')], "e3":['Log Out', 'logout']}
                allsongs = db.session.query(Songs).filter(Songs.l_id == User.l_id).all()
                if allsongs != []:
                    data['songs'] = []
                    for i in allsongs:
                        data['songs'].append(i)
                    return render_template("createalbum.html", data=data)
                else:
                    return redirect(url_for("error", token="notcreator"))
            
            if request.method == "POST":
                name = request.form.get('name')
                checkboxes = request.form.getlist('checkbox')
                print(name, checkboxes)
                album = Album(name=name, By=User.l_id)
                db.session.add(album)
                db.session.commit()
                for i in checkboxes:
                    s = S_Album(s_id = int(i), a_id=album.a_id)
                    db.session.add(s)
                db.session.commit()

                return redirect(url_for("home"))
    
    @app.route("/album/<int:id>", methods=["GET", "POST"])
    def album(id):
        # global loggedUser
        User = db.session.query(Loggers).filter(Loggers.username==session.get('loggedUser')).first()
        if session.get('isLoggedIn') and session.get('profile')=="user":
            if request.method == "GET":
                album = db.session.query(Album).filter(Album.a_id==id).first()
                data = {"nav": "even", "user": User, "Owner":User.l_id==album.By, "e1":['Home', url_for("home")], "e2":['Create Album', url_for('createalbum')], "e3":['Log Out', url_for('logout')], "album": album}
                data['songs'] = []
                songs = db.session.query(S_Album).filter(S_Album.a_id == id).all()
                for i in songs:
                    data['songs'].append(db.session.query(Songs).filter(Songs.s_id == i.s_id).one())
                
                if User.profile == "creator":
                    allsongs = db.session.query(Songs).filter(Songs.l_id == User.l_id).all()
                    data['remainingsongs'] = []
                    for i in allsongs:
                        if i not in data['songs']:
                            data['remainingsongs'].append(i)
                return render_template("albumlist.html", data=data)
            
            if request.method == "POST":
                if "delete" in request.form:
                    db.session.delete(db.session.query(Album).filter(Album.a_id == id).one())
                    allsong = db.session.query(S_Album).filter(S_Album.a_id == id).all()
                    for i in allsong:
                        db.session.delete(i)
                    db.session.commit()
                    return redirect(url_for("home"))
                if "submit" in request.form:
                    print("HERE")
                    checkboxes = request.form.getlist('checkbox')
                    print(checkboxes)
                    for i in checkboxes:
                        s = S_Album(s_id = int(i), a_id=id)
                        db.session.add(s)
                    db.session.commit()
                    return redirect(url_for("album", id=id))
                if "deletesong" in request.form:
                    s_id = request.form["deletesong"]
                    db.session.delete(db.session.query(S_Album).filter(S_Album.s_id == s_id).filter(S_Album.a_id == id).one())
                    db.session.commit()
                    return redirect(url_for("album", id=id))

        else:
            return redirect(url_for("error", token="unauthenticated"))
            
            
    @app.route("/displayflag", methods=["GET", "POST"])
    def displayflag():
        # global loggedUser
        User = db.session.query(Admin).filter(Admin.admin_name==session.get('loggedUser')).first()
        if session.get('isLoggedIn') and session.get('profile')=="admin":
            if request.method == "GET":
                data = {"nav": "uneven", "template": 1, "sub":"yes","user": User, "e1":['Dashboard', url_for('admin')], "e2":['Tracks', 'track'],"e3":['Log Out', 'logout']}
                data['songs'] = []
                allflags = db.session.query(Flag).all()
                for i in allflags:
                    data['songs'].append([db.session.query(Songs).filter(Songs.s_id == i.s_id).one(), True])
                return render_template("display_flag.html", data=data)
        
            if request.method == "POST":
                s_id = request.form['flag']
                if 'delete' in request.form:
                    s_id = request.form['delete']
                    song = db.session.query(Songs).filter(Songs.s_id == s_id).one()
                    db.session.delete(song)
                    com = db.session.query(Comments).filter(Comments.s_id == s_id).all()
                    for i in com:
                        db.session.delete(i)
                    lp = db.session.query(LoggersPlaylist).filter(LoggersPlaylist.s_id == s_id).all()
                    for i in lp:
                        db.session.delete(i)
                    pl = db.session.query(Played).filter(Played.s_id == s_id).all()
                    for i in pl:
                        db.session.delete(i)
                    comp = db.session.query(Composer).filter(Composer.s_id == s_id).all()    
                    for i in comp:
                        db.session.delete(i)
                    comp = db.session.query(Flag).filter(Flag.s_id == s_id).all()
                    for i in comp:
                        db.session.delete(i)
                    db.session.commit()
                    
                flagged = db.session.query(Flag).filter(Flag.s_id == s_id).all()
                if flagged == []:
                    newflag = Flag(s_id = s_id)
                    db.session.add(newflag)
                    db.session.commit()
                else:
                    db.session.delete(flagged[0])
                    db.session.commit()
                return redirect(url_for("displayflag"))
        else:
            return redirect(url_for("error", token="unauthenticated"))