import pandas as pd
import pandas_profiling as pp

# import logging.config
# from config.logging_config import logging_config

from .app_config import config_wrapper
from .config import config_reader
from configparser import NoSectionError
from .database.db import db

from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user

from .forms.login_form import LoginForm
from .forms.parameters_form import GeneralParamForm
from .forms.register import RegisterForm
from .forms.upload_user import UploadUserForm
from .forms.upload_form import NewTabularFileForm, GenerateDataSet, UploadImageForm

from functools import wraps

from .generator.simulator import parse
from .core.session import Session
from .core.thread_handler import ThreadHandler

from .utils import db_ops, config_ops
from .utils.custom import save_local_model
from .utils.feature_util import get_tabular_graphs, get_image_graphs, save_image_graphs, get_summary, save_summary
from .utils.local_utils import *
from .utils.metrics import *
from .utils.param_utils import get_params
from .utils.request_util import *
from .utils.upload_util import get_examples, new_config

from .database.user import User

WTF_CSRF_SECRET_KEY = os.urandom(42)
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)
appConfig = config_wrapper.ConfigApp()

Bootstrap(app)
app.secret_key = WTF_CSRF_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = appConfig.database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = appConfig.track_modifications()
app.config['JSON_SORT_KEYS'] = appConfig.json_sort_keys()

USER_ROOT = appConfig.user_root() if appConfig.user_root() is not None else APP_ROOT

th = ThreadHandler()
login_manager = LoginManager()
login_manager.init_app(app)


def check_config(func):
    @wraps(func)
    def check_session(*args, **kwargs):
        if 'token' in request.form and 'token' in session:
            if session['token'] != request.form['token']:
                return redirect(url_for('login'))
        return func(*args, **kwargs)

    return check_session


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if not db_ops.checklogin(form, login_user, session, sess, USER_ROOT):
            # app.logger.warn('Login attempt to %s from IP %s', form.username.data, request.remote_addr)
            return render_template('login.html', form=form, error='Invalid username or password')
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    form = RegisterForm()
    username = session['user']
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('signup.html', form=form, error="Passwords are not equals", user=username,
                                   token=session['token'])
        if not db_ops.sign_up(form):
            return render_template('signup.html', form=form, error="Username already exists", user=username,
                                   token=session['token'])
        return render_template('login.html', form=LoginForm(), token=session['token'])
    return render_template('signup.html', form=form, user=username, token=session['token'])


@app.route('/user_data', methods=['GET', 'POST'])
@login_required
def user_data():
    username = session['user']
    form = UploadUserForm()
    if form.validate_on_submit():
        email = form.email.data
        db_ops.update_user(username, email)
    db_ops.get_user_data(username, form)
    _, param_configs = config_ops.get_configs_files(USER_ROOT, username)
    user_dataset = config_ops.get_datasets_type(USER_ROOT, username)
    return render_template('upload_user.html', form=form, user=username, token=session['token'],
                           datasets=user_dataset, parameters=param_configs)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    username = session['user']
    return render_template('dashboard.html', title='Dashboard', user=username,
                           user_configs=config_ops.get_datasets(USER_ROOT, username), token=session['token'])


@app.route('/tensorboard', methods=['GET', 'POST'])
@login_required
def tensorboard():
    username = session['user']
    port = ''
    running, config_file = th.check_running(username)
    if not running:
        config_file = sess.get_config_file() if sess.check_key('config_file') else None
    if config_file is not None:
        try:
            sess.set_config_file(config_file)
            sess.load_config()
            port = th.get_port(username, sess.get_config_file())
        except:
            pass
    return render_template('tensorboard.html', title='Tensorboard', user=username,
                           user_configs=config_ops.get_datasets(USER_ROOT, username), token=session['token'], port=port)


@app.route('/upload_tabular', methods=['GET', 'POST'])
@login_required
def upload_tabular():
    username = session['user']
    examples = get_examples()
    form = NewTabularFileForm()
    if form.validate_on_submit():
        try:
            dataset_name = config_ops.new_config(form.data['train_file'], form.data['test_file'], USER_ROOT, username)
            return jsonify(status='ok', msg=dataset_name)
        except Exception as e:
            return jsonify(status='error', msg=str(e))
    return render_template('upload_tabular.html', token=session['token'], form=form,
                           datasets=config_ops.get_datasets(USER_ROOT, username), examples=examples,
                           gen_form=GenerateDataSet(), data_types=config_ops.get_datasets_type(USER_ROOT, username))


