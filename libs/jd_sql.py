class SaveQueueMange:
    # 写入商品基本信息的sql语句
    @staticmethod
    def save_goods_info(q, goods_data):
        sql = "replace into `jd`.`goods_info` (`goods_id`, `goods_name`, `goods_price`) " \
              "values ('{goods_id}', '{goods_name', '{goods_price');"
        try:
            sql = sql.format(**goods_data)
        except Exception as e:
            print(goods_data, e)
        else:
            q.put(sql)

    # 保存评论的语句
    @staticmethod
    def save_comment(q, goods_id, comments):
        # print(comments)
        sql_str = "replace into `jd`.`goods_comments` set " \
                  "comment_id={id}," \
                  "goods_id={goods_id}," \
                  "content={content}," \
                  "create_time={createtionTime}," \
                  "score={score}," \
                  "user_client={userClient}"
        for comment in comments:
            try:
                sql = sql_str.format(goods_id=goods_id, **comment)
            except Exception as e:
                print(comment, e)
            else:
                q.put(sql)

    # 写入摘要概况的语句
    @staticmethod
    def save_comment_summary(q, comments_summary_data):
        comments_summary = {
            'goods_id': comments_summary_data['ProductId'],
            'comment_count': comments_summary_data['CommentCount'],
            'default_good_count': comments_summary_data['DefaultGoodCount'],
            'good_count': comments_summary_data['GoodCount'],
            'good_rate': comments_summary_data['GoodRate'],
            'general_count': comments_summary_data['GeneralCount'],
            'general_rate': comments_summary_data['GeneralRate'],
            'poor_count': comments_summary_data['PoorCount'],
            'poor_rate': comments_summary_data['PoorRate'],
            'score_1_count': 0,
            'score_2_count': 0,
            'score_3_count': 0,
            'score_4_count': 0,
            'score_5_count': 0,
        }
        sql = "replace into `jd`.`goods_comment_summary` set " \
              "goods_id={goods_id}," \
              "comment_count={comment_count}," \
              "default_good_count={default_good_count},  " \
              "good_count={good_count}, " \
              "good_rate={good_rate}," \
              "general_count={general_count}, " \
              "general_rate={general_rate}, " \
              "poor_count={poor_count}, " \
              "poor_rate={poor_rate}, " \
              "score_1_count={score_1_count}, " \
              "score_2_count={score_2_count}, " \
              "score_3_count={score_3_count}, " \
              "score_4_count={score_4_count}, " \
              "score_5_count={score_5_count}"
        try:
            sql = sql.format(**comments_summary)
        except Exception as e:
            print('summary_error:', e)
        else:
            q.put(sql)

    # SQL写入数据库
    @staticmethod
    def save_into_mysql(cnx, sql, q):
        try:
            cursor = cnx.cursor()
            cursor.execute(sql)
            cnx.commit()
        except Exception as e:
            cursor.close()
            print('error:', e)
        else:
            print('sucess')
        finally:
            # 传出队列完成信号
            q.task_done()
            cnx.close()
