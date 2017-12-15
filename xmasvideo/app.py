import os

from flask import abort, Flask, redirect, render_template, request, url_for

from .convert import pick_images, images_to_video
from .s3 import upload_mp4_video_to_s3, get_s3_file_public_url
from .utils import slugify


app = Flask(__name__)
app.config.from_object("xmasvideo.config")


@app.route('/')
def index():
    return render_template('hello.html')


@app.route('/', methods=['POST'])
def create():
    message = request.form.get('message')
    message = slugify(message)
    if not message:
        return redirect(url_for('index'))
    images = pick_images(message)
    video_path = images_to_video(message, images)
    video_filename = os.path.split(video_path)[1]
    if not get_s3_file_public_url(video_filename):
        upload_mp4_video_to_s3(video_path, video_filename)
    else:
        app.logger.info('%s exists on S3, skipping upload.', video_filename)
    return redirect(url_for('video', name=video_filename, message=message))


@app.route('/video/<message>/<name>')
def video(message, name):
    s3_video_url = get_s3_file_public_url(name)
    if not s3_video_url:
        app.logger.info('%s does not exist on S3', name)
        abort(404)
    return render_template('video.html', video_url=s3_video_url,
                           message=message)