@app.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    username = session['user']
    form = UploadImageForm()
    if form.validate_on_submit():
        option_selected = form.selector.data['selector']
        file = form[option_selected].data['file']
        try:
            dataset_name = config_ops.new_image_dataset(USER_ROOT, username, option_selected, file)
            return jsonify(status='ok', msg=dataset_name)
        except Exception as e:
            return jsonify(status='error', msg=str(e))
    return render_template('upload_image.html', token=session['token'],
                           data_types=config_ops.get_datasets_type(USER_ROOT, username), form=form)


@app.route('/data_graphs', methods=['POST', 'GET'])
@login_required
@check_config
def data_graphs():
    dataset_name = get_datasetname(request)
    data = get_tabular_graphs(USER_ROOT, session['user'], dataset_name)
    return jsonify(**data)


@app.route('/tabular_profile', methods=['POST', 'GET'])
@login_required
@check_config
def tabular_profile():
    dataset_name = get_datasetname(request)
    main_path = sys_ops.get_dataset_path(USER_ROOT, session['user'], dataset_name)
    if not os.path.isfile(os.path.join(main_path, 'profile.html')):
        df = pd.read_csv(os.path.join(main_path, dataset_name + '.csv'))
        profile = pp.ProfileReport(df)
        profile.to_file(outputfile=os.path.join(main_path, 'profile.html'))
    with open(os.path.join(main_path, 'profile.html'), 'r') as prof:
        profile = prof.read()
    return jsonify(data=profile)


@app.route('/image_graphs', methods=['POST', 'GET'])
@login_required
@check_config
def image_graphs():
    username = session['user']
    dataset_name = get_datasetname(request)
    data = get_image_graphs(USER_ROOT, username, dataset_name)
    if data is None:
        local_sess = Session(app, appConfig)
        local_sess.add_user((username, session['_id']))
        new_config(dataset_name, username, local_sess, USER_ROOT, appConfig)
        data = {'data': local_sess.get_helper().get_data()}
        save_image_graphs(USER_ROOT, username, dataset_name, data)
    return jsonify(**data)


@app.route('/gui', methods=['GET', 'POST'])
@login_required
def gui():
    username = session['user']
    _, param_configs = config_ops.get_configs_files(USER_ROOT, username)
    user_dataset = config_ops.get_datasets_and_types(USER_ROOT, username)
    return render_template('gui.html', user=username, token=session['token'], user_dataset=user_dataset,
                           dataset_params={}, data=None, parameters=param_configs, cy_model=[],
                           model_name='new_model', num_outputs=None, error=False)


@app.route('/gui_load', methods=['POST'])
@login_required
@check_config
def gui_load():
    local_sess = Session(app, appConfig)
    username = session['user']
    local_sess.add_user((username, session['_id']))
    _, param_configs = config_ops.get_configs_files(USER_ROOT, username)
    user_dataset = config_ops.get_datasets_and_types(USER_ROOT, username)
    model_name = get_model(request)
    local_sess.set_config_file(sys_ops.get_config_path(USER_ROOT, username, model_name))
    if local_sess.load_config():
        hlp = local_sess.get_helper()
        return render_template('gui.html', token=session['token'], user=username, user_dataset=user_dataset,
                               parameters=param_configs, dataset_params=hlp.get_dataset_params(), data=hlp.get_data(),
                               cy_model=sys_ops.load_cy_model(model_name, username), model_name=model_name,
                               num_outputs=hlp.get_num_outputs(), error=False)
    return render_template('gui.html', token=session['token'], user=username, user_dataset=user_dataset,
                           dataset_params={}, data=None, parameters=param_configs, cy_model=[], model_name='new_model',
                           num_outputs=None, error=True)


@app.route('/gui_select_data', methods=['POST'])
@login_required
@check_config
def gui_select_data():
    username = session['user']
    dataset_name = get_dataset(request)
    local_sess = Session(app, appConfig)
    local_sess.add_user((username, session['_id']))
    data = get_summary(USER_ROOT, username, dataset_name)
    if data is None:
        new_config(dataset_name, username, local_sess, USER_ROOT, appConfig)
        data = local_sess.get_helper().get_data()
        save_summary(USER_ROOT, username, dataset_name, data)
    return jsonify(data=data)


