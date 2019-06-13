import os
from flask import Flask
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                        os.path.join(basedir, 'data-test.sqlite')
manager = Manager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return '<%r followed %r>' % (self.follower.name, self.followed.name)
    

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    """
    In [10]: print(u1.followed)
    SELECT follows.follower_id AS follows_follower_id, follows.followed_id AS follows_followed_id, follows.timestamp AS follows_timestamp, users_1.id AS users_1_id, users_1.name AS users_1_name, users_2.id AS users_2_id, users_2.name AS users_2_name
    FROM follows LEFT OUTER JOIN users AS users_1 ON users_1.id = follows.follower_id LEFT OUTER JOIN users AS users_2 ON users_2.id = follows.followed_id
    WHERE ? = follows.follower_id
    """
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    """
    In [9]: print(u1.followers)
    SELECT follows.follower_id AS follows_follower_id, follows.followed_id AS follows_followed_id, follows.timestamp AS follows_timestamp, users_1.id AS users_1_id, users_1.name AS users_1_name, users_2.id AS users_2_id, users_2.name AS users_2_name
    FROM follows LEFT OUTER JOIN users AS users_1 ON users_1.id = follows.follower_id LEFT OUTER JOIN users AS users_2 ON users_2.id = follows.followed_id
    WHERE ? = follows.followed_id
    """
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    
    def __repr__(self):
        return '<User %r>' % self.name
    

def make_shell_context():
    return dict(app=app, db=db, User=User, Follow=Follow)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test():
    u = [User(name='u%d' % (i + 1)) for i in range(5)]
    db.session.add_all(u)
    db.session.commit()
    for i in range(5):
        for j in range(i + 1, 5):
            db.session.add(Follow(follower=u[i], followed=u[j]))
    db.session.commit()
    
    for i in User.query.all():
        print(i)
    
    for j in Follow.query.all():
        print(j)
            
if __name__ == '__main__':
    manager.run()