import json
import os
import pandas as pd
from configparser import NoSectionError
from forms.deploy_form import DeploymentForm
from forms.parameters_form import GeneralParamForm
from forms.upload_user import UploadUserForm
from utils import run_utils, upload_util, db_ops, param_utils, config_ops, sys_ops
from config import config_reader
from database.db import db
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user
from forms.login_form import LoginForm
from forms.register import RegisterForm
from forms.upload_form import NewTabularFileForm, GenerateDataSet, UploadImageForm

from user import User
from thread_handler import ThreadHandler
from session import Session
from utils.request_util import *
from utils.visualize_util import get_norm_corr
from functools import wraps
from generator.simulator import parse
from utils.metrics import *
from utils import custom

SAMPLE_DATA_SIZE = 5
WTF_CSRF_SECRET_KEY = os.urandom(42)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__)

Bootstrap(app)
app.secret_key = WTF_CSRF_SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///username.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JSON_SORT_KEYS'] = False

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
        if not db_ops.checklogin(form, login_user, session, sess):
            return render_template('login.html', form=form, error='Invalid username or password')
        return redirect(url_for('dashboard'))
    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
@login_required
def signup():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password2.data:
            return render_template('signup.html', form=form, error="Passwords are not equals", user=session['user'])
        if not db_ops.sign_up(form):
            return render_template('signup.html', form=form, error="Username already exists", user=session['user'])
        return render_template('login.html', form=LoginForm())
    return render_template('signup.html', form=form, user=session['user'])


@app.route('/user_data', methods=['GET', 'POST'])
@login_required
def user_data():
    username = session['user']
    form = UploadUserForm()
    if form.validate_on_submit():
        email = form.email.data
        db_ops.update_user(username, email)
    db_ops.get_user_data(username, form)
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    user_dataset = config_ops.get_datasets_type(APP_ROOT, username)
    return render_template('upload_user.html', form=form, user=session['user'], token=session['token'],
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
                           user_configs=config_ops.get_datasets(APP_ROOT, username), token=session['token'])


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
                           user_configs=config_ops.get_datasets(APP_ROOT, username), token=session['token'], port=port)


@app.route('/upload_tabular', methods=['GET', 'POST'])
@login_required
def upload_tabular():
    username = session['user']
    examples = upload_util.get_examples()
    form = NewTabularFileForm()
    if form.validate_on_submit():
        try:
            dataset_name = config_ops.new_config(form.data['train_file'], form.data['test_file'], APP_ROOT, username)
            return jsonify(status='ok', msg=dataset_name)
        except Exception as e:
            return jsonify(status='error', msg=str(e))
    return render_template('upload_tabular.html', token=session['token'], form=form,
                           datasets=config_ops.get_datasets(APP_ROOT, username), examples=examples,
                           gen_form=GenerateDataSet(), data_types=config_ops.get_datasets_type(APP_ROOT, username))


@app.route('/upload_image', methods=['GET', 'POST'])
@login_required
def upload_image():
    username = session['user']
    form = UploadImageForm()
    if form.validate_on_submit():
        option_selected = form.selector.data['selector']
        file = form[option_selected].data['file']
        try:
            dataset_name = config_ops.new_image_dataset(APP_ROOT, username, option_selected, file)
            return jsonify(status='ok', msg=dataset_name)
        except Exception as e:
            return jsonify(status='error', msg=str(e))
    return render_template('upload_image.html', token=session['token'],
                           data_types=config_ops.get_datasets_type(APP_ROOT, username), form=form)


@app.route('/gui', methods=['GET', 'POST'])
@login_required
def gui():
    username = session['user']
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    user_dataset = config_ops.get_datasets_and_types(APP_ROOT, username)
    return render_template('gui.html', user=username, token=session['token'], page=1, user_dataset=user_dataset,
                           dataset_params={}, data=None, parameters=param_configs, cy_model=[],
                           model_name='new_model', num_outputs=None)


@app.route('/gui_load', methods=['POST'])
@login_required
@check_config
def gui_load():
    local_sess = Session(app)
    local_sess.add_user((session['user'], session['_id']))
    username = session['user']
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    user_dataset = config_ops.get_datasets_and_types(APP_ROOT, username)

    model_name = request.form['model']
    local_sess.set_config_file(sys_ops.get_config_path(APP_ROOT, username, model_name))

    if local_sess.load_config():
        hlp = local_sess.get_helper()
        return render_template('gui.html', token=session['token'], page=1, user=username, user_dataset=user_dataset,
                               parameters=param_configs, dataset_params=hlp.get_dataset_params(), data=hlp.get_data(),
                               cy_model=sys_ops.load_cy_model(model_name, username),
                               model_name=model_name, num_outputs=hlp.get_num_outputs())
    #  TODO send error config not loaded
    return render_template('gui.html', token=session['token'], page=1, user=username, user_dataset=user_dataset,
                           dataset_params={}, data=None, parameters=param_configs, cy_model=[], model_name='new_model',
                           num_outputs=None)


