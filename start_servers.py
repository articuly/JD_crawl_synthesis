import os

if os.name == 'nt':
    os.system('start /b python run_jd_spider.py')
    os.system('start /b python run_jd_analysis.py')
    os.system('start /b flask run -h 127.0.0.1 -p 8000')
else:
    os.system('python run_jd_spider.py&')
    os.system('python run_jd_analysis.py&')
    os.system('flask run -h 127.0.0.1 -p 8000&')
