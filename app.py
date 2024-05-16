from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64 
import requests

plt.switch_backend('agg')

app = Flask(__name__)

def get_data():
    url = 'https://docs.google.com/spreadsheets/d/13Z7qMtifDp27RAb1RSCFWLNBIB86y4IL3yFXuBayT-4/export?format=xlsx&id=13Z7qMtifDp27RAb1RSCFWLNBIB86y4IL3yFXuBayT-4'
    response = requests.get(url)
    with open('data.xlsx', 'wb') as f:
        f.write(response.content)

    df = pd.read_excel('data.xlsx')

    return df

def generate_plot(df, column, plot_type):
    plt.figure(figsize=(12, 8))
    plt.rcParams.update({'font.size': 14, 'font.family': 'serif'})

    
    if plot_type == 'bar':
        labels = df.iloc[:, 0].tolist()
        values = pd.to_numeric(df[column], errors='coerce').dropna().tolist()
        if values:
            plt.bar(labels, values, color='red')
            plt.xlabel('Date and Time')
            plt.ylabel(column)
            plt.title(f'{column} Bar Plot')
            plt.xticks(rotation=90)
            plt.tight_layout()
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
    
            return chart_url
        
    
    elif plot_type == 'line':
        labels = df.iloc[:, 0].tolist()
        values = pd.to_numeric(df[column], errors='coerce').dropna().tolist()
        if labels and values:
            plt.plot(labels, values, marker='*', linestyle='-',color='green')
            plt.xlabel('Date and Time')
            plt.ylabel(column)
            plt.title(f'{column} Line Plot')
            plt.xticks(rotation=90)
            plt.tight_layout()

            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
    
            return chart_url
        
    elif plot_type == 'scatter':
        labels = df.iloc[:, 0].tolist()
        values = df[column].tolist()  
        if all(pd.notnull(value) for value in values):
            plt.scatter(labels, values)
            plt.xlabel('Date and Time')
            plt.ylabel(column)
            plt.title(f'{column} over Time')
            plt.xticks(rotation=90)
            plt.tight_layout()

            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
    
            return chart_url
        

    elif plot_type == 'box':
        values = pd.to_numeric(df[column], errors='coerce').dropna().tolist()
        if values:
            plt.boxplot(values)
            plt.xlabel(column)
            plt.title(f'{column} Distribution')
            plt.tight_layout()

            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            chart_url = base64.b64encode(img.getvalue()).decode()
            plt.close()
    
            return chart_url
        
    return None
        




    


@app.route('/', methods=['GET', 'POST'])
def index():
    df = get_data()

    if request.method == 'POST':
        plot_type = request.form.get('plot_type')

        columns = df.columns[1:]

        chart_data = []

        if plot_type:
            for column in columns:
                chart_url = generate_plot(df, column, plot_type)
                if chart_url:
                    chart_data.append((chart_url, column))

        table_html = df.to_html()

        return render_template('index.html', table_html=table_html, chart_data=chart_data)

    table_html = df.to_html()
    return render_template('index.html', table_html=table_html, chart_data=[])

if __name__ == '__main__':
    app.run(debug=True)
