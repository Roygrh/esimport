import sys
import yaml
from connectors import ElevenMsSqlConnector

if __name__ == '__main__':
    with open("config/config.yml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)

    # Display Date Route
    print('Moving data')
    print('from MsSql: ' + cfg['ELEVEN_HOST'])
    print('to ElasticSearch: ' + cfg['ES_HOST'])
    #step_size = input('Enter batch size:')
    print(cfg['OS'])
    if cfg['OS'] == 'windows':
        connection = "DRIVER={{SQL Server}};SERVER={0}; database={1}; \
                trusted_connection=no;UID={2};PWD={3}".format(cfg['ELEVEN_HOST'], cfg['ELEVEN_DB'],
                                                              cfg['ELEVEN_USER'],
                                                              cfg['ELEVEN_PASSWORD'])
    # Note: on linux server location defined in odbc.ini
    elif cfg['OS'] == 'linux':
        connection = "DSN=sqlserverdatasource; \
             trusted_connection=no;UID={0};PWD={1}".format(cfg['ELEVEN_USER'], cfg['ELEVEN_PASSWORD'])
    else:
        print('Unknown Operating System in config.yml. Should be windows or linux.')
        exit()

    sqlConn = ElevenMsSqlConnector(connection)
    print('MaxID: {0}'.format(sqlConn.maxId()))
