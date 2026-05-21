from pymilvus import MilvusClient, DataType

client = MilvusClient(uri="http://localhost:19530")
print("客户端创建好了")

schema = MilvusClient.create_schema(
    auto_id=True,
    enable_dynamic_field=False
)

schema.add_field(field_name="id",datatype=DataType.INT64,is_primary=True)
schema.add_field(field_name="text",datatype=DataType.VARCHAR,max_length=500)
schema.add_field(field_name="vector",datatype=DataType.FLOAT_VECTOR,dim=768)

client.create_collection(
    collection_name="test_memory",
    schema=schema
)
print("Collection 创建成功")

collections = client.list_collections()
print("当前 collection 列表：",collections)