@app.route('/gui_input', methods=['POST'])
@login_required
@check_config
def gui_input():
    local_sess = Session(app)
    local_sess.add_user((session['user'], session['_id']))
    dataset_name, user = get_dataset(request), session['user']
    upload_util.new_config(dataset_name, user, local_sess, APP_ROOT)
    hlp = local_sess.get_helper()
    hlp.set_split(get_split(request))
    hlp.process_features_request(request)
    result = hlp.process_targets_request(request)
    return jsonify(**result)


@app.route('/gui_select_data', methods=['POST'])
@login_required
@check_config
def gui_select_data():
    local_sess = Session(app)
    local_sess.add_user((session['user'], session['_id']))
    dataset_name, user = get_dataset(request), session['user']
    upload_util.new_config(dataset_name, user, local_sess, APP_ROOT)
    data = local_sess.get_helper().get_data()
    return jsonify(data=data)


@app.route('/save_model', methods=['GET', 'POST'])
@login_required
@check_config
def save_model():
    local_sess = Session(app)
    local_sess.add_user((session['user'], session['_id']))
    dataset_name, user = get_dataset(request), session['user']
    upload_util.new_config(dataset_name, user, local_sess, APP_ROOT)
    hlp = local_sess.get_helper()
    hlp.set_split(get_split(request))
    local_sess.get_helper().process_features_request(request)
    local_sess.get_helper().process_targets_request(request)

    model_name = get_model_name(request)
    local_sess.set_model_name(model_name)
    local_sess.set_mode(get_mode(request))
    if get_mode(request) == 'custom':
        local_sess.set_custom(request.get_json())
        path = sys_ops.get_models_pat(APP_ROOT, session['user'])
        os.makedirs(path, exist_ok=True)
        c_path, t_path = custom.save_model_config(local_sess.get_model(), path, local_sess.get_cy_model(), model_name)
        local_sess.set_custom_path(c_path)  #
        local_sess.set_transform_path(t_path)
    else:
        custom_path = sys_ops.create_custom_path(APP_ROOT, session['user'], model_name)
        cy_model = get_cy_model(request)
        custom.save_cy_model(custom_path, cy_model)

        data = get_data(request)
        data['loss_function'] = get_loss(request)
        custom.save_canned_data(data, custom_path)

        local_sess.set_canned_data(data)
        local_sess.set_cy_model(cy_model)

    username = session['user']
    config_path = sys_ops.get_config_path(APP_ROOT, username, local_sess.get_model_name())
    local_sess.set_config_file(config_path)
    local_sess.write_config()

    config_ops.define_new_model(APP_ROOT, username, local_sess.get_writer(), local_sess.get_model_name())
    local_sess.write_params()
    return jsonify(explanation='ok')


@app.route('/params_run', methods=['POST'])
@login_required
@check_config
def params_run():
    try:
        model_name = get_model_name(request)
        config_file = sys_ops.get_config_path(APP_ROOT, session['user'], model_name)
        parameters = param_utils.get_params(config_file)
        sess.set_config_file(config_file)
        sess.load_config()
        sess.set_model_name(model_name)
        export_dir = config_reader.read_config(sess.get_config_file()).export_dir()
        checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
        metric = sess.get_metric()
        graphs = train_eval_graphs(config_reader.read_config(sess.get_config_file()).checkpoint_dir())
        return jsonify(checkpoints=checkpoints, parameters=parameters, metric=metric, graphs=graphs)
    except (KeyError, NoSectionError):
        return jsonify(checkpoints='', parameters='', metric='', graphs={})


@app.route('/params_predict', methods=['POST'])
@login_required
@check_config
def params_predict():
    try:
        local_sess = Session(app)
        local_sess.add_user((session['user'], session['_id']))
        model_name = get_model_name(request)
        config_file = sys_ops.get_config_path(APP_ROOT, session['user'], model_name)
        local_sess.set_config_file(config_file)
        local_sess.load_config()
        local_sess.set_model_name(model_name)
        export_dir = config_reader.read_config(local_sess.get_config_file()).export_dir()
        checkpoints = run_utils.get_eval_results(export_dir, local_sess.get_writer(), local_sess.get_config_file())
        metric = local_sess.get_metric()
        params, _ = local_sess.get_helper().get_default_data_example()
        return jsonify(checkpoints=checkpoints, metric=metric, params=params)
    except (KeyError, NoSectionError):
        return jsonify(checkpoints='', metric='', params={})


