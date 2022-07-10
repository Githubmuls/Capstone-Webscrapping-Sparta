from lib2to3.pgen2.pgen import DFAState
from sqlite3 import DatabaseError
from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class': 'lister-list'})
title_year = table.find_all('h3', attrs={'class':'lister-item-header'})
ratings = table.find_all('strong')
votes = table.find_all('p', attrs={'class': 'sort-num_votes-visible'})

row_length = len(title_year)

temp = [] #initiating a list 

for i in range(0, row_length):

    #get data
    title_year = table.find_all('h3', attrs={'class':'lister-item-header'})[i].text
    title = title_year.split("\n")
    
    ratings = table.find_all('strong')[i].text
    
    votes = table.find_all('p', attrs={'class': 'sort-num_votes-visible'})[i].text
    votes = votes.lstrip('\nVotes:\n').lstrip('\n').split("\n")

    temp.append((title[2], ratings, votes[0])) 

temp = temp[::-1]

#change into dataframe
data = pd.DataFrame(temp, columns = ('Title', 'Ratings', 'Votes'))

#insert data wrangling here
data['Votes'] = data['Votes'].str.replace(',','')
data['Ratings'] = data['Ratings'].astype('float64')
data['Votes'] = data['Votes'].astype('int64')

data = data.set_index('Title')

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{data["Votes"].mean().round(2)}' #be careful with the " and ' 

	# generate plot
	ax = data.plot(figsize = (10,9)) 
	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)