@app.route('/gui_input', methods=['POST'])
@login_required
@check_config
def gui_input():
    local_sess = Session(app, appConfig)
    username = session['user']
    local_sess.add_user((username, session['_id']))
    dataset_name = get_dataset(request)
    new_config(dataset_name, username, local_sess, USER_ROOT, appConfig)
    hlp = local_sess.get_helper()
    hlp.set_split(get_split(request))
    result = hlp.process_targets_request(request)
    return jsonify(**result)


@app.route('/save_model', methods=['GET', 'POST'])
@login_required
@check_config
def save_model():
    local_sess = Session(app, appConfig)
    username = session['user']
    local_sess.add_user((username, session['_id']))
    dataset_name = get_dataset(request)
    new_config(dataset_name, username, local_sess, USER_ROOT, appConfig)
    hlp = local_sess.get_helper()
    hlp.set_split(get_split(request))
    local_sess = save_local_model(local_sess, request, USER_ROOT, username)
    config_ops.define_new_model(USER_ROOT, username, local_sess.get_writer(), local_sess.get_model_name())
    local_sess.write_params()
    return jsonify(explanation='ok')


@app.route('/params_run', methods=['POST'])
@login_required
@check_config
def params_run():
    model_name = get_model_name(request)
    username = session['user']
    log_mess = sys_ops.get_log_mess(username, model_name)
    try:
        config_file = sys_ops.get_config_path(USER_ROOT, username, model_name)
        parameters = get_params(config_file, appConfig)
        sess.set_config_file(config_file)
        sess.load_config()
        sess.set_model_name(model_name)
        export_dir = config_reader.read_config(sess.get_config_file()).export_dir()
        checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
        metric = sess.get_metric()
        graphs = train_eval_graphs(config_reader.read_config(sess.get_config_file()).checkpoint_dir())
        return jsonify(checkpoints=checkpoints, parameters=parameters, metric=metric, graphs=graphs, log=log_mess)
    except (KeyError, NoSectionError):
        model_name, checkpoints, metric, graphs, log_mess = run_utils.define_empty_run_params()
        return jsonify(checkpoints=checkpoints, parameters={}, metric=metric, graphs=graphs, log=log_mess)


@app.route('/params_predict', methods=['POST'])
@login_required
@check_config
def params_predict():
    try:
        local_sess = Session(app, appConfig)
        hlp = load_local_sess(local_sess, request, session['user'], session['_id'], USER_ROOT)
        export_dir = config_reader.read_config(local_sess.get_config_file()).export_dir()
        checkpoints = run_utils.get_eval_results(export_dir, local_sess.get_writer(), local_sess.get_config_file())
        metric = local_sess.get_metric()
        params, _ = hlp.get_default_data_example()
        has_test = hlp.has_split_test()
        return jsonify(checkpoints=checkpoints, metric=metric, params=params, has_test=has_test)
    except (KeyError, NoSectionError):
        return jsonify(checkpoints='', metric='', params={})


@app.route('/run', methods=['GET', 'POST'])
@login_required
@check_config
def run():
    username = session['user']
    _, model_configs = config_ops.get_configs_files(USER_ROOT, username)
    user_datasets = config_ops.get_datasets_and_types(USER_ROOT, username)
    form = GeneralParamForm()
    running, model_name, checkpoints, metric, graphs, log_mess = run_utils.load_run_config(sess, th, username, form)
    if request.method == 'POST':
        all_params_config = run_utils.run_post(sess, request, USER_ROOT, username, th)
        th.handle_request(get_action(request), all_params_config, username, get_resume_from(request),
                          sess.get_config_file())
        return jsonify(status='ok', metric=sess.get_metric())
    form.update(appConfig)
    return render_template('run.html', user=username, token=session['token'], form=form,
                           user_models=model_configs, dataset_params=user_datasets, running=running,
                           model_name=model_name, checkpoints=checkpoints, metric=metric, graphs=graphs, log=log_mess)


@app.route('/predict', methods=['POST', 'GET'])
@login_required
@check_config
def predict():
    username = session['user']
    if request.method == 'POST':
        modelname = get_modelname(request)
        local_sess = Session(app, appConfig)
        hlp, all_params_config = generate_local_sess(local_sess, request, username, session['_id'], USER_ROOT)
        new_features = hlp.get_new_features(request, default_features=False)
        set_canned_data(username, modelname, USER_ROOT, all_params_config)
        final_pred, success = th.predict_estimator(all_params_config, new_features)
        return jsonify(error=final_pred) if not success else jsonify(
            run_utils.get_predictions(hlp.get_targets(), final_pred))
    _, param_configs = config_ops.get_configs_files(USER_ROOT, username)
    return render_template('predict.html', user=username, token=session['token'], parameters=param_configs)