@app.route('/run', methods=['GET', 'POST'])
@login_required
@check_config
def run():
    username = session['user']
    _, model_configs = config_ops.get_configs_files(APP_ROOT, username)
    user_datasets = config_ops.get_datasets_and_types(APP_ROOT, username)
    model_name = ''
    checkpoints = ''
    metric = ''
    graphs = {}

    form = GeneralParamForm()

    running, config_file = th.check_running(username)
    if not running:
        config_file = sess.get_config_file() if sess.check_key('config_file') else None

    if config_file is not None:
        sess.set_config_file(config_file)
        sess.load_config()
        param_utils.set_form(form, sess.get_config_file())
        model_name = config_file.split('/')[-2]
        sess.set_model_name(model_name)
        export_dir = config_reader.read_config(sess.get_config_file()).export_dir()
        checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
        metric = sess.get_metric()
        graphs = train_eval_graphs(config_reader.read_config(sess.get_config_file()).checkpoint_dir())

    if request.method == 'POST':
        sess.run_or_pause(is_run(request))

        config_path = sys_ops.get_config_path(APP_ROOT, username, request.form['model_name'])
        sess.set_model_name(request.form['model_name'])

        sess.set_config_file(config_path)
        sess.load_config()

        sess.get_writer().populate_config(request.form)
        sess.get_writer().write_config(sess.get_config_file())

        th.run_tensor_board(username, sess.get_config_file())

        all_params_config = config_reader.read_config(sess.get_config_file())

        canned_data = os.path.join(APP_ROOT, 'user_data', username, 'models', request.form['model_name'], 'custom',
                                   'canned_data.json')
        if os.path.isfile(canned_data):
            all_params_config.set_canned_data(json.load(open(canned_data)))

        all_params_config.set_email(db_ops.get_email(username))

        sess.check_log_fp(all_params_config)

        th.handle_request(get_action(request), all_params_config, username, get_resume_from(request),
                          sess.get_config_file())
        metric = sess.get_metric()
        return jsonify(status='ok', metric=metric)

    return render_template('run.html', title="Run", user=username, token=session['token'], form=form,
                           user_models=model_configs, dataset_params=user_datasets, running=running,
                           model_name=model_name, checkpoints=checkpoints, metric=metric, graphs=graphs)


@app.route('/predict', methods=['POST', 'GET'])
@login_required
@check_config
def predict():
    if request.method == 'POST':
        local_sess = Session(app)
        local_sess.add_user((session['user'], session['_id']))

        config_path = sys_ops.get_config_path(APP_ROOT, session['user'], request.form['model_name'])
        local_sess.set_model_name(request.form['model_name'])

        local_sess.set_config_file(config_path)
        local_sess.load_config()
        hlp = local_sess.get_helper()
        all_params_config = run_utils.create_result_parameters(request, local_sess)
        new_features = hlp.get_new_features(request, default_features=False)

        canned_data = os.path.join(APP_ROOT, 'user_data', session['user'], 'models', request.form['model_name'],
                                   'custom',
                                   'canned_data.json')
        if os.path.isfile(canned_data):
            all_params_config.set_canned_data(json.load(open(canned_data)))

        final_pred, success = th.predict_estimator(all_params_config, new_features)
        return jsonify(error=final_pred) if not success else jsonify(
            run_utils.get_predictions(hlp.get_targets(), final_pred))
    username = session['user']
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    return render_template('predict.html', user=session['user'], token=session['token'],
                           parameters=param_configs)


@app.route('/explain', methods=['POST', 'GET'])
@login_required
@check_config
def explain():
    if request.method == 'POST':
        local_sess = Session(app)
        local_sess.add_user((session['user'], session['_id']))

        config_path = sys_ops.get_config_path(APP_ROOT, session['user'], request.form['model_name'])
        local_sess.set_model_name(request.form['model_name'])

        local_sess.set_config_file(config_path)
        local_sess.load_config()
        hlp = local_sess.get_helper()
        all_params_config = run_utils.create_result_parameters(request, local_sess)

        ep = hlp.process_explain_request(request)
        if 'explanation' in ep:
            return jsonify(**ep)

        canned_data = os.path.join(APP_ROOT, 'user_data', session['user'], 'models', request.form['model_name'],
                                   'custom',
                                   'canned_data.json')
        if os.path.isfile(canned_data):
            all_params_config.set_canned_data(json.load(open(canned_data)))

        result, success = th.explain_estimator(all_params_config, ep)
        if success:
            result = hlp.explain_return(request, result)
            return jsonify(**result)

        return jsonify(error=result)

    username = session['user']
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    return render_template('explain.html', user=session['user'], token=session['token'],
                           parameters=param_configs)


