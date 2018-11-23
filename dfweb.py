import json
import os
import pandas as pd
from configparser import NoSectionError
from forms.deploy_form import DeploymentForm
from forms.parameters_form import GeneralParamForm
from forms.upload_user import UploadUserForm
from utils import run_utils, upload_util, db_ops, feature_util, param_utils, preprocessing, config_ops, sys_ops
from config import config_reader
from database.db import db
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user
from forms.login_form import LoginForm
from forms.register import RegisterForm
from forms.upload_form import UploadForm
from pprint import pprint
from user import User
from utils import explain_util
from thread_handler import ThreadHandler
from session import Session
from utils.request_util import default_feature, default_columns, get_cat_columns, get_selected_rows, get_action, is_run, \
    get_resume_from
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
        return redirect(url_for('upload'))
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
    user_dataset = config_ops.get_datasets(APP_ROOT, username)
    return render_template('upload_user.html', form=form, user=session['user'], token=session['token'],
                           datasets=user_dataset, parameters=param_configs)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    sess.reset_user()  # TODO new session??
    username = session['user']
    form = UploadForm()
    mess = False
    if form.validate_on_submit() or form.options.data['is_existing'] == 'generate_data':
        if form.options.data['is_existing'] == 'new_files' and not form.new_files.train_file.data == '':
            mess = config_ops.new_config(form.new_files.train_file.data, form.new_files.test_file.data, APP_ROOT,
                                         username)
        elif form.options.data['is_existing'] == 'generate_data':
            dataset_name = form.generate_dataset.data['dataset_name']
            mess = config_ops.check_generated(dataset_name, APP_ROOT, username)
    examples = upload_util.get_examples()
    return render_template('upload.html', title='Data upload', form=form, page=0,
                           user_configs=config_ops.get_datasets(APP_ROOT, username), examples=examples, user=username,
                           token=session['token'], mess=mess)


@app.route('/gui', methods=['GET', 'POST'])
@login_required
@check_config
def gui():
    username = session['user']
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    user_dataset = config_ops.get_datasets(APP_ROOT, username)
    if not sess.check_key('config_file'):
        return render_template('gui.html', user=username, token=session['token'], page=1, user_dataset=user_dataset,
                               dataset_params={}, data=None, parameters=param_configs, cy_model=[],
                               model_name='new_model', num_outputs=None)
    data = sess.get_dataset()
    dataset_params = data.get_params()
    return render_template('gui.html', token=session['token'], page=1, user=username,
                           user_dataset=user_dataset,
                           parameters=param_configs,
                           cy_model=sys_ops.load_cy_model(sess.get_model_name(), username),
                           model_name=sess.get_model_name(),
                           num_outputs=data.get_num_outputs(),
                           dataset_params=dataset_params, data=data.get_data_summary().to_json())


@app.route('/gui_load', methods=['POST'])
@login_required
@check_config
def gui_load():
    username = session['user']
    model = request.form['model']
    sess.set_config_file(os.path.join(APP_ROOT, 'user_data', username, 'models', model, 'config.ini'))
    sess.load_config()

    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    user_dataset = config_ops.get_datasets(APP_ROOT, username)
    data = sess.get_dataset()
    dataset_params = data.get_params()
    return render_template('gui.html', token=session['token'], page=1, user=username, user_dataset=user_dataset,
                           parameters=param_configs, cy_model=sys_ops.load_cy_model(model, username),
                           num_outputs=data.get_num_outputs(),
                           dataset_params=dataset_params, data=data.get_data_summary().to_json(), model_name=model)


@app.route('/gui_select_data', methods=['POST'])
@login_required
@check_config
def gui_select_data():
    sess.reset_user()
    dataset_name, user = request.get_json()['dataset'], session['user']
    upload_util.new_config(dataset_name, user, sess, APP_ROOT)
    return jsonify(data=False)


