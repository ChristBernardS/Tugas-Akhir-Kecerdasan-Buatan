import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from flask import Flask, render_template, request
import pandas as pd
from datetime import datetime
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    # Read the DataFrame
    df = pd.read_csv("katalog_gempa.csv")

    # Change data type for each column
    df['tgl'] = pd.to_datetime(df['tgl'])
    df['ot'] = pd.to_datetime(df['ot'])
    df['Year'] = df['tgl'].dt.year
    df['Month'] = df['tgl'].dt.month_name()
    df['Day'] = df['tgl'].dt.day_name()
    df['Hour'] = df['ot'].dt.hour

    # Change the order of columns in the dataframe
    new_cols = ['remark', 'mag', 'depth', 'tgl', 'ot', 'Year', 'Month', 'Day', 'Hour', 'lat', 'lon', 'strike1', 'dip1', 'rake1', 'strike2', 'dip2', 'rake2']
    df = df[new_cols]
    df = df.reindex(columns = new_cols)

    # Fill NaN value with 0
    df.fillna(0, inplace = True)

    # Rename columns
    df.rename(columns = {'remark': 'Location', 'mag': 'Magnitude', 'depth': 'Depth (km)', 'tgl': 'Date',
                        'ot': 'Time', 'lat': 'Latitude', 'lon': 'Longitude'}, inplace = True)
    
    column_data = df['Location']
    
    lokasi = set()
    for value in column_data:
        lokasi.add(value)
    lokasi = sorted(lokasi)

    # Start the select form
    select_form = '<select id=\"DropDown\" name="data">'
    for value in lokasi:
        select_form += f'<option value="{value}">{value}</option>'
    select_form += '</select>'

    selected_value = None
    input_text = None
    input_date = None
    date_difference = None
    output = None
    if request.method == 'POST':
            selected_value = request.form.get('data')
            input_text = float(request.form.get('input_text'))
            input_date = request.form.get('input_date')
            output = "<hr>"
            output += f"<p>Anda memilih lokasi: <span class=\"outputValue\">{selected_value} </span></p>"
            output += f"<p>Anda mencari gempa berskala : <span class=\"outputValue\">{input_text} SR</span></p>"
            output += f"<p>Anda memasukan tanggal : <span class=\"outputValue\">{input_date}</span></p>"   
                       
            if input_date:
                selected_date = datetime.strptime(input_date, '%Y-%m-%d').date()
                today_date = datetime.today().date()
                date_difference = (selected_date - today_date).days
                output += f"<p>Perbedaan waktu dengan hari ini adalah : <span class=\"outputValue\"> {date_difference} hari</span></p>"

                event_occurence = len(df[(df['Magnitude']>input_text) & (df['Location']==selected_value)])
                lambdaJava = event_occurence/15
                span = date_difference/365
                x = 0
                p = ((np.exp(-span*lambdaJava))*(span*lambdaJava)**x)
                output += f'<p>Jumlah banyaknya peristiwa yang terjadi selama 15 tahun terakhir di {selected_value} dengan magnitudo minimal {input_text} adalah <span class="outputValue"> {event_occurence} kali</span></p>'
                output += f'<p>Intensitas gempa dalam 15 tahun terakhir adalah <span class="outputValue"> {round(lambdaJava,2)}</span></p>'
                output += f'<p>Perkiraan terjadinya gempa dalam {date_difference} hari kedepan dengan kriteria berada di {selected_value} dan magnitdo minimal {input_text} adalah <span class="outputValue"> {round((1-p)*100, 2)}% </span> </p>'


    # Render the form in the HTML template
    return render_template('template.html', 
                        select_form=select_form,
                        selected_value=selected_value,
                        input_text=input_text,
                        input_date=input_date,
                        date_difference=date_difference,
                        output=output)

if __name__ == '__main__':
    app.run(debug=True)