from users.models import*
from datetime import timedelta
from agriculture2.settings import MEDIA_ROOT,DOMAIN
from users.serializers import*
from users.views import getDetails
import os
import csv,requests,datetime


# https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_South_Asia_24h.csv  #MODIS 1km
# https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_Asia_24h.csv     #VIIRS 375 S-NPP
# https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_South_Asia_24h.csv      #VIIRS 375m/NOAA-20

def job1():
    
    print(os.getcwd())
    directory = os.path.join(MEDIA_ROOT , 'NASADATA', str(datetime.datetime.today()).split()[0])
    if not os.path.exists(directory):
        os.makedirs(directory)


    print(str(datetime.datetime.today()))
    print("start VIIRS 375 S-NPP")
    link = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/suomi-npp-viirs-c2/csv/SUOMI_VIIRS_C2_South_Asia_24h.csv"
    locations = []
    count=0
    cs=0;
    csa=0
    
    filename='VIIRS_375_S-NPP_'+str(datetime.datetime.today()).split()[0]+'.csv'
    csvFile = open(os.path.join(directory,filename), 'w')
    csvFile.write('State,District,Block,Village,longitude,latitude,acq_date,acq_time\n');
    

    with requests.Session() as s:

        download= s.get(link)
        dec = download.content.decode('utf-8')
        cr = csv.reader(dec.splitlines(),delimiter=',')
        my_list = list(cr)
        
        for r in my_list[1:]:

            
            if float(r[0])<=30.35 and float(r[0])>=27.39 and float(r[1])<=77.36 and float(r[1])>=74.28:
                
                latitude=r[0]
                longitude=r[1]
                try:
                    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng='+latitude+','+longitude+'&key=AIzaSyB7DjJvNTqtsMUKR-SCwaGl3V-8VHkaslU') 
                except:
                    continue
                geo = response.json()
                
                district=None
                state=None
                village=None
                block=None
                data=[]
                try:
                    for x in range(len(geo['results'][0]['address_components'])):
                        if geo['results'][0]['address_components'][x]['types'][0]=="administrative_area_level_1":
                            state=geo['results'][0]['address_components'][x]['long_name']
                        elif geo['results'][0]['address_components'][x]['types'][0]=="administrative_area_level_2":
                            district=geo['results'][0]['address_components'][x]['long_name']
                        elif geo['results'][0]['address_components'][x]['types'][0]=="locality":
                            village=geo['results'][0]['address_components'][x]['long_name']
                except Exception as e:
                    print(e)



                if state != None and state.upper()=='HARYANA' and district != None and district.upper() in ['PANCHKUL','AMBALA','YAMUNANAGAR','KURUKSHETRA','KAITHAL','KARNAL','PANIPAT','SONIPAT','JIND','FATEHABAD','SIRSA','HISAR','BHIWANI','ROHTAK','JHAJJAR','MAHENDRAGARH','REWARI','GURUGRAM','NUH','FARIDABAD','PALWAL','CHARKHI DADRI']:
                    
                    if state!=None: state= state.upper()
                    if district!=None: district= district.upper()
                    if village!=None: village= village.upper()

                    cs=cs+1;
                    data.append(state)
                    data.append(district)
                    data.append(block)
                    data.append(village)
                    data.append(longitude)
                    data.append(latitude)
                    data.append(r[5])
                    data.append(r[6])
                    locations.append(data)
                    csvFile.write(
                        str(state) + ',' 
                      + str(district) + ',' 
                      + str(block) + ',' 
                      + str(village) + ',' 
                      + str(longitude) + ',' 
                      + str(latitude) + ','
                      + str(r[5]) + ','
                      + str(r[6]) + ','
                      + '\n')
                    dat={}
                    dat['state']=state
                    dat['district']=district
                    dat['block_name']=block
                    dat['village_name']=village
                    dat['longitude']=longitude
                    dat['latitude']=latitude
                    dat['acq_date'] = datetime.datetime.strptime(r[5], '%Y-%m-%d').strftime('%Y-%m-%d')
                    dat['acq_time']=str(r[6])[0:2]+':'+str(r[6])[2:4]+':00'
                    dat['satellite']='NPP'
                    try:
                        serializer = AddNASALocationDataSerializer(data=dat)
                        if serializer.is_valid():
                            csa=csa+1
                            serializer.save()                            
                    except Exception as e:
                        print(e)
                    
        print(cs)
        print(csa)
        print("stop VIIRS 375 S-NPP")
        csvFile.close()

    try:
        for data in locations:

            dat={}
            dis=District.objects.filter(state__state=data[0].upper(),district=data[1].upper())
            if(len(dis)==1):
                dat['district'] = dis[0].pk
            else:
                continue 


            vil=[]
            if data[3]!=None:
                vil=Village.objects.filter(village=data[3].upper(),block__district__district=data[1].upper())
                if(len(vil)==1):
                    dat['village_name'] = vil[0].pk

            dat['longitude'] = data[4]
            dat['latitude'] = data[5]
            
            Dda = []
            Dda = dda.objects.filter(district__district=data[1].rstrip().upper())
            if(len(Dda)==1):
                dat['dda'] = Dda[0].pk
            
           
            Ado = []
            if data[3]!=None:
                Ado = ado.objects.filter(village_ado__village=data[3].rstrip().upper())
                if len(Ado)==1:
                    dat['ado'] = Ado[0].pk
            
            dat['acq_date'] = datetime.datetime.strptime(data[6], '%Y-%m-%d').strftime('%Y-%m-%d')
            dat['acq_time']=str(r[6])[0:2]+':'+str(r[6])[2:4]+':00'
            serializer = AddLocationSerializer(data=dat)
            if serializer.is_valid():
                sss=serializer.save()
                count = count + 1;

                #storing location extra data in GeoDataLocation model
                result = None
                coordinates = data[5]+" ,"+data[4]
                xx=0;
                while result == None and xx<5:
                    try:
                        result = getDetails(coordinates)   
                    except:
                        xx+=1
                        pass
                
                if(result!=None):
                    geodata=dict()
                    geodata['location']=sss.id
                    geodata['murrabba_num']=result['Murabba No']
                    geodata['khasra_number']=result['Khasra No']
                    geodata['ownership']='|'.join(result['Owners Name']) 
                    try:
                        serializer1 = AddLocationGeoDataSerializer(data=geodata)
                        if serializer1.is_valid():
                            serializer1.save()
                    except:
                        pass

        print(count)
    except Exception as e:
        print(e)


    print("start VIIRS 375m_NOAA-20")
    link = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/noaa-20-viirs-c2/csv/J1_VIIRS_C2_South_Asia_24h.csv"      #VIIRS 375m/NOAA-20
    cs=0
    csa=0
    filename='VIIRS_375m_NOAA_'+str(datetime.datetime.today()).split()[0]+'.csv'
    csvFile = open(os.path.join(directory,filename), 'w')
    csvFile.write('State,District,Block,Village,longitude,latitude,acq_date,acq_time\n');
    

    with requests.Session() as s:

        download= s.get(link)
        dec = download.content.decode('utf-8')
        cr = csv.reader(dec.splitlines(),delimiter=',')
        my_list = list(cr)
        
        for r in my_list[1:]:

            
            if float(r[0])<=30.35 and float(r[0])>=27.39 and float(r[1])<=77.36 and float(r[1])>=74.28:
                
                latitude=r[0]
                longitude=r[1]
                try:
                    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng='+latitude+','+longitude+'&key=AIzaSyB7DjJvNTqtsMUKR-SCwaGl3V-8VHkaslU') 
                except:
                    continue
                geo = response.json()
                
                district=None
                state=None
                village=None
                block=None
                try:
                    for x in range(len(geo['results'][0]['address_components'])):
                        if geo['results'][0]['address_components'][x]['types'][0]=="administrative_area_level_1":
                            state=geo['results'][0]['address_components'][x]['long_name']
                        elif geo['results'][0]['address_components'][x]['types'][0]=="administrative_area_level_2":
                            district=geo['results'][0]['address_components'][x]['long_name']
                        elif geo['results'][0]['address_components'][x]['types'][0]=="locality":
                            village=geo['results'][0]['address_components'][x]['long_name']
                except Exception as e:
                    print(e)



                if state != None and state.upper()=='HARYANA' and district != None and district.upper() in ['PANCHKUL','AMBALA','YAMUNANAGAR','KURUKSHETRA','KAITHAL','KARNAL','PANIPAT','SONIPAT','JIND','FATEHABAD','SIRSA','HISAR','BHIWANI','ROHTAK','JHAJJAR','MAHENDRAGARH','REWARI','GURUGRAM','NUH','FARIDABAD','PALWAL','CHARKHI DADRI']:
                    
                    if state!=None: state= state.upper()
                    if district!=None: district= district.upper()
                    if village!=None: village= village.upper()

                    cs=cs+1;
                    csvFile.write(
                        str(state) + ',' 
                      + str(district) + ',' 
                      + str(block) + ',' 
                      + str(village) + ',' 
                      + str(longitude) + ',' 
                      + str(latitude) + ','
                      + str(r[5]) + ','
                      + str(r[6]) + ','
                      + '\n')
                    dat={}
                    dat['state']=state
                    dat['district']=district
                    dat['block_name']=block
                    dat['village_name']=village
                    dat['longitude']=longitude
                    dat['latitude']=latitude
                    dat['acq_date'] = datetime.datetime.strptime(r[5], '%Y-%m-%d').strftime('%Y-%m-%d')
                    dat['acq_time']=str(r[6])[0:2]+':'+str(r[6])[2:4]+':00'
                    dat['satellite']='NOAA'
                    try:
                        serializer = AddNASALocationDataSerializer(data=dat)
                        if serializer.is_valid():
                            csa=csa+1
                            serializer.save()
                    except Exception as e:
                        print(e)
        print(cs)
        print(csa)
        print("stop VIIRS 375m/NOAA-20")
        csvFile.close()






    print("start MODIS 1km")
    link = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_South_Asia_24h.csv"  #MODIS 1km
    cs=0
    csa=0
    filename='MODIS_1km_'+str(datetime.datetime.today()).split()[0]+'.csv'
    csvFile = open(os.path.join(directory,filename), 'w')
    csvFile.write('State,District,Block,Village,longitude,latitude,acq_date,acq_time\n');
    

    with requests.Session() as s:

        download= s.get(link)
        dec = download.content.decode('utf-8')
        cr = csv.reader(dec.splitlines(),delimiter=',')
        my_list = list(cr)
        
        for r in my_list[1:]:

            
            if float(r[0])<=30.35 and float(r[0])>=27.39 and float(r[1])<=77.36 and float(r[1])>=74.28:
                
                latitude=r[0]
                longitude=r[1]
                try:
                    response = requests.get('https://maps.googleapis.com/maps/api/geocode/json?latlng='+latitude+','+longitude+'&key=AIzaSyB7DjJvNTqtsMUKR-SCwaGl3V-8VHkaslU') 
                except:
                    continue
                geo = response.json()
                
                district=None
                state=None
                village=None
                block=None
                try:
                    for x in range(len(geo['results'][0]['address_components'])):
                        if geo['results'][0]['address_components'][x]['types'][0]=="administrative_area_level_1":
                            state=geo['results'][0]['address_components'][x]['long_name']
                        elif geo['results'][0]['address_components'][x]['types'][0]=="administrative_area_level_2":
                            district=geo['results'][0]['address_components'][x]['long_name']
                        elif geo['results'][0]['address_components'][x]['types'][0]=="locality":
                            village=geo['results'][0]['address_components'][x]['long_name']
                except Exception as e:
                    print(e)



                if state != None and state.upper()=='HARYANA' and district != None and district.upper() in ['PANCHKUL','AMBALA','YAMUNANAGAR','KURUKSHETRA','KAITHAL','KARNAL','PANIPAT','SONIPAT','JIND','FATEHABAD','SIRSA','HISAR','BHIWANI','ROHTAK','JHAJJAR','MAHENDRAGARH','REWARI','GURUGRAM','NUH','FARIDABAD','PALWAL','CHARKHI DADRI']:
                    
                    if state!=None: state= state.upper()
                    if district!=None: district= district.upper()
                    if village!=None: village= village.upper()

                    cs=cs+1;
                    csvFile.write(
                        str(state) + ',' 
                      + str(district) + ',' 
                      + str(block) + ',' 
                      + str(village) + ',' 
                      + str(longitude) + ',' 
                      + str(latitude) + ','
                      + str(r[5]) + ','
                      + str(r[6]) + ','
                      + '\n')
                    dat={}
                    dat['state']=state
                    dat['district']=district
                    dat['block_name']=block
                    dat['village_name']=village
                    dat['longitude']=longitude
                    dat['latitude']=latitude
                    dat['acq_date'] = datetime.datetime.strptime(r[5], '%Y-%m-%d').strftime('%Y-%m-%d')
                    dat['acq_time']=str(r[6])[0:2]+':'+str(r[6])[2:4]+':00'
                    dat['satellite']='MODIS'
                    try:
                        serializer = AddNASALocationDataSerializer(data=dat)
                        if serializer.is_valid():
                            csa=csa+1
                            serializer.save()
                    except Exception as e:
                        print(e)
        print(cs)
        print(csa)
        print("stop MODIS 1km")
        csvFile.close()