@app.route('/gui_split', methods=['POST'])
@login_required
@check_config
def gui_split():
    train, val, test = request.get_json()['train'], request.get_json()['validation'], request.get_json()['test']
    sess.get_dataset().set_split(",".join([str(train), str(val), str(test)]))
    return jsonify(data=sess.get_dataset().get_data_summary().to_json())


@app.route('/gui_features', methods=['POST'])
@login_required
@check_config
def gui_features():
    dataset = sess.get_dataset()
    ds = dataset.get_data_summary()
    dataset.set_normalize(request.get_json()['normalize'])
    cat_columns, default_values = feature_util.reorder_request(default_feature(request), get_cat_columns(request),
                                                               default_columns(request), dataset.get_df().keys())
    dataset.update_features(cat_columns, default_values)
    data = ds[(ds.Category != 'hash') & (ds.Category != 'none')]
    return jsonify(data=data.to_json(), old_targets=dataset.get_targets() or [])


@app.route('/gui_targets', methods=['POST'])
@login_required
@check_config
def gui_targets():
    selected_rows = request.get_json()['targets']
    dataset = sess.get_dataset()

    if not dataset.update_targets(selected_rows):
        return jsonify(error='Only numerical features are supported for multiouput.')

    dataset.split_dataset()
    dataset.update_feature_columns()  # TODO maybe inside split

    if not preprocessing.check_train(dataset.get_train_file(), dataset.get_targets()):  # TODO move to type-tabular
        return jsonify(error='Number of classes for the target should be greater than 1.')

    num_outputs = dataset.get_num_outputs()
    input_shape = dataset.get_num_inputs()
    hidden_layers = param_utils.get_hidden_layers(input_shape, num_outputs, dataset.get_train_size())
    return jsonify(error=False, num_outputs=num_outputs, input_shape='[' + str(input_shape) + ']',
                   hidden_layers=hidden_layers)


@app.route('/gui_editor', methods=['GET', 'POST'])
@login_required
@check_config
def gui_editor():
    sess.set_custom(request.get_json())
    return jsonify(explanation='ok')


@app.route('/save_canned', methods=['GET', 'POST'])
@login_required
@check_config
def save_canned():  # TODO not allowed if image (for now)
    custom_path = os.path.join(APP_ROOT, 'user_data', session['user'], 'models',
                               request.get_json()['model_name'], 'custom')
    cy_model = request.get_json()['cy_model']
    data = request.get_json()['data']
    custom.save_cy_model(custom_path, cy_model)
    data['loss_function'] = request.get_json()['loss']
    sess.set_canned_data(data)
    sess.set_cy_model(cy_model)
    return jsonify(explanation='ok')


@app.route('/save_model', methods=['GET', 'POST'])
@login_required
@check_config
def save_model():
    model_name = request.values['modelname']
    sess.set_model_name(model_name)
    sess.set_mode('canned')
    if request.values['mode'] == '0':
        sess.set_mode('custom')
        path = os.path.join(APP_ROOT, 'user_data', session['user'], 'models')
        os.makedirs(path, exist_ok=True)
        c_path, t_path = custom.save_model_config(sess.get_model(), path, sess.get_cy_model(), model_name)
        sess.set_custom_path(c_path)
        sess.set_transform_path(t_path)
    return redirect(url_for('parameters'))


@app.route('/parameters', methods=['GET', 'POST'])
@login_required
@check_config
def parameters():
    form = GeneralParamForm()
    if form.validate_on_submit():
        sess.get_writer().populate_config(request.form)
        return redirect(url_for('run'))
    username = session['user']
    config_path = os.path.join(APP_ROOT, 'user_data', username, 'models', sess.get_model_name(), 'config.ini')
    sess.set_config_file(config_path)
    param_utils.set_form(form, sess.get_config_file())
    sess.write_config()
    return render_template('parameters.html', title="Parameters", form=form, page=2, user=session['user'],
                           token=session['token'])


