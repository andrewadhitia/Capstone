from flask import Flask, render_template 
import pandas as pd
import requests
from bs4 import BeautifulSoup 
from io import BytesIO
import base64
import matplotlib.pyplot as plt

app = Flask(__name__)

def scrap(url):
    #This is fuction for scrapping
    url_get_cp =\
requests.get('https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=31-12-2019')
    soup_cp = BeautifulSoup(url_get_cp.content,"html.parser")
    
    #Find the key to get the information
    table_cp = soup_cp.find('table', attrs={'class':'table'})
    tr_cp = table_cp.find_all('tr')

    temp_cp = [] #initiating a tuple

    for i in range(1, len(tr_cp)):
        row = table_cp.find_all('tr')[i]
    
        #get tanggal
        tanggal = row.find_all('td')[0].text
        tanggal = tanggal.strip() #for removing the excess whitespace
    
        #get kurs jual
        jual = row.find_all('td')[1].text
        jual = jual.strip() #for removing the excess whitespace
      
        #get kurs beli
        beli = row.find_all('td')[2].text
        beli = beli.strip() #for removing the excess whitespace
    
        temp_cp.append((tanggal,jual,beli)) 
        
    temp_cp = temp_cp[::-1]
    
   #data wranggling -  try to change the data type to right data type
    df_cp = pd.DataFrame(temp_cp, columns = ('tanggal','jual','beli'))
    df_cp['jual'] = df_cp['jual'].str.replace(",",".").astype('float64') 
    df_cp['beli'] = df_cp['beli'].str.replace(",",".").astype('float64') 
    
    import dateparser

    df_cp['tanggal'] = df_cp.tanggal.apply(lambda x : dateparser.parse(x))

    df_cp = df_cp.set_index('tanggal')

   #end of data wranggling

    return df_cp

@app.route("/")
def index():
    df = scrap('https://monexnews.com/kurs-valuta-asing.htm?kurs=JPY&searchdatefrom=01-01-2019&searchdateto=31-12-2019') #insert url here

    #This part for rendering matplotlib
    fig = plt.figure(figsize=(5,2),dpi=300)
    df.plot()
    
    #Do not change this part
    plt.savefig('plot1',bbox_inches="tight") 
    figfile = BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)
    figdata_png = base64.b64encode(figfile.getvalue())
    result = str(figdata_png)[2:-1]
    #This part for rendering matplotlib

    #this is for rendering the table
    df = df.to_html(classes=["table table-bordered table-striped table-dark table-condensed"])

    return render_template("index.html", table=df, result=result)


if __name__ == "__main__": 
    app.run()
