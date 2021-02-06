import streamlit as st
import numpy as np 
import pandas as pd 
import altair as alt 

st.title('GGD Palmes metingen - Dashboard (test fase)')

#Dataset aanmaken
url='https://raw.githubusercontent.com/ivmoorselaar/palmes_no2/main/NO2_JAREN.csv'
url2='https://github.com/ivmoorselaar/palmes_no2/blob/main/NO2_LOCATIES.xlsx?raw=true'

jaren=pd.read_csv(url,sep=';')
locaties=pd.read_excel(url2)

#Datasets bewerken
jaren=jaren.rename(columns={'CodeJ':'Code'})

loc=locaties[['Code', 'Gemeente', 'Type_meetpunt']]
loc.columns = loc.columns.str.strip()

no2=pd.merge(jaren, loc, how='left', on='Code')
no2=no2.rename(columns={'_2020':2020,'_2019':2019,'_2018':2018,'_2017':2017,'_2016':2016,'_2015':2015,'_2014':2014,'_2013':2013,
                             '_2012':2012, '_2011':2011,'_2010':2010})

#Selecteer op gemeente (meerdere gemeente tegelijk)
st.sidebar.title('Selecteer een of meerdere gemeentes')
subset_data = no2

gemeente_input = st.sidebar.multiselect(
'Selecteer Gemeente(s)',
no2.groupby('Gemeente').count().reset_index()['Gemeente'].tolist())
# by gemeente
if len(gemeente_input) > 0:
    subset_data = no2[no2['Gemeente'].isin(gemeente_input)]

#Tabel
st.header('Tabel: Gemiddelde NO2 concentratie in geselecteerde gemeente(s)')
if st.checkbox('Tabel Gemeente'):
	tabel=subset_data.groupby(['Gemeente','Type_meetpunt']).mean().reset_index()
	st.table(tabel.style.set_precision(1))
	

#Bar Graph
st.header('Gemiddelde NO2 concentratie in geselecteerde gemeente(s) per type meetpunt')
if st.checkbox('Grafiek (bar) Gemeente'):
	if len(gemeente_input) > 0:
		
		bars=(alt.
		  Chart(subset_data).
		  mark_bar().
		  encode(x='Gemeente',
		  y='mean(2020):Q',
		  color='Type_meetpunt:N',
		  column='Type_meetpunt:N').
		  properties(height=150, width=50))

		st.altair_chart(bars)

#Line graph
st.header('Ontwikkeling NO2 concentratie door de tijd per Gemeente')

#Selectie gemeente
if st.checkbox('Grafiek trend NO2'):
	if len(gemeente_input) > 0:
	    
		#Omvormen data
		df=subset_data.groupby(['Gemeente','Type_meetpunt']).mean().reset_index()
		df=df.melt(id_vars=['Gemeente','Type_meetpunt'])
		df=df.rename(columns={'variable':'Jaar', 'value':'NO2 jaargem'})
		df['Jaar'] = pd.to_datetime(df['Jaar'], format='%Y')

		#Trend
		multiline=alt.Chart(df).mark_line(point=True).encode(
		    x='Jaar',
		    y='NO2 jaargem',
		    color='Type_meetpunt',
		    strokeDash='Type_meetpunt')

		st.altair_chart(multiline)


st.header('Correlatie 2020 vs 2019')
""" Puntjes onder de rode lijn betekenen dat de concentratie
in 2020 hoger was vergeleken met 2019"""

#Met onderstaande if maak je aanvink box om grafiek te zien
if st.checkbox('Grafiek correlatie'):
	st.subheader(gemeente_input)
	points = alt.Chart(subset_data).mark_point().encode(
	    x='2020:Q',
	    y='2019:Q',
	    color='Type_meetpunt'
	).interactive()

	line = pd.DataFrame({
	    'no2_conc': [0, 50],
	    'no2_conc':  [0, 50],
	})

	line_plot = alt.Chart(line).mark_line(color= 'red').encode(
	    x= 'no2_conc',
	    y= 'no2_conc',
	)

	points + line_plot
#st.altair_chart(points)