@app.route('/run', methods=['GET', 'POST'])
@login_required
@check_config
def run():
    username = session['user']
    config_ops.define_new_model(APP_ROOT, username, sess.get_writer(), sess.get_model_name())
    sess.write_params()
    all_params_config = config_reader.read_config(sess.get_config_file())
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    all_params_config.set_email(db_ops.get_email(username))
    # labels = feature_util.get_target_labels(sess.get_targets(), sess.get_cat(), sess.get_fs())
    export_dir = all_params_config.export_dir()

    checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
    th.run_tensor_board(username, sess.get_config_file())
    running = th.check_running(username)
    sess.run_or_pause(running)

    if request.method == 'POST':
        sess.run_or_pause(is_run(request))
        # dtypes = sess.get_fs().group_by(sess.get_cat_list())
        sess.check_log_fp(all_params_config)
        th.handle_request(get_action(request), all_params_config, username, get_resume_from(request))
        return jsonify(True)
    dataset = sess.get_dataset()
    dict_types, categoricals = run_utils.get_dictionaries(dataset.get_defaults(), dataset.get_categories(),
                                                          dataset.get_feature_selection(),
                                                          dataset.get_targets())
    sfeatures = feature_util.remove_targets(dataset.get_defaults(), dataset.get_targets())
    explain_disabled = run_utils.get_explain_disabled(dataset.get_categories())
    return render_template('run.html', title="Run", page=3, features=sfeatures,
                           types=run_utils.get_html_types(dict_types), categoricals=categoricals,
                           checkpoints=checkpoints, port=th.get_port(username, sess.get_config_file()),
                           running=sess.get_status(), explain_disabled=explain_disabled, targets=dataset.get_targets(),
                           user=username, token=session['token'], metric=sess.get_metric(),
                           has_test=dataset.get_test_file is not None)

    # return render_template('run.html', title="Run", page=3, checkpoints=checkpoints, running=sess.get_status(),
    #                        port=th.get_port(username, sess.get_config_file()), user=username, token=session['token'],
    #                        metric=sess.get_metric(), **params)


@app.route('/predict', methods=['POST'])
@login_required
@check_config
def predict():
    new_features, all_params_config = run_utils.create_result_parameters(request, sess, sess.get_dataset())
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    final_pred = th.predict_estimator(all_params_config, new_features)
    return jsonify(error=True) if final_pred is None else jsonify(
        run_utils.get_predictions(sess.get_dataset().get_targets(), final_pred))


@app.route('/explain', methods=['POST', 'GET'])
@login_required
@check_config
def explain():
    if request.method == 'POST':
        new_features, all_params_config = run_utils.create_result_parameters(request, sess, sess.get_dataset())
        labels = sess.get_dataset().get_target_labels()
        input_check = explain_util.check_input(request.form['num_feat'], request.form['top_labels'], len(new_features),
                                               1 if labels is None else len(labels))
        if input_check is not None:
            return jsonify(explanation=input_check)
        if sess.mode_is_canned():
            all_params_config.set_canned_data(sess.get_canned_data())
        ep = {
            'features': new_features,
            'num_features': int(request.form['num_feat']),
            'top_labels': int(request.form['top_labels']),
            'sel_target': request.form['exp_target']
        }

        result = th.explain_estimator(all_params_config, ep)
        return jsonify(
            explanation=explain_util.explain_return(sess, new_features, result, sess.get_dataset().get_targets()))
    else:
        return render_template('explain.html', title="Explain", page=5, graphs=sess.get_dict_graphs(),
                               predict_table=sess.get_dict_table(), features=sess.get_new_features(),
                               model=sess.get_model(), exp_target=sess.get_exp_target(), type=sess.get_type(),
                               user=session['user'], token=session['token'])


