import os
import timeit

from flask import Flask, flash, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from celery import Celery
from v2s_wrapper import execute_v2s
from v2s.util.general import JSONFileUtils
from result_processing import *

UPLOAD_FOLDER = os.getcwd().strip('flask_application') + 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CELERY_RESULT_BACKEND'] = "redis://localhost:6379/0"
app.config['CELERY_BROKER_URL'] = "redis://localhost:6379/0"

celery = Celery(app.name,
                broker=app.config['CELERY_BROKER_URL'],
                result_backend=app.config['CELERY_BROKER_URL'])


@celery.task(bind=True)
def process_video(self, filepath):
    self.update_state(state='PROCESSING')

    start = timeit.default_timer()
    detected_actions_json = execute_v2s(filepath)
    extracted_actions = extract_action(detected_actions_json)

    file_path, extension = os.path.splitext(filepath)

    # get the hint text for the action
    for i in range(len(extracted_actions)):
        # only do for tap and long tap:
        if extracted_actions[i]["act_type"] != "SWIPE":
            screen = extracted_actions[i]['first_frame'] - 1
            screen_number = f'{screen:04}'
            screen_path = file_path +  f"/extracted_frames/{screen_number}.jpg"

            coordinate = extracted_actions[i]['taps'][0]

            extracted_actions[i]['action_hint'] = get_action_hint(screen_path, coordinate)

    # put the resulting screen ocr result
    for i in range(0, len(extracted_actions)):
        # the result of the last action
        if i == len(extracted_actions) - 1:
            # find the number of total frames in the video
            extracted_frames_dir = file_path  + f"/extracted_frames/"
            total_frames = len([name for name in os.listdir(extracted_frames_dir) if
                                os.path.isfile(os.path.join(extracted_frames_dir, name))])

            first_frame = extracted_actions[i]['first_frame']

            # two seconds after the start of the action, else use the last frame of the video
            if first_frame + 60 > total_frames:
                screen_number = f'{total_frames:04}'
            else:
                screen_number = f'{first_frame+60:04}'

        else:
            # the resulting screen of the first action is the the screen before the second action
            screen_before_next_action = extracted_actions[i+1]['first_frame'] - 1
            screen_number = f'{screen_before_next_action:04}'

        screen_path = file_path +  f"/extracted_frames/{screen_number}.jpg"
        extracted_actions[i]['resulting_screen_ocr'] = ocr(screen_path)

    # self.update_state(result=extracted_actions)
    JSONFileUtils.output_data_to_json(extracted_actions, os.path.join(filepath.rsplit(".", 1)[0], "all_detections.json"))

    duration = timeit.default_timer() - start
    # self.update_state(result=extracted_actions)
    JSONFileUtils.output_data_to_json({"duartion": duration}, os.path.join(filepath.rsplit(".", 1)[0], "duration.json"))
    JSONFileUtils.output_data_to_json(extracted_actions, os.path.join(filepath.rsplit(".", 1)[0], "all_detections.json"))
    return extracted_actions



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            task = process_video.apply_async(args=[filepath])
            return jsonify(202, {'Location': url_for('task_status', task_id=task.id)})

    # return jsonify(202, {'Location': '/testing'})
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


@app.route('/status/<task_id>')
def task_status(task_id):
    task = process_video.AsyncResult(task_id)
    if task.state == 'PENDING':
        # job did not start yet
        response = {
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state
        }
        if task.info is not None:
            response['result'] = task.info
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'status': str(task.info),  # this is the exception raised
        }
    return jsonify(response)


if __name__ == '__main__':
    app.run(host="118.138.31.50", port=5000, debug=True) #CHANGE TO YOUR IPV4 ADDRESS
