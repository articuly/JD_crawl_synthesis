import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from queue import Queue
from redis import StrictRedis
from socket import socket, AF_INET, SOCK_STREAM
from libs.jd_sql import SaveQueueMange
from libs.jd_spider import JdSpider
from mysql.connector import pooling

# 缓存
redis = StrictRedis('127.0.0.1')
# 建立tcp服务器，监听爬虫请求
spider_server = socket(AF_INET, SOCK_STREAM)
spider_server.bind(('0.0.0.0', 8800))
spider_server.listen()
# 可多进程运行
spider_pool = ProcessPoolExecutor(max_workers=4)


# 运行爬虫，整合各环节
def run_spider(goods_id):
    # 创建队列存放结果
    q = Queue()
    # 默认为为处理器个数
    thread_pool = ThreadPoolExecutor()
    try:
        cnxpool = pooling.MySQLConnection(pool_name='mypool', pool_size=10,
                                          user='root', password='123456',
                                          host='127.0.0.1', database='jd', )
    except Exception as e:
        print('pool error', e)
    try:
        jd_spider = JdSpider(goods_id)
        goods_info = jd_spider.get_good_info()
        # 加入保存队列，商品信息
        SaveQueueMange.save_goods_info(q, goods_info)
        if goods_info.get('goods_name') is not None:
            goods_comment_summary_data = jd_spider.get_comments_summary()
            # 加入保存队列，商品概况
            SaveQueueMange.save_comment_summary(q, goods_comment_summary_data)
            # 加入保存队列，商品评论
            if goods_comment_summary_data:
                pages = min(2, round(goods_comment_summary_data['CommentCount'] / 10))
                futures = [thread_pool.submit(jd_spider.get_comments_list, page) for page in range(1, pages)]
                for futures in as_completed(futures):  # 等待所有线程完成
                    data = futures.result()  # 调用futures的返回值
                    SaveQueueMange.save_comment(q, goods_id, data)
    except Exception as e:
        print(e)
    # 所有SQL插入队列后，加入一个空值
    q.put(None)

    while True:
        try:
            cnx = cnxpool._get_connection()
        except Exception as e:
            print(e, 'wait......')
            time.sleep(0.1)
        else:
            try:
                sql = q.get()
                if sql is None:
                    # 单个队列的任务完成
                    q.task_done()
                    break
                try:
                    thread_pool.submit(SaveQueueMange.save_into_mysql(cnx, sql, q))
                except Exception as e:
                    print(e)
            except Exception as e:
                print(e)
    # 等待整个队列完成
    q.join()
    redis.rpush('can_analysis', goods_id)


if __name__ == '__main__':
    # 单进程执行
    run_spider(100012583158)
    # 多进程执行
    # spider_pool.submit(run_spider, 100002183459)
    # spider_pool.submit(run_spider, 100005855774)

    # 通过socket链接启动：
    # while True:
    #     client_sock, client_address = spider_server.accept()
    #     goods_id = client_sock.recv(30).decode()
    #     print('crawling', goods_id)
    #     client_sock.close()
    #     spider_pool.submit(run_spider, goods_id)