@app.route('/upload_test_file', methods=['POST', 'GET'])
@login_required
@check_config
def upload_test_file():
    model_name = request.get_json()['model_name']
    local_sess = Session(app)
    local_sess.add_user((session['user'], session['_id']))

    config_path = sys_ops.get_config_path(APP_ROOT, session['user'], model_name)
    local_sess.set_model_name(model_name)

    local_sess.set_config_file(config_path)
    local_sess.load_config()
    result = local_sess.get_helper().test_upload(request)
    return jsonify(result=result)


@app.route('/test', methods=['POST', 'GET'])
@login_required
@check_config
def test():
    if request.method == 'POST':
        model_name = request.get_json()['model_name']
        local_sess = Session(app)
        local_sess.add_user((session['user'], session['_id']))
        config_path = sys_ops.get_config_path(APP_ROOT, session['user'], model_name)
        local_sess.set_model_name(model_name)

        local_sess.set_config_file(config_path)
        local_sess.load_config()
        hlp = local_sess.get_helper()

        try:
            has_targets, test_filename, df_test, result = hlp.test_request(request)
        except Exception as e:
            return jsonify(error='Test\'s file structure is not correct')

        all_params_config = config_reader.read_config(local_sess.get_config_file())
        all_params_config.set('PATHS', 'checkpoint_dir',
                              os.path.join(all_params_config.export_dir(), model_name))
        canned_data = os.path.join(APP_ROOT, 'user_data', session['user'], 'models', model_name,
                                   'custom',
                                   'canned_data.json')
        if os.path.isfile(canned_data):
            all_params_config.set_canned_data(json.load(open(canned_data)))

        final_pred, success = th.predict_test_estimator(all_params_config, test_filename)
        if not success:
            return jsonify(error=final_pred)
        try:
            file_path = hlp.process_test_predict(df_test, final_pred, test_filename)
        except Exception as e:
            return jsonify(error=str(e))

        df = pd.read_csv(file_path)
        predict_table = {'data': df.as_matrix().tolist(),
                         'columns': [{'title': v} for v in df.columns.values.tolist()]}
        labels = hlp.get_target_labels()
        metrics = {}
        store_predictions(has_targets, local_sess, final_pred, hlp.get_df_test(df_test, has_targets))
        if has_targets:
            metrics = get_metrics('classification', local_sess.get_y_true(), local_sess.get_y_pred(), labels,
                                  logits=local_sess.get_logits()) if hlp.get_mode() == 'classification' \
                else get_metrics('regression', local_sess.get_y_true(), local_sess.get_y_pred(), labels,
                                 target_len=len(hlp.get_targets()))

        return jsonify(predict_table=predict_table,
                       metrics=metrics,
                       targets=hlp.get_targets())

    username = session['user']
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    return render_template('test.html', user=session['user'], token=session['token'], parameters=param_configs)


@app.route('/data_graphs', methods=['POST', 'GET'])
@login_required
@check_config
def data_graphs():
    dataset_name = get_datasetname(request)
    main_path = sys_ops.get_dataset_path(APP_ROOT, session['user'], dataset_name)
    df = pd.read_csv(os.path.join(main_path, dataset_name + '.csv'))
    df_as_json, norm, corr = get_norm_corr(df)
    return jsonify(data=json.loads(df_as_json), norm=norm, corr=corr)


@app.route('/image_graphs', methods=['POST', 'GET'])
@login_required
@check_config
def image_graphs():
    local_sess = Session(app)
    local_sess.add_user((session['user'], session['_id']))
    dataset_name = get_datasetname(request)
    upload_util.new_config(dataset_name, session['user'], local_sess, APP_ROOT)
    data = local_sess.get_helper().get_data()
    return jsonify(data=data)


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
    _, models = config_ops.get_configs_files(APP_ROOT, username)
    datasets = config_ops.get_datasets_type(APP_ROOT, username)
    return jsonify(datasets=datasets, models=models, data_types=config_ops.get_datasets_type(APP_ROOT, username))


