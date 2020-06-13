import pymongo

class Handle_mongo_guazi(object):
    def __init__(self):
        myclient = pymongo.MongoClient("mongodb://localhost:27017")
        myclient.admin.authenticate("admin", "admin123")

        # 数据库名称
        self.mydb = myclient['db_guazi']

    # 存储地区平台url数据逻辑
    def save_task(self,collection_name,task):
        print("当前存储的task为:%s"%task)
        collection = self.mydb[collection_name]
        task = dict(task)
        collection.insert_one(task)

    def get_task(self,collection_name):
        collection = self.mydb[collection_name]
        # 找到一个数据并且删除，保证task不重复
        task = collection.find_one_and_delete({})
        return task

    # 存储详细信息数据
    def save_data(self,collection_name,data):
        # print("当前存储的数据为:%s"%data)
        collection = self.mydb[collection_name]
        data = dict(data)
        # 根据car_id查询并更新数据，可以保证没有重复的数据，True为当没有该数据时就添加
        collection.update({'car_id':data['car_id']},data,True)


mongo = Handle_mongo_guazi()