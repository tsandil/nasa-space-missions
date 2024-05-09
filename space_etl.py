from sqlalchemy import create_engine, text

class PostgresqlDestination:

    #Creating a Constructor to create the connection for the Load phase.
    def __init__(self,db_name) -> None:
        self.db_name = db_name
        self.db_user_name = 'tsandil'
        self.db_user_password = 'stratocaster'
        self.engine = create_engine(f'postgresql://{self.db_user_name}:{self.db_user_password}@127.0.0.1:5432/{self.db_name}')

    def create_schema(self,schema_name):
        with self.engine.connect() as conn:
            query = f"create schema if not exists {schema_name};"
            conn.execute(text(query))
            conn.commit()
            return conn

    # def query(self, query):
    #     with self.engine.connect() as conn:
    #         cur = conn.execute(text(query))
    #         return cur
    
    def execute_query(self,query):
        with self.engine.connect() as conn:
            result = conn.execute(text(query))
            conn.commit()
            return result
        
    def write_dataframe(self,df,details):
        table_name = details['table_name']
        schema_name = details['schema_name'] 
        schema_handle = SchemaDriftHandle(db_name=self.db_name)
        columns_to_add = schema_handle.check_schema_drift(df=df,details=details)
        if columns_to_add:
            schema_handle.handle_schema_drift(df=df,details=details,columns_to_add=columns_to_add)


        # if isinstance(self,SchemaDriftHandle):
        #     print("Performing Schema Drift Handle by adding necessary columns in the table...\n")
        #     schema_handle = SchemaDriftHandle(self.db_name)
        #     columns_to_add = schema_handle.check_schema_drift(df=df,details=details)
        #     if columns_to_add:
        #         schema_handle.handle_schema_drift(df=df,details=details,columns_to_add=columns_to_add)
            
        df.to_sql(table_name,schema = schema_name, con = self.engine, if_exists = 'append',index = False)
        
    def close_connection(self):
        return self.engine.dispose()
        

class SchemaDriftHandle(PostgresqlDestination):
    def __init__(self, db_name) -> None:
        super().__init__(self)
        super().__init__(db_name)
    
    def select_existing_columns(self,details):
        schema_name = details['schema_name']
        table_name = details['table_name']
        query = f"SELECT column_name FROM  information_schema.columns WHERE  table_schema = '{schema_name}' AND table_name = '{table_name}'"

        cur = self.execute_query(query=query)
        result = cur.fetchall()
        return result
    
    def check_schema_drift(self,df,details):
        with self.engine.connect() as conn:

            # Checking if column exists or no
            df_columns = df.columns.tolist()
            cur = self.select_existing_columns(details=details)

            existing_columns = [row[0] for row in cur]
            columns_to_add = [col for col in df_columns if col not in existing_columns]
            return columns_to_add    

    def add_columns(self, details,column_name, column_type):
        schema_name = details['schema_name']
        table_name = details['table_name']
        query = f"ALTER TABLE {schema_name}.{table_name} ADD COLUMN {column_name} {column_type}"
        
        cur = self.execute_query(query=query)
        print(f"Added column {column_name} of type {column_type} to the table.")
        return cur
    
    def alter_column_datatypes(self,details,column_name,column_type):
        schema_name = details['schema_name']
        table_name = details['table_name']
        query = f"ALTER TABLE {schema_name}.{table_name} ALTER COLUMN {column_name} TYPE {column_type}"
        cur = self.execute_query(query=query)
        print(f"Column : {column_name} has been altered to type {column_type}")
        return cur

    def get_column_datatypes(self,details):
        schema_name = details['schema_name']
        table_name = details['table_name']
        query = f"SELECT column_name, data_type FROM information_schema. columns WHERE table_schema = '{schema_name}' AND table_name = '{table_name}'; "
        cur = self.execute_query(query=query)
        result = cur.fetchall()
        print(result)
        return result
    
    def handle_schema_drift(self,df, details,columns_to_add):
            for column_name in columns_to_add:
                df_datatype = df[column_name].dtype
                column_type = self.map_df_dtype_to_postgres(df_datatype)
                self.add_columns(details=details,column_name=column_name,column_type=column_type)
        
    

    def map_df_dtype_to_postgres(self,df_dtype):
        dtype_map = {
            'int8':'SMALLINT',
            'int16':'SMALLINT',
            'int32':'INTEGER',
            'int64':'BIGINT',
            'float16':'REAL',
            'float32':'REAL',
            'float64':'DOUBLE PRECISION',
            'bool':'BOOLEAN',
            'datetime64[ns':'TIMESTAMP',
            'string':'TEXT',
            'boolean':'BOOLEAN',
            'datetime':'TIMESTAMP',
            'date':'DATE',
            'float':'DOUBLE PRECISION',
            'integer':'BIGINT',
            'arrays':'ARRAY',
            'datetime64':'TIMESTAMP',
            'object':'text',
            'category':'text',
            'mixed':'text',
        }

        dtype_str = str(df_dtype)
        column_type = dtype_map.get(dtype_str,'TEXT')

        return column_type
    

    



