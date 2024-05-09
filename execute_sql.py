from space_etl import PostgresqlDestination

def create_schema(schema_name):
    db_name = 'my_database1'
    psql = PostgresqlDestination(db_name=db_name)
    print(schema_name)
    response = psql.create_schema(schema_name=schema_name)

    print(response)
    return response


def get_query():
    db_name = 'my_database1'
    query = f"select * from {db_name}.spacemissions_etl.space_missions;"
    
    psql = PostgresqlDestination(db_name=db_name)

    response = psql.query(query=query)
    print(response.fetchmany(2))



if __name__ == '__main__':
    # create_schema('exec_schema_1')
    get_query()


    

    