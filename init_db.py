import sqlite3

DATABASE = 'app.db'
db = sqlite3.connect(DATABASE)

cursor = db.cursor()

# Creation of table "images". If it existed already,
# we delete the table and create a new one
cursor.execute("""DROP TABLE IF
               EXISTS images""")
cursor.execute("""CREATE TABLE images
               (id INTEGER PRIMARY KEY
               AUTOINCREMENT,
               nom_du_fichier VARCHAR(30) NOT NULL,
               titre VARCHAR(50) NOT NULL,
               description VARCHAR(500) NOT NULL,
               categories VARCHAR(20) NOT NULL,
               date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL)""")

# Creation of table "commentaires"
cursor.execute("DROP TABLE IF EXISTS commentaires")
cursor.execute("""CREATE TABLE commentaires
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
               surnom VARCHAR(30) NOT NULL,
               commentaire VARCHAR(500) NOT NULL,
               hashtag VARCHAR(20),
               vote INTEGER,
               upload_id INTEGER NOT NULL,
               CONSTRAINT fk_images
               FOREIGN KEY (upload_id)
               REFERENCES images(upload_id)
               ON DELETE CASCADE)""")

# Creation of table "commentaires"
cursor.execute("DROP TABLE IF EXISTS commentaires")
cursor.execute("""CREATE TABLE commentaires
               (id INTEGER PRIMARY KEY AUTOINCREMENT,
               date TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
               surnom VARCHAR(30) NOT NULL,
               commentaire VARCHAR(500) NOT NULL,
               hashtag VARCHAR(20),
               vote INTEGER,
               upload_id INTEGER NOT NULL,
               CONSTRAINT fk_images
               FOREIGN KEY (upload_id)
               REFERENCES images(upload_id)
               ON DELETE CASCADE)""")

# création d'une table categories 
cursor.execute("""DROP TABLE IF
               EXISTS categories""")
cursor.execute("""CREATE TABLE categories
               (id INTEGER PRIMARY KEY
               AUTOINCREMENT,
               name VARCHAR(30) NOT NULL)""")

for name in ["People",
             "Animal",
             "Landscape",
             "Humor",
             "Nerd"]:
    cursor.execute("""INSERT INTO categories (name)
                    VALUES (?)""", (name,))

# We save our changes into the database file
db.commit()

# We close the connection to the database
db.close()
