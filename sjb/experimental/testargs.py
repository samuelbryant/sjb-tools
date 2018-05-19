import argparse
import sys

def build_args():

  p = argparse.ArgumentParser(prog='test1', description='top level argparser')

  sub = p.add_subparsers(dest='command')

  par1 = argparse.ArgumentParser(usage=argparse.SUPPRESS, add_help=False)
  par1.add_argument(
    '--flag1', dest='const1', required=False, help='par 1, flag 1 help')
  par1.add_argument(
    'req1', help='par 1, req 1 help')

  par2 = argparse.ArgumentParser(usage=argparse.SUPPRESS, add_help=False)
  par2.add_argument(
    '--flag2', dest='const2', required=False, help='par 2, flag 2 help')
  par2.add_argument(
    'req2', help='par 2, req 2 help')




  g = p.add_argument_group(title='group title', description='group description')
  g.add_argument('group1', help='group1 help')
  g.add_argument('--grflag', help='group1 flag')

  cmd1 = sub.add_parser('foo', help='sub1 (foo) help')
  cmd2 = sub.add_parser('bar', help='sub2 (bar) help', parents=[par1, par2])
  cmd2.add_argument('barsub', help='bar sub argument')

  return p

def test1():
  p = build_args()
  args = p.parse_args(sys.argv[1:])

if __name__ == '__main__':
  test1()
