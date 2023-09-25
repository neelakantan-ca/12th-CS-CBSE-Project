def insertData(username, password, table_name, data, database_name):
    #importing mysql connector
    import mysql.connector
    try:
        #connecting databases of players
        connection=mysql.connector.connect(host='localhost',username=username,password=password,database=database_name)
        #establishing a cursor for the above connection
        cursor=connection.cursor()  
        #inserting data into the table using the above established cursor
        cursor.execute(f"insert into {table_name} values('{data[0]}','{data[1]}')")
    except Exception as e:
        print(e)