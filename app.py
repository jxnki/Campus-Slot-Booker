from flask import Flask,render_template,request
app=Flask(__name__)

import psycopg2

from dotenv import load_dotenv
import os

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

@app.route('/')
def home():
	return render_template('index.html')
	
@app.route('/book', methods=['GET', 'POST'])
def book():

    if request.method == 'POST':

        name = request.form['name']
        resource = request.form['resource']
        date = request.form['date']

        print(name, resource, date)

        return "Booking Submitted!"

    return render_template('book.html')
    

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST
)
print("Database connected successfully!")

if __name__=='__main__':
	app.run(debug=True)
