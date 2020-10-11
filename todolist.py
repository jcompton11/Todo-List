from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker

from datetime import datetime as dt
from datetime import timedelta as td

engine = create_engine('sqlite:///todo.db?check_same_thread=False')

Base = declarative_base()

today = dt.today()


class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True)
    task = Column(String, default='Nothing to do!')
    deadline = Column(Date, default=today)

    def __repr__(self):
        return self.task


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def add_task():
    what_to_do = input("\nEnter task\n")
    deadline = input("Enter deadline\n")

    dt_obj = dt.strptime(deadline, '%Y-%m-%d')
    new_row = Task(task=what_to_do, deadline=dt_obj)
    session.add(new_row)
    session.commit()
    print("The task has been added!")


def delete_task():
    rows = session.query(Task).filter(Task.deadline <= today.date()).all()

    print("Choose the number of the tasks you want to delete:")
    print_all_tasks(rows, nothing_to_delete=True)

    choice = int(input().strip())
    if rows:
        specific_row = rows[choice - 1]

        session.delete(specific_row)
        session.commit()


def print_tasks(rows, **options):
    opt_today_format = options.get("today")
    opt_week_format = options.get("week")

    if opt_today_format:
        print(opt_today_format)
    elif opt_week_format:
        print(opt_week_format)

    if rows:
        for i in range(len(rows)):
            print(f"{i + 1}. {rows[i].task}")
    else:
        print("Nothing to do!")


def print_all_tasks(rows, tasks_not_missed=False, nothing_to_delete=False):
    if rows:
        for row in rows:
            print(f"{row.id}. {row.task}. {row.deadline.day} {row.deadline.strftime('%b')}")
    else:
        if tasks_not_missed:
            print("Nothing is missed!")
        elif nothing_to_delete:
            print("Nothing to delete")
        else:
            print("Nothing to do!")


def todays_tasks():
    rows = session.query(Task).filter(Task.deadline == today.date()).all()

    print_tasks(rows, today=f"\nToday {today.day} {today.strftime('%b')}:")


def weeks_tasks():
    day_obj = today.date()
    end_date = today + td(days=7)
    end = end_date.date()

    while day_obj != end:
        rows = session.query(Task).order_by(Task.deadline).filter(Task.deadline == day_obj).all()
        print_tasks(rows, week=f"\n{day_obj.strftime('%A')} {day_obj.day} {day_obj.strftime('%b')}:")
        day_obj = day_obj + td(days=1)


def missed_tasks():
    rows = session.query(Task).filter(Task.deadline < today.date()).all()

    print("Missed Tasks:")
    print_all_tasks(rows, tasks_not_missed=True)


def all_tasks():
    print("\nAll tasks:")
    rows = session.query(Task).order_by(Task.deadline).all()

    print_all_tasks(rows)


def main():
    prompt = """
1) Today's tasks
2) Week's tasks
3) All tasks
4) Missed tasks
5) Add task
6) Delete task
0) Exit"""
    print(prompt)

    choice = input().strip()

    if choice == "1":
        todays_tasks()
    elif choice == "2":
        weeks_tasks()
    elif choice == "3":
        all_tasks()
    elif choice == "4":
        missed_tasks()
    elif choice == "5":
        add_task()
    elif choice == "6":
        delete_task()
    elif choice == "0":
        print("\nBye!")
        exit(0)


if __name__ == "__main__":
    while True:
        main()
