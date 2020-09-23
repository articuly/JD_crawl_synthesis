from flask import Flask, render_template, session, jsonify
import os
from socket import socket, AF_INET, SOCK_STREAM
import re
from extensions import csrf, db
from form import SpiderForm
from settings import config
from models import GoodsInfo, GoodsCommentsSummary, GoodsComments
from redis import StrictRedis

# 初始化实例
app = Flask(__name__)
app.config.from_object(config)
csrf.init_app(app)
db.init_app(app)
redis = StrictRedis('127.0.0.1')


@app.route('/')
def hello_world():
    form = SpiderForm()
    return render_template('index.html', form=form)


@app.route('/runspider', methods=['post'])
def run_spider():
    form = SpiderForm()
    if form.validate():
        url = form.url.data
        goods_id = re.findall("(\d+)", url)[0]
        if goods_id in None:
            return ''
        session['goods_id'] = goods_id
        goods_info = GoodsInfo.query.get(goods_id)
        if goods_info is None:
            send_spider_request(goods_id)  # 没有分析记录则爬取
        return 'ok'  # 这里表示可以进入分析环节
    return jsonify(form.errors)


@app.route('/analysis')
def jd_analysis():
    '''
    输出商品名称，价格等信息
    输出好评，中评，差评占比
    输出用户评价词云图
    '''
    res = {
        'status': 'wait',
        'goods_info': None,
        'comments': None,
        'wordcloud': None,
    }
    goods_id = session['goods_id']
    goods_info = GoodsInfo.query.get(goods_id)
    print(goods_info)
    # 如果分析环节中，结果已经存在，直接输出分析结果
    if goods_info is not None and goods_info.can_analysis:
        analysis_result_path = os.path.join(app.config['RESULT_PATH'], session['goods_id'])
        comments_path = os.path.join(analysis_result_path, 'comment_analysis.png')
        wordcloud_path = os.path.join(analysis_result_path, 'comment_wordcloud.png')
        res = {
            'status': 'finish',
            'goods_info': {'goods_name': goods_id.goods_name,
                           'goods_price': goods_id.goods_price},
            # 将分析结果的图片路经由绝对路经转为Web访问路经
            'comments': comments_path.replace(app.config['BASEDIR'], ''),
            'wordcloud': wordcloud_path.replace(app.config['BASEDIR'], ''),
        }
    return jsonify(res)


def send_spider_request(goods_id):
    pass


if __name__ == '__main__':
    app.run()
