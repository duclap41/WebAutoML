import pyobdc

class MSSQLServer:
    def __init__(self, drive='SQL Server', server='localhost\\', database='qlnv3', username='', password=''):
        self.__drive = drive
        self.__sever = server
        self.__database = database
        self.__username = username
        self.__password = password
        self.__connection = None

    def connect(self):
        strsql = f"DRIVER={self.__drive};SERVER={self.__sever} ;DATABASE={self.__database};UID={self.__username};PWD={self.__password}"
        self.__connection = pyobdc.connect(strsql)
    def close(self):
        cursor = self.__connection.cursor()
        cursor.close()

    def select(self, query):
        try:
            cursor = self.__connection.cursor()
            cursor.execute(query)
        except:
            pass
        return cursor.fetchall()

if __name__ == '__main__':
    cn = MSSQLServer()
    cn.connect()
    #data = cn.select("select first_name, last_name, email, phone FROM sales.staffs")