@app.route('/explain', methods=['POST', 'GET'])
@login_required
@check_config
def explain():
    username = session['user']
    if request.method == 'POST':
        local_sess = Session(app, appConfig)
        hlp, all_params_config = generate_local_sess(local_sess, request, username, session['_id'], USER_ROOT)
        ep = hlp.process_explain_request(request)
        if 'explanation' in ep:
            return jsonify(**ep)
        set_canned_data(username, get_modelname(request), USER_ROOT, all_params_config)
        result, success = th.explain_estimator(all_params_config, ep)
        if success:
            result = hlp.explain_return(request, result)
            return jsonify(**result)
        return jsonify(error=result)
    _, param_configs = config_ops.get_configs_files(USER_ROOT, username)
    return render_template('explain.html', user=username, token=session['token'], parameters=param_configs)


@app.route('/upload_test_file', methods=['POST', 'GET'])
@login_required
@check_config
def upload_test_file():
    local_sess = Session(app, appConfig)
    hlp = load_local_sess(local_sess, request, session['user'], session['_id'], USER_ROOT)
    result = hlp.test_upload(request)
    return jsonify(result=result)


@app.route('/test', methods=['POST', 'GET'])
@login_required
@check_config
def test():
    username = session['user']
    if request.method == 'POST':
        local_sess = Session(app, appConfig)
        hlp, all_params_config = generate_local_sess(local_sess, request, username, session['_id'], USER_ROOT)
        test_output = process_test_request(local_sess, hlp, all_params_config, username, USER_ROOT, request, th)
        return jsonify(**test_output)
    _, param_configs = config_ops.get_configs_files(USER_ROOT, username)
    return render_template('test.html', user=username, token=session['token'], parameters=param_configs)


@app.route('/delete', methods=['POST'])
@login_required
@check_config
def delete():
    all_params_config = config_reader.read_config(sess.get_config_file())
    export_dir = all_params_config.export_dir()
    del_id = get_delete_id(request)
    paths = [del_id] if del_id != 'all' else [d for d in os.listdir(export_dir) if
                                              os.path.isdir(os.path.join(export_dir, d))]
    sys_ops.delete_recursive(paths, export_dir)
    if len([i for i in os.listdir(export_dir) if os.path.isdir(os.path.join(export_dir, i))]) == 0:
        sys_ops.tree_remove(all_params_config.checkpoint_dir())
    checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
    return jsonify(checkpoints=checkpoints)


@app.route('/delete_model', methods=['POST'])
@login_required
@check_config
def delete_model():
    username = session['user']
    sys_ops.delete_models(get_all(request), [get_model(request)], username)
    _, models = config_ops.get_configs_files(USER_ROOT, username)
    datasets = config_ops.get_datasets_type(USER_ROOT, username)
    return jsonify(datasets=datasets, models=models, data_types=config_ops.get_datasets_type(USER_ROOT, username))


@app.route('/delete_test_file', methods=['POST'])
@login_required
@check_config
def delete_test_file():
    username = session['user']
    _, param_configs = config_ops.get_configs_files(USER_ROOT, username)
    error, mess = sys_ops.delete_file_test(request, param_configs, USER_ROOT, username)
    return jsonify(error=error, mess=mess)


@app.route('/delete_dataset', methods=['POST'])
@login_required
@check_config
def delete_dataset():
    username = session['user']
    sys_ops.delete_dataset(get_all(request), get_dataset(request), get_models(request), username)
    _, models = config_ops.get_configs_files(USER_ROOT, username)
    datasets = config_ops.get_datasets(USER_ROOT, username)
    return jsonify(datasets=datasets, models=models, data_types=config_ops.get_datasets_type(USER_ROOT, username))


@app.route('/refresh', methods=['GET'])
@login_required
@check_config
def refresh():
    running, config_file = th.check_running(session['user'])
    sess.run_or_pause(running)
    try:
        hlp = sess.get_helper()
        all_params_config = config_reader.read_config(sess.get_config_file())
        epochs = run_utils.get_step(hlp.get_train_size(), all_params_config.train_batch_size(),
                                    all_params_config.checkpoint_dir())
        export_dir = all_params_config.export_dir()
        checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
        graphs = train_eval_graphs(all_params_config.checkpoint_dir())
        log = sess.get('log_fp').read() if sess.check_key('log_fp') else ''
        return jsonify(checkpoints=checkpoints, log=log, running=running, epochs=epochs, graphs=graphs)
    except (KeyError, NoSectionError):
        return jsonify(checkpoints='', log='', running=running, epochs=0, graphs={})


