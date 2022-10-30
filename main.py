from core.instances.Table import Table

class Settings:
    INPUT = r'Input\sample1.xls'

CONFIGS = Settings()

def main():
    input = Table(CONFIGS.INPUT)

if __name__ == '__main__':
    main()