# -*- coding: utf-8 -*-
"""
Code to scrape website contents 

Created on Wed Oct 22 19:36:30 2014
@author: tobie
"""
import pandas as pd
import requests

from lxml import html


#empty container to save website in
data = pd.DataFrame()
#empty list for temp use
el = []

base_url = 'http://globalenergyobservatory.org/'
scrape_url = 'http://globalenergyobservatory.org/list.php?db=PowerPlants&type=Coal'


#read all the links to dataframe data
#-------------------------------------
page  = requests.get(scrape_url)
dom   = html.fromstring(page.text)

for link in dom.xpath('//a/@href'): # select the url in href for all a tags(links)
    if 'geoid' in link:
        print "found url: ",base_url+link
        el.append(base_url+link)
data['url'] = el


#transverse all pages and save complete page to dataframe
#we should do this in parralel using map
#puts everything in a dataframe...not sure this is good iea
#idea was to pickle the dataframe...but did not work
#----------------------------------------------------------
el = []
for i, station_url in enumerate(data['url']):
    print station_url,
    page = requests.get(station_url)
    dom = html.fromstring(page.text)
    print 1428-i, 'to go'
    el.append(dom)
data['dom'] = el


#parse dom to find info
#uses xpath to get some info
#-scrape from DOM
data['description'] = data['dom'].apply(lambda x : x.xpath('//*[@class="wrapper"]/form[1]/div[1]/table[2]/tr/td/text()')[0])
data['name'] 		= data['dom'].apply(lambda x : x.xpath('//*[@id="Name"]/@value')[0])
data['boiler'] 		= data['dom'].apply(lambda x : x.xpath(' //*[@id="Boiler_Manufacturer_1"]/@value')[0])


#scrape from description tag using pythons text functions
#offsets hard coded. not a good idea should format change
data['units'] 		= data['description'].apply( lambda a : a[a.find('It has') + 7: a.find('It has')+9].rstrip() )
data['plant_type']  = data['description'].apply( lambda a : a[a.find('TYPE')   + 5: a.find('with')].rstrip())
data['capacity'] 	= data['description'].apply( lambda a : a[a.find('capacity of') + 12:a.find('MWe')].rstrip())
data['operated_by'] = data['description'].apply( lambda a : a[a.find('operated by') + 12 :-1].rstrip() )


#prepare xls writeout
#------------------------
writeout = pd.DataFrame()
writeout['name']            = data['name']
writeout['description']     = data['description']
writeout['plant_type']      = data['plant_type']
writeout['capacity']        = data['capacity']
writeout['units']           = data['units']
writeout['boiler']          = data['boiler']
writeout['operated_by']     = data['operated_by']
writeout['url']             = data['url']

# write out to excel -- the needed format
# you can use .to_csv() to be more portable
writeout.to_excel('power_scrape.xls')