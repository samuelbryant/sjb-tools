import os,textwrap,sys

def display_todo(todo):
  print('%-3d %s' % (todo.id, todo.text))

def display_todos(todo_list):
  for todo in todo_list:
    display_todo(todo)
