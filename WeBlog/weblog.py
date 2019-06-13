# -*- coding:utf-8 -*-
import os

COV = None
if os.environ.get('WEBLOG_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from app import create_app, db
from app.models import User, Role, Post, Permission, Comment


app = create_app(os.getenv('WEBLOG_CONFIG') or 'default')
migrate = Migrate(app, db)
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Post=Post, Permission=Permission, Comment=Comment)

manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)

@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('WEBLOG_COVERAGE'):
        import sys
        os.environ['WEBLOG_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    import tests.test_client
    tests = unittest.TestLoader().discover('tests') #.loadTestsFromName('tests.test_client')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()

@manager.command
def generate_fake():
    from app.fake import generate_fake_comments, generate_fake_posts, generate_fake_users
    generate_fake_comments()
    generate_fake_posts()
    generate_fake_users()

@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
        profile_dir=profile_dir)
    app.run()

@manager.command
def deploy():
    """Run deployment tasks."""
    from flask_migrate import upgrade
    from app.models import Role, User
    # 把数据库迁移到最新修订版本
    upgrade()
    # 创建用户角色
    Role.insert_roles()
    # 让所有用户都关注此用户
    User.add_self_follows()

if __name__ == '__main__':
    manager.run()

'''
test command for REST API.
~~~

http --json --auth <email>:<password> GET http://127.0.0.1:5000/api/v1.0/posts/

http --json --auth : GET 'http://127.0.0.1:5000/api/v1.0/posts/?page=1'

http --auth <email>:<password> --json POST http://127.0.0.1:5000/api/v1.0/posts/ "body=I'm adding a post from the *command line*."

http --auth <email>:<password> --json GET http://127.0.0.1:5000/api/v1.0/token

http --json --auth eyJpYXQ...: GET http://127.0.0.1:5000/api/v1.0/posts/

'''