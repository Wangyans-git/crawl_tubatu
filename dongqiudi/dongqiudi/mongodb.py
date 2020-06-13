import pymongo


class Handle_mongo_dongqiudi(object):
    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017")
        myclient.admin.authenticate("admin", "admin123")
        # 数据库名称
        self.mydb = myclient["dongchedi_mongo"]

    # 存储逻辑
    def save_data(self,colections_name,data):
        collection = self.mydb[colections_name]
        data = dict(data)
        collection.insert_one(data)


mongo = Handle_mongo_dongqiudi()