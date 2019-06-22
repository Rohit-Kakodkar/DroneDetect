from pyspark.sql import DataFrameWriter
import os

class PostgresConnector(object):
    def __init__(self, hostname, dbname, pusername, password):
        self.database_name = dbname
        self.hostname = hostname
        self.url_connect = "jdbc:postgresql://{hostname}:5432/{db}".format(hostname=self.hostname, db=self.database_name)
        self.properties = {"user":pusername,
                      "password" :password,
                      "driver": "org.postgresql.Driver"
                     }
    def get_writer(self, df):
        return DataFrameWriter(df)

    def write(self, df, table, md):
        my_writer = self.get_writer(df)
        print("GOT HERE")
        df.write.jdbc(url=self.url_connect,table= table,mode=md,properties=self.properties)
