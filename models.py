from extensions import db


class GoodsInfo(db.Model):
    goods_id = db.Column(db.Integer, primary_key=True)
    goods_name = db.Column(db.String(200))
    goods_price = db.Column(db.Float)
    update = db.Column(db.DateTime)
    can_analysis = db.Column(db.Boolean)
    analysis_date = db.Column(db.DateTime)


class GoodsCommentsSummary(db.Model):
    goods_id = db.Column(db.Integer, primary_key=True)
    default_good_count = db.Column(db.Integer)
    comment_count = db.Column(db.Integer)
    good_count = db.Column(db.Integer)
    good_rate = db.Column(db.Float)
    general_count = db.Column(db.Integer)
    general_rate = db.Column(db.Float)
    pool_count = db.Column(db.Integer)
    pool_rate = db.Column(db.Float)
    score_1_count = db.Column(db.Integer)
    score_2_count = db.Column(db.Integer)
    score_3_count = db.Column(db.Integer)
    score_4_count = db.Column(db.Integer)
    score_5_count = db.Column(db.Integer)


class GoodsComments(db.Model):
    comment_id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, index=True)
    content = db.Column(db.String(500))
    create_time = db.Column(db.DateTime)
    score = db.Column(db.Integer)
    user_client = db.Column(db.Integer)
