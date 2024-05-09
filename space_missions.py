import requests
import pandas as pd
import json
import space_etl

def extract_missions_data():
    list_of_missions = [
        "STS-40",
        "Biosatellite%20III",
        # "Biosatellite%20II",
        # "Cosmos%20782",
        # "Cosmos%20936",
        # "Cosmos%201514",
        # "Cosmos%201129",
        # "Cosmos%201667",
        # "Cosmos%201887",
        # "SpaceX-19",
        # "SpaceX-21",
        # "SpaceX-23",
        # "SpaceX-22"
    ]

    api_url = 'https://osdr.nasa.gov/'
    list_of_mission_data = []

    for mission in list_of_missions:
        mission_url = f'{api_url}geode-py/ws/api/mission/{mission}'

        print(f'The URL of the mission {mission} is : {mission_url}\n')
        print('--------------------------------------------------------\n')

        headers = {
            'Content-Type':'application/json',
            'Accept':'application/json'
        }

        get_mission_data = requests.get(mission_url,headers=headers)

        # print(get_mission_data)
        mission_data = get_mission_data.json()
        list_of_mission_data.append(mission_data)

    return list_of_mission_data
        
def transform_mission_data(list_of_mission_data):
    df = pd.DataFrame(list_of_mission_data)
    
    #Since postgres doesnt support the loading of nested dictionaries, we need to parse into json
    def parse_json(val):
        return json.dumps(val)
    
    df['vehicle'] = df['vehicle'].apply(parse_json)
    df['people'] = df["people"].apply(parse_json)
    df['versionInfo'] = df["versionInfo"].apply(parse_json)
    df['parents'] = df["parents"].apply(parse_json)
    df['added_col1'] = 2
    df['added_col2'] = 2.2323
    return df

def load_mission_data(df):
    #Creating schema in postgres named "spacemissions_etl"
    schema_name = 'spacemissions_etl'
    db_name = 'my_database1'
    table_name = 'space_missions'

    try:
        details = {
            'schema_name':schema_name,
            'db_name':db_name,
            'table_name':table_name
        }
        postgres = space_etl.PostgresqlDestination(db_name=db_name)

        postgres.write_dataframe(df=df,details=details)
        postgres.close_connection()

        print(f'Data was loaded successfully....')
    except Exception as e:
        print(f"Data failed to load:\n {e}")
        postgres.close_connection()




if __name__=='__main__':
    list_of_mission_data = extract_missions_data()
    df = transform_mission_data(list_of_mission_data=list_of_mission_data)
    load_mission_data(df=df)



        

    
    