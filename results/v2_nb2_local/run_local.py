import sys

def main():
    g = {'__name__': 'nb'}
    exec(compile(open(__file__.replace('run_local.py','body.py'),encoding='utf-8').read(),'body','exec'), g)

if __name__ == '__main__':
    main()
