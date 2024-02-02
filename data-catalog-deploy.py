# Inlined from /metadata-ingestion/examples/library/dataset_schema.py
# Imports for urn construction utility methods
from datahub.emitter.mce_builder import make_data_platform_urn, make_dataset_urn
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.emitter.rest_emitter import DatahubRestEmitter

import psycopg2
import sys


# Imports for metadata model classes
from datahub.metadata.schema_classes import *


# Database configuration - You might want to store these in environment variables
db_config = {
    # 'server': 'postgresql.postgresql-ns.svc.cluster.local',
    'server': 'datamgmtdemo01.eastasia.cloudapp.azure.com',
    'database': 'demodb01',
    'username': 'felixchung',
    'password': 'Passw0rd',
    'port': '30432' 
}

def case1():
    return StringTypeClass()

def case2():
    return BooleanTypeClass()

def case3():
    return NumberTypeClass()

def case4():
    return DateTypeClass()

def case5():
    return TimeTypeClass()

def get_db_connection(db_config):
    conn_string = f"dbname={db_config['database']} user={db_config['username']} password={db_config['password']} host={db_config['server']} port={db_config['port']}"
    conn = psycopg2.connect(conn_string)
    return conn

# Function to parse key-value pairs from command line arguments
def parse_key_value_pairs(argv):
    params = {}
    for arg in argv[1:]:  # Skip the script name
        key, value = arg.split('=', 1)
        params[key] = value
    return params

parameters = parse_key_value_pairs(sys.argv)
batchKey = parameters['batch_key']
token = parameters['token']

with get_db_connection(db_config) as conn:
    with conn.cursor() as cursor:
        try:
            cursor.execute("""
                select 
                    dataset_path
                    , name
                    , description
                    , data_type
                    , is_sensitive
                from 
                    DATA_CATALOG_DRAFT 
                where batch_key=%s
                """
                ,(batchKey,)
            )
            # Fetch all the rows
            rows = cursor.fetchall()
            dataset_name = '"."' .join(rows[0][0].split('/'))
            dataset_name = f'"{dataset_name}"'
            switch_dict = {
                        "VARCHAR": case1,
                        "BOOLEAN": case2,
                        "DECIMAL": case3,
                        "INTEGER": case3,
                        "BIGINT": case3,
                        "FLOAT": case3,
                        "DOUBLE": case3,
                        "DATE": case4,
                        "TIME": case5,
                        "TIMESTAMP": case5,
                    }
            
            fields = []
            for row in rows:
                dataset_path = row[0]
                name = row[1]
                description = row[2]
                data_type = row[3]
                is_sensitive = row[4]
                typeClass = switch_dict.get(data_type)()
                field = SchemaFieldClass(
                                fieldPath=name,
                                type=SchemaFieldDataTypeClass(type=typeClass),
                                nativeDataType=data_type,  # use this to provide the type of the field in the source system's vernacular
                                description=description,
                                lastModified=AuditStampClass(
                                    time=1640692800000, actor="urn:li:corpuser:ingestion"
                                ),
                            )
                fields.append(field)
                
            event: MetadataChangeProposalWrapper = MetadataChangeProposalWrapper(
                entityUrn=make_dataset_urn(platform="dremio", name=dataset_name, env="PROD"),
                aspect=SchemaMetadataClass(
                    schemaName="customer",  # not used
                    platform=make_data_platform_urn("dremio"),  # important <- platform must be an urn
                    version=0,  # when the source system has a notion of versioning of schemas, insert this in, otherwise leave as 0
                    hash="",  # when the source system has a notion of unique schemas identified via hash, include a hash, else leave it as empty string
                    platformSchema=OtherSchemaClass(rawSchema="__insert raw schema here__"),
                    lastModified=AuditStampClass(
                        time=1640692800000, actor="urn:li:corpuser:ingestion"
                    ),
                    fields=fields,
                ),
            )
            # Create rest emitter
            rest_emitter = DatahubRestEmitter(gms_server="http://datamgmtdemo01.eastasia.cloudapp.azure.com:31080", token=token)
            cursor.execute("update DATA_CATALOG_DRAFT set status = %s where batch_key=%s",('Completed',batchKey,))
            rest_emitter.emit(event)
            conn.commit()
        except psycopg2.DatabaseError as e:
            print(e)
            conn.rollback()  # Rollback the transaction on error
        finally:
            print('process ended')