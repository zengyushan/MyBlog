# -*- coding:utf-8 -*-
import os
from app.models import User, Liuyanban, Rizhi, Permission,Role,Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)


def make_shell_context():
    return dict(app=app, db=db, Rizhi=Rizhi, User=User, Liuyanban=Liuyanban,Role=Role,Comment=Comment, Permission=Permission)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)  # 在命令行中，用`db`调用`MigrateCommand
migrate = Migrate(app, db)  # 初始化

if __name__ == '__main__':
    manager.run()
