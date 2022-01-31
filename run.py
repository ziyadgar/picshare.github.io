from flask import Flask, jsonify, g, abort, request, redirect, render_template, url_for, flash, send_from_directory
import sqlite3
from werkzeug.utils import secure_filename
import hashlib
import requests
import os
from uuid import UUID, uuid4



UPLOAD_FOLDER = 'static/img/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
SECRET_KEY = 'ziyadG1990@'.encode('utf8')


app = Flask(__name__)
DATABASE = 'app.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = SECRET_KEY


# ------------------------------------------------- #
#                     DATABASE                      #
# ------------------------------------------------- #


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


# ------------------------------------------------- #
#                     Fonction                      #
# ------------------------------------------------- #

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def make_unique(string):
    ident = uuid4()
    my_tuple = string.partition(".")
    return f"{ident}" + f"{my_tuple[-2]}" + f"{my_tuple[-1]}"

# ------------------------------------------------- #
#                   GALERIE ZIYAD                   #
# ------------------------------------------------- #

#-------------------Route index-------------------
@app.route('/', methods=['GET'])
def index():
    try:
        db = get_db()
        cursor = db.execute("""SELECT name FROM categories""")
        elements = cursor.fetchall()
        my_list = []
        for element in elements:
            my_list.append(element[0])
        #----------------------Partie SELECT categories-------------------
        cursor2 = db.execute("""SELECT categories FROM images 
                            ORDER BY date DESC""")
        elements2 = cursor2.fetchall()
        my_list2 = []
        for elem2 in elements2:
            my_list2.append(elem2[0])
        #----------------------Partie SELECT nom du fichier---------------
        cursor3 = db.execute("""SELECT nom_du_fichier
                            FROM images 
                            ORDER BY date DESC""")
        elements3 = cursor3.fetchall()
        my_list3 = []
        for elem3 in elements3:
            my_list3.append(elem3[0])
        #----------------------Partie SELECT titre---------------
        cursor4 = db.execute("""SELECT titre
                            FROM images 
                            ORDER BY date DESC""")
        elements4 = cursor4.fetchall()
        my_list4 = []
        for elem4 in elements4:
            my_list4.append(elem4[0])
        #----------------------Partie SELECT id---------------
        cursor5 = db.execute("""SELECT id
                            FROM images 
                            ORDER BY date DESC""")
        elements5 = cursor5.fetchall()
        my_list5 = []
        for elem5 in elements5:
            my_list5.append(elem5[0])
        return render_template('index.html', 
                            zip=zip, 
                            my_list2=my_list2, 
                            my_list3=my_list3,
                            my_list4=my_list4,
                            my_list5=my_list5,
                            my_list=my_list)
    except Exception:
        return redirect('/')

# ------------------------------------------------- #
#                   UPLOAD LUCIE                    #
# ------------------------------------------------- #

@app.route("/upload/<name>")
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route("/upload/")
def show_upload():
    return render_template("upload.html")


@app.route("/upload/", methods=[ "POST" ])
def upload_picture():
    try:
        db = get_db()
        if "file" not in request.files:
            return redirect("/upload/")
        files=request.files["file"]
        nfiles = make_unique(files.filename)
        liste_pictures=[]
        cursor=db.execute("SELECT nom_du_fichier FROM images")
        for elem in cursor.fetchall():
            liste_pictures.append(elem[0])
        check=nfiles in liste_pictures
        titre=request.form["titre"]
        description=request.form["description"]
        categorie=request.form["categorie"]
        if (nfiles != ""
            and titre != ""
            and allowed_file(nfiles)
            and description != ""
            and categorie != ""
            and check is False):
            filename = secure_filename(nfiles)
            files.save(os.path.join(UPLOAD_FOLDER, filename))
            db=get_db()
            db.execute("INSERT INTO images (nom_du_fichier, titre, description, categories ) VALUES (?, ?, ?, ?)", [nfiles, titre, description, categorie])
            db.commit()
            return redirect ("/")
        flash("erreur lors du chargement du fichier !")
        return redirect("/upload/")
    except Exception:
        return redirect("/upload/")

# ------------------------------------------------- #
#              PICTURE PAGES ANN-LISE               #
# ------------------------------------------------- #

@app.route('/picturespage/<image_id>', methods=["POST"])
def commentary(image_id):
    db = get_db()
    # ----------------------------------Partie(DELETE) modifié par Ziyad GARGOURI---------------------
    confdelete = request.form.to_dict("confdelete")
    if confdelete == {"confdelete": "delete", "delete": "Supprimer"}:
        db.execute("PRAGMA foreign_keys=off")
        db.execute("""DELETE FROM `images` WHERE id=? """, [image_id,])
        db.execute("PRAGMA foreign_keys=on")
        db.commit()
        return redirect("/")
    # ----------------------------------FIN de la partie(DELETE) modifié par Ziyad GARGOURI-----------
    else:     
        surnom = request.form.to_dict()['pseudo']
        commentaire = request.form.to_dict()['commentary']
        vote = request.form.to_dict()['rangeInput']
        db.execute("PRAGMA foreign_keys=off")
        db.execute("""INSERT INTO commentaires (surnom, commentaire, vote, upload_id) 
                    VALUES (?, ?, ?, (SELECT images.id FROM images WHERE images.id = ?))""", (surnom, commentaire, vote, image_id,))
        db.execute("PRAGMA foreign_keys=on")
        db.commit()
        url = "/picturespage/" + image_id
        return redirect(url)


# -- AFFICHAGE DE L'IMAGE ET DE SES COMMENTAIRES -- #

@app.route('/picturespage/<image_id>')
def visualisation(image_id):
    imageid = image_id
    db = get_db()
    images = db.execute("SELECT nom_du_fichier, titre, description FROM images WHERE id=?",[imageid])
    elements = images.fetchall()
    my_list = []
    for elem in elements:
        my_list.append(elem)
    commentaires = db.execute("""SELECT commentaires.surnom, 
                              commentaires.commentaire, 
                              commentaires.vote FROM commentaires 
                              LEFT JOIN images 
                              ON commentaires.upload_id = images.id
                              WHERE images.id = (?)
                              ORDER by commentaires.date DESC""", [imageid,])
    elements = commentaires.fetchall()
    my_list1 = []
    for elem in elements:
        my_list1.append(elem)
    cursor2 = db.execute("""SELECT AVG(commentaires.vote) AS vote,
                        COUNT(commentaires.vote) AS nombre 
                        FROM commentaires LEFT JOIN images
                        ON commentaires.upload_id=images.id
                        WHERE vote != "0" AND images.id == ?""", (image_id,))
    elements2 = cursor2.fetchall()
    my_dict = {}
    for elem2 in elements2:
        my_dict.update({elem2[0]: elem2[1]})
    db.commit()
    url = "/picturespage/" + image_id
    return render_template('picturespage.html', url=url, all_images=my_list, my_list1=my_list1, my_dict=my_dict, int=int)    


if __name__ == '__main__':
    app.run(debug=True)
