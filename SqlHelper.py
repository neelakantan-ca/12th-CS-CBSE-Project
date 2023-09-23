def f(databasename, tablename, username, password, tuple):
    import mysql.connector as s

    try:
        m = s.connect(
            host="localhost",
            username="root",
            password="Harshan@4506",
            database="{}",
        ).format(databasename)
    except Exception:
        m = s.connect(
            host="localhost", username="root", password="Harshan@4506"
        )
        w = m.cursor()
        w.execute('create database "{}"').format(databasename)
    w.execute("use databasename")
    w.execute("show tables")
    q = w.fetchall()
    if tablename not in q:
        w.execute(
            'create table "{}"(Id varchar(50),Player_Name varchar(50),Score int'
        ).format(tablename)
