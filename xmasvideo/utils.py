from functools import wraps
import re
import shutil
import string

from flask import abort, current_app as app, request


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def slugify(text, delim='-'):
    """Generates ASCII-only slug without digits."""
    result = []
    for word in _punct_re.split(text.lower()):
        word = ''.join([i for i in word if i in string.ascii_lowercase])
        if word:
            result.append(word)
    return str(delim.join(result))


def unslugify(text, delim='-'):
    return text.replace(delim, ' ').title()


def cache_flush_password_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not app.config['CACHE_FLUSH_PASSWORD']:
            abort(403)
        if request.form.get('password') != app.config['CACHE_FLUSH_PASSWORD']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def flush_tmp_app_directories():
    try:
        shutil.rmtree(app.config['XMAS_OUTPUT_FOLDER'])
    except FileNotFoundError:
        pass
    app.logger.info('Deleted %s and its contents',
                    app.config['XMAS_OUTPUT_FOLDER'])
    try:
        shutil.rmtree(app.config['XMAS_IMAGE_TXT_FILES_DIR'])
    except FileNotFoundError:
        pass
    app.logger.info('Deleted %s and its contents',
                    app.config['XMAS_IMAGE_TXT_FILES_DIR'])
    try:
        shutil.rmtree(app.config['XMAS_VIDEOS_IMAGES_DIR'])
    except FileNotFoundError:
        pass
    app.logger.info('Deleted %s and its contents',
                    app.config['XMAS_VIDEOS_IMAGES_DIR'])


def apply_acronyms_to_title(title):
    acronyms_original = app.config['ACRONYMS']
    acronyms_upper = [acronym.upper() for acronym in acronyms_original]
    new_title = []
    for title_part in title.split():
        try:
            index = acronyms_upper.index(title_part.upper())
            new_title.append(acronyms_original[index])
        except ValueError:
            new_title.append(title_part)
    return ' '.join(new_title)
