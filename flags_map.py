from flask import Flask
from urllib.request import urlopen 
from urllib.error import HTTPError

import base64
import csv
import folium
import geopandas
import hvplot.pandas
import matplotlib.pyplot as plt
#import mpld3
import numpy as np
import pandas as pd
import sys
import warnings

warnings.filterwarnings('ignore')

app = Flask(__name__)


@app.route('/')
def index():

	# Get centroids
	world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))

	# folium uses EPSG:4326 (WGS84)
	# TODO: For some reason, US and France look wrong but other countries look mostly right
	centroids = world.to_crs(4326).centroid
	centroid_list = pd.concat([world.name, centroids], axis=1)
	# world.plot(figsize=(18,12));
	# mpld3.show()

	# Get flags
	flags_dict =  pd.read_csv('Country_Flags.csv', header=None, index_col=0, usecols=[0,2], squeeze=True).to_dict()

	# Create base map
	folium_map =  folium.Map(location=[0,0], tiles="OpenStreetMap", zoom_start=2, max_bounds=True)
	folium.TileLayer('Stamen Terrain').add_to(folium_map)

	# Add markers at each centroid
	for index, c in centroid_list.iterrows():
		country = c['name']
		lon = c[0].x
		lat = c[0].y

		if not flags_dict.__contains__(country):
			print('Missing flag for ' + country, file=sys.stdout)
			continue

		# orig size 750x500
		flag = flags_dict[country]
		#print(flag, file=sys.stdout)

		# try:
		# 	encoded = base64.b64encode(urlopen(flag).read())
		# 	#decoded = base64.b64decode(encoded)
		# except HTTPError:
		# 	print('Missing url ' + flag, file=sys.stdout)
		# 	continue

		html=f"""
		<h1> {country}</h1>
		<img src={flag} style="width:180px;height:120px;padding:1px;border:thin solid black" />  
  		      """
		iframe = folium.IFrame(html=html, width=200, height=200)
		# html="""
		# <h1> {country}</h1>
		# <img src="data:image/svg+xml;base64,{encoded} style="width:180px;height:120px;">  
	 	#      """.format
		# iframe = folium.IFrame(html=html(country=country, encoded=encoded), width=200, height=200)
		popup = folium.Popup(iframe, max_width=2650)

		folium.Marker(
			location=[lat, lon],
			popup=popup
			).add_to(folium_map)


	return folium_map._repr_html_()


if __name__ == '__main__':
    app.run(debug=True)