@app.route('/running_check', methods=['GET'])
@login_required
@check_config
def running_check():
    running, config_file = th.check_running(session['user'])
    epochs = 0
    model_name = ''
    sess.run_or_pause(running)
    if running:
        if config_file is not None and not sess.check_key('config_file'):
            sess.set_config_file(config_file)
            sess.load_config()
            sess.set_model_name(model_name)
        try:
            config_file = sess.get_config_file()
            hlp = sess.get_helper()
            all_params_config = config_reader.read_config(sess.get_config_file())
            epochs = run_utils.get_step(hlp.get_train_size(), all_params_config.train_batch_size(),
                                        all_params_config.checkpoint_dir())
            model_name = config_file.split('/')[-2]
        except (KeyError, NoSectionError):
            pass
    return jsonify(running=running, epochs=epochs, model_name=model_name)


@app.route('/generate', methods=['GET', 'POST'])
@login_required
@check_config
def generate():
    dataset_name = get_datasetname(request)
    script = get_script(request)
    main_path = sys_ops.get_dataset_path(USER_ROOT, session['user'], dataset_name)
    try:
        parse(script, main_path, dataset_name)
        sys_ops.create_split_folders(main_path)
        return jsonify(valid=str(True))
    except Exception as e:
        return jsonify(valid=str(e))


@app.route("/default_prediction", methods=['GET', 'POST'])
@login_required
@check_config
def default_prediction():
    username = session['user']
    local_sess = Session(app, appConfig)
    hlp = load_local_sess(local_sess, request, username, session['_id'], USER_ROOT)
    all_params_config = config_reader.read_config(local_sess.get_config_file())
    export_dir = all_params_config.export_dir()
    checkpoints = run_utils.get_eval_results(export_dir, local_sess.get_writer(), local_sess.get_config_file())
    metric = local_sess.get_metric()
    if len(checkpoints) == 0:
        return jsonify(checkpoints={}, metric=metric)
    checkpoint = run_utils.ckpt_to_table(checkpoints)['Model'].values[-1]
    all_params_config = run_utils.create_result_parameters(request, local_sess, checkpoint=checkpoint)
    new_features = hlp.get_new_features(None, default_features=True)
    sys_ops.get_canned_data(USER_ROOT, username, get_modelname(request), all_params_config)
    pred, success = th.predict_estimator(all_params_config, new_features, all=True)
    if not success:
        return jsonify(error=pred)

    example = hlp.generate_rest_call(pred)
    return jsonify(example=example, checkpoints=checkpoints, metric=metric)


@app.route("/deploy", methods=['GET', 'POST'])
@login_required
@check_config
def deploy():
    username = session['user']
    if request.method == 'POST' and 'model_name' in request.form:
        local_sess = Session(app, appConfig)
        local_sess.add_user((username, session['_id']))
        model_name = get_modelname(request)  # request.form['model_name']
        config_path = sys_ops.get_config_path(USER_ROOT, username, model_name)
        all_params_config = config_reader.read_config(config_path)
        file_path = sys_ops.export_models(all_params_config.export_dir(), request.form['selected_rows'], model_name)
        return send_file(file_path, mimetype='application/zip', attachment_filename=file_path.split('/')[-1],
                         as_attachment=True)
    _, param_configs = config_ops.get_configs_files(USER_ROOT, username)
    return render_template('deploy.html', user=username, token=session['token'], parameters=param_configs)


@app.errorhandler(401)
def unauthorized(e):
    return render_template('error.html', error=e.name, number=e.code, message=e.description)


@app.errorhandler(404)
def notfound(e):
    return render_template('error.html', error=e.name, number=e.code, message=e.description)


@app.errorhandler(405)
def notallowed(e):
    return render_template('error.html', error=e.name, number=e.code, message=e.description)


@app.route('/')
def main():
    return redirect(url_for('login'))


# def flash_errors(form):
#     for field, errors in form.errors.items():
#         for error in errors:
#             flash(u"%s" % error)


db.init_app(app)

sess = Session(app, appConfig)

if __name__ == '__main__':
    app.run(debug=appConfig.debug(),
            threaded=appConfig.threaded(),
            host=appConfig.host(),
            port=appConfig.port())
