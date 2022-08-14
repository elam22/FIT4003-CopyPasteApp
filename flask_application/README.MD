This is the backend of the android application, the android frontend will post the video using http post to the server and the server will process the vide

# How to set up
### Environment
1. create a conda environment with python=3.6.9, higher version should be compatible but not tested yet
2. activate your environment 
3. cd to `\BackendWithV2S\python_v2s`
4. run `pip install .`
5. run `conda install ffmpeg`
6. cd to `\BackendWithV2S\flask_application`
7. run `pip install -r requirements.txt`

### Docker
Needed for redis, which is a database then can save our result
1. Download docker, install needed dependency such as WSL
2. in cmd `docker pull redis`
3. in cmd `docker run -d -p 6379:6379 redis`
4. this will create and start an image of the backend


# How to run
1. activate your environment
2. cd to `\BackendWithV2S\flask_application`
3. in cmd, `flask run`
4. in another cmd, `celery -A app.celery worker --loglevel=INFO --pool=solo` to run celery, which is a task queue system
5. open your docker application
6. find the container that you have created last time for redis, start the image
7. To remove queue task run `celery -A app.celery purge` in cmd.