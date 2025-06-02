from app import app, db, DataSet

with app.app_context():
    print('数据集列表:')
    datasets = DataSet.query.all()
    for d in datasets:
        print(f'ID: {d.id}, 名称: {d.name}')
        if d.custom_fields:
            print(f'自定义字段: {d.custom_fields[:200]}...')
        else:
            print('自定义字段: 无')
        print('-' * 50) 