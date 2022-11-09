##this code requires funtion inputs (lines 14-20)
##You must install the google earth engine API and authenticate it to use
##for GEE python api install see https://developers.google.com/earth-engine/guides/python_install

##importing libraries
import pandas as pd
import ee

# Initialize the library
ee.Initialize()

##These are the inputs for the function. The function requires all of them.
start_date = '2021-03-01'   ##Start of date range
end_date = '2021-04-30'     ##end of date range
longitude = -83.093234      ##Update with longitude of location
latitude = 42.28691         ##Update with latitude of location
scale = 10                  ##The scale in meters. Does not make a difference if only taking one point
dir_soil = r'C:\Users\Tarri\R_projects\HS650_final_project\data\soil.csv'              ##Make sure to update this with your directory and file name
dir_prec = r'C:\Users\Tarri\R_projects\HS650_final_project\data\prec.csv'              ##EX) r'C:\Users\User\Documents\fileName\pythonCode\'Test.csv'

def data_pull(i_date, f_date, long, lat, scale, dir_soil, dir_prec):

        #Import the Image collection data
    Soil_Moisture = ee.ImageCollection('NASA_USDA/HSL/SMAP10KM_soil_moisture')
    Precipitation = ee.ImageCollection('JAXA/GPM_L3/GSMaP/v6/operational')


        # Selection of appropriate bands and dates from each image collection.
    Surf_Soil_Moisture = Soil_Moisture.select('ssm').filterDate(i_date, f_date)                 ##surface moisture
    Sub_Soil_Moisture = Soil_Moisture.select('susm').filterDate(i_date, f_date)                 ##sub surface moisture
    Per_Soil_Moisture = Soil_Moisture.select('smp').filterDate(i_date, f_date)                  ##percent moisture
    hourly_Prec = Precipitation.select('hourlyPrecipRate').filterDate(i_date, f_date)           ##satellite precipitation
    hourly_Prec_gage = Precipitation.select('hourlyPrecipRateGC').filterDate(i_date, f_date)    ##gage corrected precipitation

        ##Defining the location of interest
    poi = ee.Geometry.Point(long, lat)

        #This section calculates and prints the mean value of the soil moisture collection at the point.
        #Can use to check if the correct bands have been chose by seeing the data.
        ##Only serves as a check, do not need section otherwise.
    surf_soil_mois_point = Surf_Soil_Moisture.mean().sample(poi, scale).first().get('ssm').getInfo()
    sub_soil_mois_point = Sub_Soil_Moisture.mean().sample(poi, scale).first().get('susm').getInfo()
    per_soil_mois_point = Per_Soil_Moisture.mean().sample(poi, scale).first().get('smp').getInfo()
    hourly_Prec_point = hourly_Prec.mean().sample(poi, scale).first().get('hourlyPrecipRate').getInfo()
    hourly_Prec_gage_point = hourly_Prec_gage.mean().sample(poi, scale).first().get('hourlyPrecipRateGC').getInfo()
    print('Average surface soil moisture at point:', surf_soil_mois_point, 'mm')
    print('Average subsurface soil moisture at point:', sub_soil_mois_point, 'mm')
    print('Average percent surface soil moisture at point:', per_soil_mois_point, '%')
    print('Average hourly precipitation rate at point:', hourly_Prec_point, 'mm/hr')
    print('Average hourly gage precipitation rate at point:', hourly_Prec_gage_point, 'mm/hr')

        #Get the data for the pixel intersecting the location of interest using the defined scale.
    surf_soil_mois_lst = Surf_Soil_Moisture.getRegion(poi, scale).getInfo()
    sub_soil_mois_lst = Sub_Soil_Moisture.getRegion(poi, scale).getInfo()
    per_soil_mois_lst = Per_Soil_Moisture.getRegion(poi, scale).getInfo()
    hourly_Prec_lst = hourly_Prec.getRegion(poi, scale).getInfo()
    hourly_Prec_gage_lst = hourly_Prec_gage.getRegion(poi, scale).getInfo()

        ##Sets up the dataframe
    def ee_array_to_df(arr, list_of_bands):
            #Transforms ee.Image.getRegion array to pandas.DataFrame.
        df = pd.DataFrame(arr)

            # Rearranges the header.
        headers = df.iloc[0]
        df = pd.DataFrame(df.values[1:], columns=headers)

            # Remove rows without data inside.
        df = df[['longitude', 'latitude', 'time', *list_of_bands]].dropna()

            # Convert the data to numeric values.
        for band in list_of_bands:
            df[band] = pd.to_numeric(df[band], errors='coerce')

            # Convert the time field into a datetime.
        df['datetime'] = pd.to_datetime(df['time'], unit='ms')

            # Keep the columns of interest.
        df = df[['datetime', *list_of_bands]]

        return df

        ##Sending data to the function to create datraframes
    surf_soil_mois_df = ee_array_to_df(surf_soil_mois_lst, ['ssm'])
    sub_soil_mois_df = ee_array_to_df(sub_soil_mois_lst, ['susm'])
    per_soil_mois_df = ee_array_to_df(per_soil_mois_lst, ['smp'])
    hourly_Prec_df = ee_array_to_df(hourly_Prec_lst, ['hourlyPrecipRate'])
    hourly_Prec_gage_df = ee_array_to_df(hourly_Prec_gage_lst, ['hourlyPrecipRateGC'])

        ##combining dataframes of similiar data.
    Soil_mois_Df = pd.merge(surf_soil_mois_df, sub_soil_mois_df, how='inner', on='datetime')
    Soil_mois_Df = pd.merge(Soil_mois_Df, per_soil_mois_df, how='inner', on='datetime')
    Prec_Df = pd.merge(hourly_Prec_df, hourly_Prec_gage_df, how='inner', on='datetime')

        #Saves out .CSV files for new data being pulled
    #Soil_mois_Df.to_csv(dir_soil)
    #Prec_Df.to_csv(dir_prec)
    return Soil_mois_Df, Prec_Df

soil, prec = data_pull(i_date=start_date, f_date=end_date, long=longitude,lat=latitude, scale=scale, dir_soil=dir_soil, dir_prec=dir_prec)

