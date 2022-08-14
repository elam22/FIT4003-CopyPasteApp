from os.path import join
from glob import glob

from setuptools import setup, find_packages, Extension

with open('README.md') as readme_file:
    README = readme_file.read()

# with open('HISTORY.md') as history_file:
#     HISTORY = history_file.read()

setup_args = dict(
    name='v2s',
    version='4.0',
    description='Video2Scenario',
    long_description=README,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    data_files=[('v2s', [join('v2s','v2s_config.json'), join('v2s','device_config.json'), join('v2s', 'app_config.json')]),
                (join('v2s', 'app_apks'), glob(join('v2s', 'app_apks','*.apk'))),
                (join('v2s', 'phase1', 'detection', 'opacity_model'), [join('v2s', 'phase1', 'detection', 'opacity_model', 'model-saved-alex8-tuned.h5')]),
                (join('v2s', 'phase1', 'detection', 'touch_model'),[join('v2s', 'phase1', 'detection', 'touch_model', 'v2s_label_map.pbtxt')]),
                (join('v2s', 'phase1', 'detection', 'touch_model', 'saved_model_n5'), [join('v2s', 'phase1', 'detection', 'touch_model', 'saved_model_n5', 'frozen_inference_graph_n5.pb'), join('v2s', 'phase1', 'detection', 'touch_model', 'saved_model_n5', 'saved_model.pb')]),
                (join('v2s', 'phase1', 'detection', 'touch_model', 'saved_model_n6p'), [join('v2s', 'phase1', 'detection', 'touch_model', 'saved_model_n6p', 'frozen_inference_graph_n6.pb'), join('v2s', 'phase1', 'detection', 'touch_model', 'saved_model_n5', 'saved_model.pb')]),
                (join('v2s', 'phase1', 'detection', 'touch_model', 'saved_model_n7'), [join('v2s', 'phase1', 'detection', 'touch_model', 'saved_model_n7', 'saved_model.pb')]),
                (join('v2s', 'phase3', 'reran'), [join('v2s', 'phase3', 'reran', 'replay-arm'), 
                join('v2s', 'phase3', 'reran', 'replay-i686'), join('v2s', 'phase3', 'reran', 'replay.c')])],
    author='SEMERU',
    author_email='charlyb@gmail.com',
    keywords=['v2s', 'Video2Scenario', 'android'],
    scripts=[join('v2s', 'bin','exec_v2s')],
    url='https://gitlab.com/SEMERU-Code/Android/Video2Sceneario/',
    download_url='https://pypi.org/project/v2s/',
    python_requires='>=3.8.0'
)

install_reqs = [
    'ffmpeg',
    'ffmpeg-python',
    'Keras==2.2.4',
    'Keras-Applications==1.0.8',
    'Keras-Preprocessing==1.1.0',
    'matplotlib==3.1.1',
    'numpy>=1.20.2',
    'Pillow==6.2.0',
    'scipy==1.3.1',
    'tensorboard>=2.0.0',
    'tensorflow>=2.0.0',
    'tensorflow-mac-os'
]

if __name__ == '__main__':
    setup(**setup_args, install_requires=install_reqs)
