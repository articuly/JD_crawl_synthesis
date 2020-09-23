import os
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from wordcloud import WordCloud
from mysql.connector import pooling

myfont = fm.FontProperties(fname='msyh.ttf')
mpl.rcParams['font.family'] = [myfont.get_name()]
mpl.use('agg')


class JdAnalysis:
    # 初始化，保存路经
    def __init__(self, goods_id, cnx, save_path=None):
        if save_path is None:
            base_path = os.path.abspath(os.path.dirname(__file__))
            save_path = os.path.join(base_path, 'static', 'analysis_picture')
        self.goods_id = goods_id
        self.save_path = os.path.join(save_path, str(goods_id))
        self.cnx = cnx
        self.cursor = cnx.cursor()

        if not os.path.exists(self.save_path):
            try:
                os.makedirs(self.save_path)
            except Exception as e:
                print('os', e)

    # 好评占比分析
    def run_analysis_comment_count(self):
        # 分析结果存储路经
        analysis_result_file_path = os.path.join(self.save_path, 'comment_analysis.png')
        comment_sql = "select good_count, general_count, poor_count from `jd`.`goods_comment_summary` where goods_id={goods_id};"
        comment_sql = comment_sql.format(goods_id=self.goods_id)

        df = pd.read_sql(comment_sql, self.cnx)
        # print(df.info())
        s = df.iloc[0]
        s.rename('好评占比', inplace=True)
        s.rename(index={'good_count': '好评', 'general_count': '中评', 'poor_count': '差评'}, inplace=True)
        print(s)
        try:
            ax = s.plot(kind='pie', figsize=(12, 12), autopct='%.1f%%', wedgeprops=dict(width=0.8, edgecolor='w'),
                        startangle=-30, fontsize=16, pctdistance=0.9, explode=(0, 0, 0.3), labeldistance=1.02)
        except Exception as e:
            print(e)
        try:
            ax.figure.savefig(analysis_result_file_path, dpi=300, bbox_inches='tight')
        except Exception as e:
            print(e)

    # 词云图生成
    def run_analysis_comment_wordcloud(self):
        analysis_results_file_path = os.path.join(self.save_path, 'comment_wordcloud.png')
        comment_sql = "select content from `jd`.`goods_comments` where goods_id={goods_id};"
        comment_sql = comment_sql.format(goods_id=self.goods_id)

        comments = pd.read_sql(comment_sql, self.cnx)
        text = ','.join(comments['content'])
        # 词云对象
        wc = WordCloud(width=1600, height=1200, background_color='white', font_path='msyh.ttf')
        hot_words = wc.generate(text)
        hot_words.to_file(analysis_results_file_path)

    def update_goods_info(self):
        sql = "update `jd`.`goods_info` set can_analysis=1 where goods_id={goods_id};"
        sql = sql.format(goods_id=self.goods_id)
        self.cnx.commit()

    def __del__(self):
        print(self.goods_id, '分析完成')
        try:
            self.cursor.close()
        except Exception as e:
            print(e)
        try:
            self.cnx.close()
        except Exception as e:
            print(e)


if __name__ == '__main__':
    cnxpool = pooling.MySQLConnectionPool(pool_name='mypool', pool_size=10,
                                          user='root', password='123456',
                                          host='localhost', database='jd')
    cnx = cnxpool.get_connection()

    jd_analysis = JdAnalysis(100002183459, cnx)
    jd_analysis.run_analysis_comment_count()
    jd_analysis.run_analysis_comment_wordcloud()
    jd_analysis.update_goods_info()