@app.route('/test', methods=['POST', 'GET'])
@login_required
@check_config
def test():
    dataset = sess.get_dataset()
    if 'filename' in request.get_json():
        test_file = request.get_json()['filename']
        try:
            test_filename = os.path.join(dataset.get_base_path(), 'test', test_file)
            df = sys_ops.bytestr2df(request.get_json()['file'], test_filename)
            has_targets = sys_ops.check_df(df, dataset.get_df(), dataset.get_targets(), test_filename)
        except ValueError:
            return jsonify(result="The file contents are not valid.")
    else:
        test_filename = dataset.get_test_file()
        has_targets = True
        df = pd.read_csv(test_filename)
    all_params_config = config_reader.read_config(sess.get_config_file())
    all_params_config.set('PATHS', 'checkpoint_dir',
                          os.path.join(all_params_config.export_dir(), request.get_json()['model']))
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    final_pred = th.predict_test_estimator(all_params_config, test_filename)
    if final_pred is None:
        return jsonify(result='Model\'s structure does not match the new parameter configuration')

    predict_file = sys_ops.save_results(df, final_pred['preds'], dataset.get_targets(), test_filename.split('/')[-1],
                                        dataset.get_base_path())
    sess.set_has_targets(has_targets)
    sess.set_predict_file(predict_file)

    store_predictions(has_targets, sess, final_pred, df[dataset.get_targets()].values)
    return jsonify(result="ok")


@app.route('/data_graphs', methods=['POST', 'GET'])
@login_required
@check_config
def data_graphs():
    if request.method == 'POST':
        sess.set_generate_df(request.form['generate_dataset-dataset_name'], APP_ROOT)
        return jsonify(explanation='ok')
    else:
        df_as_json, norm, corr = get_norm_corr(sess.get('generated_df').copy())
        return render_template('data_graphs.html', data=json.loads(df_as_json), norm=norm, corr=corr)


@app.route('/delete', methods=['POST'])
@login_required
@check_config
def delete():
    all_params_config = config_reader.read_config(sess.get_config_file())
    export_dir = all_params_config.export_dir()
    del_id = request.get_json()['deleteID']
    paths = [del_id] if del_id != 'all' else [d for d in os.listdir(export_dir) if
                                              os.path.isdir(os.path.join(export_dir, d))]
    sys_ops.delete_recursive(paths, export_dir)
    checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
    return jsonify(checkpoints=checkpoints)


@app.route('/delete_model', methods=['POST'])
@login_required
@check_config
def delete_model():
    username = session['user']
    sys_ops.delete_models(request.get_json()['all'], [request.get_json()['model']], username)
    _, models = config_ops.get_configs_files(APP_ROOT, username)
    datasets = config_ops.get_datasets(APP_ROOT, username)
    return jsonify(datasets=datasets, models=models)


@app.route('/delete_dataset', methods=['POST'])
@login_required
@check_config
def delete_dataset():
    username = session['user']
    sys_ops.delete_dataset(request.get_json()['all'], request.get_json()['dataset'], request.get_json()['models'],
                           username)
    _, models = config_ops.get_configs_files(APP_ROOT, username)
    datasets = config_ops.get_datasets(APP_ROOT, username)
    return jsonify(datasets=datasets, models=models)


@app.route('/refresh', methods=['GET'])
@login_required
@check_config
def refresh():
    all_params_config = config_reader.read_config(sess.get_config_file())
    running = th.check_running(session['user'])
    sess.run_or_pause(running)
    epochs = run_utils.get_step(sess.get_dataset().get_train_size(), all_params_config.train_batch_size(),
                                all_params_config.checkpoint_dir())
    try:
        config_file = sess.get_config_file()
        export_dir = config_reader.read_config(config_file).export_dir()
        checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), config_file)
        return jsonify(checkpoints=checkpoints, data=sess.get('log_fp').read(), running=running, epochs=epochs)
    except (KeyError, NoSectionError):
        return jsonify(checkpoints='', data='', running=running, epochs=epochs)


