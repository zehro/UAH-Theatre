from sqlalchemy import create_engine

engine = create_engine('mysql+pymysql://test:sombra123@35.185.36.22/UAH_Theater')
connection = engine.connect()
# result = connection.execute("select * from AUDITACTION")
# for row in result:
#     print("Audit Action:", row['Name'])
# connection.close()
