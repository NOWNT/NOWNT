from Task import Task
from Test import Test
from User import User
from web import launch_web
from Database import Database
from Task import HttpMethod


class Homepage(Task):
    method = HttpMethod.GET
    endpoint = '/'


class GuestUser(User):
    wait_time = 0
    tasks = [Homepage]


class MonthlyTest(Test):
    tag = "Monthly Test"
    user_map = {
        GuestUser: 20,
    }


duration_seconds = 60
launch_web('127.0.0.1', 5050, MonthlyTest(), Database('database.db'), duration=duration_seconds)