@app.route('/confirm', methods=['GET', 'POST'])
@login_required
@check_config
def confirm():
    dataset_name = request.get_json()['datasetname']
    script = request.get_json()['script']
    main_path = os.path.join(APP_ROOT, 'user_data', session['user'], 'datasets', dataset_name)

    e = parse(script, main_path, dataset_name)
    if e is not True:
        e = str(e).split("Expecting: ")[0]
    os.makedirs(os.path.join(main_path, 'train'), exist_ok=True)
    os.makedirs(os.path.join(main_path, 'valid'), exist_ok=True)
    os.makedirs(os.path.join(main_path, 'test'), exist_ok=True)
    return jsonify(valid=str(e))


@app.route("/download", methods=['GET', 'POST'])
def download():
    file_path = sess.get_predict_file()
    filename = file_path.split('/')[-1]
    return send_file(file_path, mimetype='text/csv', attachment_filename=filename, as_attachment=True)


@app.route("/show_test", methods=['GET', 'POST'])
def show_test():
    dataset = sess.get_dataset()
    file_path = sess.get_predict_file()
    df = pd.read_csv(file_path)
    predict_table = {'data': df.as_matrix().tolist(),
                     'columns': [{'title': v} for v in df.columns.values.tolist()]}
    labels = dataset.get_target_labels()
    metrics = None

    if sess.get_has_targets():
        metrics = get_metrics('classification', sess.get_y_true(), sess.get_y_pred(), labels,
                              logits=sess.get_logits()) if sess.check_key('logits') \
            else get_metrics('regression', sess.get_y_true(), sess.get_y_pred(), labels,
                             target_len=len(dataset.get_targets()))

    return render_template('test_prediction.html', token=session['token'], predict_table=predict_table, metrics=metrics,
                           targets=dataset.get_targets())


@app.route("/deploy", methods=['GET', 'POST'])
@login_required
@check_config
def deploy():
    all_params_config = config_reader.read_config(sess.get_config_file())
    dataset = sess.get_dataset()
    export_dir = all_params_config.export_dir()
    checkpoints = run_utils.ckpt_to_table(
        run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file()))
    new_features, all_params_config = run_utils.create_result_parameters(request, sess, dataset,
                                                                         default_features=True,
                                                                         checkpoint=
                                                                         checkpoints['Model'].values[
                                                                             -1])
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    pred = th.predict_estimator(all_params_config, new_features, all=True)
    if pred is None:
        return redirect(url_for('run'))  # flash('Deploy error.', 'error')

    call, d, epred = sys_ops.gen_example(dataset.get_targets(), dataset.get_data_summary(), dataset.get_df(),
                                         'model_name', pred)
    example = {'curl': call, 'd': d, 'output': epred}

    if request.method == 'POST' and 'model_name' in request.form:
        file_path = sys_ops.export_models(export_dir, get_selected_rows(request), request.form['model_name'])
        return send_file(file_path, mimetype='application/zip', attachment_filename=file_path.split('/')[-1],
                         as_attachment=True)
    form = DeploymentForm()
    form.model_name.default = sess.get_model_name()
    form.process()
    return render_template('deploy.html', token=session['token'], checkpoints=checkpoints, page=4,
                           form=form, example=example)


@app.route('/explain_feature', methods=['POST'])
@login_required
@check_config
def explain_feature():
    exp_target = request.get_json()['exp_target']
    exp_feature = request.get_json()['explain_feature']
    all_params_config = config_reader.read_config(sess.get_config_file())
    all_params_config.set('PATHS', 'checkpoint_dir',
                          os.path.join(all_params_config.export_dir(), request.get_json()['model']))
    dataset = sess.get_dataset()
    file_path, unique_val_column = explain_util.generate_ice_df(request, dataset.get_df(), dataset.get_file(),
                                                                dataset.get_targets(), dataset.get_dtypes())
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    final_pred = th.predict_test_estimator(all_params_config, file_path)
    if final_pred is None:
        return jsonify(data='Error')

    lab, probs = explain_util.get_exp_target_prediction(dataset.get_targets(), exp_target, final_pred,
                                                        dataset.get_dtypes())
    data = {exp_feature: unique_val_column,
            exp_target: lab,
            exp_target + '_prob': probs}
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
