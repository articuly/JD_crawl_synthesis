import re
import random
import time
import requests
from lxml import html
from queue import Queue
from libs.utils import get_jsonp_dict


class JdSpider:
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'item.jd.com',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/85.0.4183.83 Safari/537.36',
    }
    goods_info = {}
    q = Queue()

    def __init__(self, goods_id):
        self.goods_id = goods_id
        self.goods_info['goods_id'] = goods_id

    def get_item_url(self):
        return 'https://item.jd.com/{0}.html'.format(self.goods_id)

    def get_price_url(self, callback_name):
        url = "https://c0.3.cn/stock?skuId={goods_id}" \
              "&area=12_988_40034_0&venderId={shop_id}&" \
              "buyNum=1&choseSuitSkuIds=&cat={cat}&" \
              "extraParam=%7B%22originid%22:%221%22%7D&fqsp=0" \
              "&pdpin=&pduid=827714610&ch=1&callback={callback_name}"
        return url.format(shop_id=self.shop_id, goods_id=self.goods_id, cat=self.cat, callback_name=callback_name)

    def get_comment_summary_url(self, callback_name):
        url = "https://club.jd.com/comment/productCommentSummaries.action?referenceIds={goods_id}&" \
              "callback={callback_name}&_={time_id}"
        return url.format(goods_id=self.goods_id, callback_name=callback_name, time_id=round(time.time()))

    def get_comment_url(self, page=1):
        url = "https://club.jd.com/comment/productPageComments.action?callback" \
              "=fetchJSON_comment98&productId={goods_id}&score=0&sortType=5&page=" \
              "{page}&pageSize=10&isShadowSku=0&fold=1"
        return url.format(goods_id=self.goods_id, page=page)

    def get_good_info(self):
        """
        从商品详情页面抓取商品名
        还需要抓取商品卖家id，分类用于jsonp接口
        """
        url = self.get_item_url()
        main_page = requests.get(url, headers=self.headers)
        name_xpath = "//div[@class='sku-name']/text()"
        dom = html.document_fromstring(main_page.text)

        try:
            goods_name = dom.xpath(name_xpath)[0].strip()
            if goods_name == '':
                goods_name = dom.xpath(name_xpath)[1].strip()
        except Exception as e:
            print('good_name', e)
        else:
            print(goods_name)
            self.goods_info['goods_name'] = goods_name

        try:
            shop_id = re.findall("venderId:.*?(\d+),", main_page.text)[0]
        except Exception as e:
            print('shop_id', e)
        else:
            self.shop_id = shop_id

        try:
            cat = re.findall("cat:.*?\[(\d+,\d+,\d+)\],", main_page.text)[0]
        except Exception as e:
            print('cat', e)
        else:
            self.cat = cat

        self.goods_info['goods_price'] = self.get_goods_price()
        return self.goods_info

    def get_goods_price(self):
        callback_name = 'jQuery' + str(random.randint(111111, 999999))
        url = self.get_price_url(callback_name)
        data = requests.get(url)
        dicts = get_jsonp_dict(callback_name, data.text)
        price = dicts['stock']['jdPrice']['p']
        print(price, '元')
        return price

    def get_comments_summary(self):
        """
        抓取评论概况
        """
        callback_name = 'jQuery' + str(random.randint(111111, 999999))
        url = self.get_comment_summary_url(callback_name)
        try:
            data = requests.get(url)
        except Exception as e:
            print('comment_summary', e)
            return None
        else:
            comments_data = get_jsonp_dict(callback_name, data.text)
            if comments_data.get('CommentsCount') is None:
                print(comments_data)
            else:
                return comments_data['CommentsCount'][0]

    def get_comments_list(self, page):
        """
        抓取评论列表
        :param page: 评论翻页
        """
        comment_url = self.get_comment_url(page=page)
        try:
            data = requests.get(comment_url)
        except Exception as e:
            print('comments', e)
            return None
        else:
            comments_data = get_jsonp_dict('fetchJSON_comment98', data.text)
            if comments_data.get("comments") is None:
                print(comments_data)
                return None
            else:
                return comments_data['comments']


if __name__ == '__main__':
    jd_spider = JdSpider(70349975885)
    goods_info = jd_spider.get_good_info()
    if goods_info.get('goods_name') is not None:
        goods_comment_summary_data = jd_spider.get_comments_summary()
        if goods_comment_summary_data:
            print(goods_comment_summary_data)
            pages = min(2, round(goods_comment_summary_data['CommentCount'] / 10))
            for page in range(1, pages):
                result = jd_spider.get_comments_list(page)
                print(result)