@app.route('/delete_dataset', methods=['POST'])
@login_required
@check_config
def delete_dataset():
    username = session['user']
    sys_ops.delete_dataset(get_all(request), get_dataset(request), get_models(request), username)
    _, models = config_ops.get_configs_files(APP_ROOT, username)
    datasets = config_ops.get_datasets(APP_ROOT, username)
    return jsonify(datasets=datasets, models=models, data_types=config_ops.get_datasets_type(APP_ROOT, username))


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
        return jsonify(checkpoints=checkpoints, data=sess.get('log_fp').read() if sess.check_key('log_fp') else '',
                       running=running, epochs=epochs, graphs=graphs)
    except (KeyError, NoSectionError):
        return jsonify(checkpoints='', data='', running=running, epochs=0, graphs={})


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
    main_path = sys_ops.get_dataset_path(APP_ROOT, session['user'], dataset_name)
    try:
        parse(script, main_path, dataset_name)
        sys_ops.create_split_folders(main_path)
        return jsonify(valid=str(True))
    except Exception as e:
        return jsonify(valid=str(e))


@app.route("/download", methods=['GET', 'POST'])
def download():
    file_path = sess.get_predict_file()
    filename = file_path.split('/')[-1]
    return send_file(file_path, mimetype='text/csv', attachment_filename=filename, as_attachment=True)


@app.route("/default_prediction", methods=['GET', 'POST'])
@login_required
@check_config
def default_prediction():
    local_sess = Session(app)
    local_sess.add_user((session['user'], session['_id']))
    model_name = get_model_name(request)

    config_path = sys_ops.get_config_path(APP_ROOT, session['user'], model_name)
    local_sess.set_model_name(model_name)

    local_sess.set_config_file(config_path)
    local_sess.load_config()
    hlp = local_sess.get_helper()
    all_params_config = config_reader.read_config(local_sess.get_config_file())
    export_dir = all_params_config.export_dir()
    checkpoints = run_utils.get_eval_results(export_dir, local_sess.get_writer(), local_sess.get_config_file())
    metric = local_sess.get_metric()
    if len(checkpoints) == 0:
        return jsonify(checkpoints={}, metric=metric)
    checkpoints_df = run_utils.ckpt_to_table(checkpoints)

    all_params_config = run_utils.create_result_parameters(request, local_sess,
                                                           checkpoint=checkpoints_df['Model'].values[-1])
    new_features = hlp.get_new_features(None, default_features=True)

    canned_data = os.path.join(APP_ROOT, 'user_data', session['user'], 'models', model_name, 'custom',
                               'canned_data.json')
    if os.path.isfile(canned_data):
        all_params_config.set_canned_data(json.load(open(canned_data)))

    pred, success = th.predict_estimator(all_params_config, new_features, all=True)
    if not success:
        return jsonify(error=pred)

    example = hlp.generate_rest_call(pred)

    return jsonify(example=example, checkpoints=checkpoints, metric=metric)


@app.route("/deploy", methods=['GET', 'POST'])
@login_required
@check_config
def deploy():
    if request.method == 'POST' and 'model_name' in request.form:
        local_sess = Session(app)
        local_sess.add_user((session['user'], session['_id']))
        model_name = request.form['model_name']
        config_path = sys_ops.get_config_path(APP_ROOT, session['user'], model_name)
        all_params_config = config_reader.read_config(config_path)

        file_path = sys_ops.export_models(all_params_config.export_dir(), request.form['selected_rows'], model_name)
        return send_file(file_path, mimetype='application/zip', attachment_filename=file_path.split('/')[-1],
                         as_attachment=True)
    username = session['user']
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    return render_template('deploy.html', user=session['user'], token=session['token'],
                           parameters=param_configs)


@app.route('/explain_feature', methods=['POST'])
@login_required
@check_config
def explain_feature():
    hlp = sess.get_helper()
    all_params_config = config_reader.read_config(sess.get_config_file())
    all_params_config.set('PATHS', 'checkpoint_dir',
                          os.path.join(all_params_config.export_dir(), get_model(request)))
    file_path, unique_val_column = hlp.create_ice_data(request)

    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    try:
        final_pred, success = th.predict_test_estimator(all_params_config, file_path)
        if not success:
            return jsonify(error=final_pred)
    except:
        return jsonify(error=final_pred)
    data = hlp.process_ice_request(request, unique_val_column, final_pred)
    return jsonify(data=data)


@app.route('/')
def main():
    return redirect(url_for('login'))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"%s" % error)


db.init_app(app)

if __name__ == '__main__':
    sess = Session(app)
    app.run(debug=True, threaded=True, host='0.0.0.0')
    # app.run(debug=True, threaded=True)

wheel==0.33.1