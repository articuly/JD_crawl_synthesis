import os
from concurrent.futures import ProcessPoolExecutor
from redis import StrictRedis
from libs.jd_analysis import JdAnalysis
from mysql.connector import pooling

cnxpool = pooling.MySQLConnectionPool(pool_name='mypool', pool_size=10,
                                      user='root', password='123456',
                                      host='localhost', database='jd')
redis = StrictRedis('127.0.0.1')
process_pool = ProcessPoolExecutor(max_workers=4)

basedir = os.path.abspath(os.path.dirname(__file__))
save_path = os.path.join(basedir, 'static', 'analysis_picture')


def run_analysis(goods_id):
    while True:
        try:
            cnx = cnxpool.get_connection()
        except Exception as e:
            print(e)
            print('wait connection...')
        else:
            break
    jd_analysis = JdAnalysis(goods_id, cnx, save_path)
    jd_analysis.run_analysis_comment_count()
    jd_analysis.run_analysis_comment_wordcloud()
    jd_analysis.update_goods_info()


if __name__ == '__main__':
    #     redis.rpush('can_analysis', 100002183459)
    #     redis.rpush('can_analysis', 100005855774)
    #     redis.rpush('can_analysis', 100012583158)
    #     redis.rpush('can_analysis', 70349975885)

    while True:
        goods_id = redis.blpop('can_analysis')
        # 链接的元素为b字条，要解码，第一个元素是链表名，第二个是商品ID
        goods_id = goods_id[1].decode()
        process_pool.submit(run_analysis, goods_id)
