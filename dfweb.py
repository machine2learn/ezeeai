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
    sess.reset_user()
    username = session['user']
    form = UploadForm()
    mess = False
    if form.validate_on_submit() or form.options.data['is_existing'] == 'generate_data':
        if form.options.data['is_existing'] == 'new_files' and not form.new_files.train_file.data == '':
            mess = config_ops.new_config(form.new_files.train_file.data, form.new_files.test_file.data, APP_ROOT,
                                         username, sess)
        elif form.options.data['is_existing'] == 'generate_data':
            dataset_name = form.generate_dataset.data['dataset_name']
            mess = config_ops.check_generated(dataset_name, APP_ROOT, username)
    flash_errors(form)
    examples = upload_util.get_examples()
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    return render_template('upload.html', title='Data upload', form=form, page=0,
                           user_configs=config_ops.get_datasets(APP_ROOT, username),
                           parameters=param_configs, examples=examples, user=username,
                           token=session['token'], mess=mess)


@app.route('/gui', methods=['GET', 'POST'])
@login_required
@check_config
def gui():
    username = session['user']
    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    user_dataset = config_ops.get_datasets(APP_ROOT, username)
    if not sess.check_key('dataset_name') or not sess.check_key('config_file'):
        return render_template('gui.html', user=username, token=session['token'], page=1, user_dataset=user_dataset,
                               dataset_params={}, data=None, parameters=param_configs, cy_model=[],
                               model_name='new_model', num_outputs=None)
    dataset_params = sess.get_dataset_params()
    sess.set_targets(sess.get_targets(), sess.get_normalize(), sess.get_train_file())
    return render_template('gui.html', token=session['token'], page=1, user=username,
                           user_dataset=user_dataset,
                           parameters=param_configs,
                           cy_model=sys_ops.load_cy_model(sess.get_model_name(), username),
                           model_name=sess.get_model_name(),
                           num_outputs=feature_util.calc_num_outputs(sess.get_df(), sess.get_targets()),
                           dataset_params=dataset_params, data=sess.get_data().to_json())


@app.route('/gui_load', methods=['POST'])
@login_required
@check_config
def gui_load():
    username = session['user']
    model = request.form['model']
    sess.set_dataset_name(request.form['dataset'])
    sess.set_config_file(os.path.join(APP_ROOT, 'user_data', username, 'models', model, 'config.ini'))
    sess.load_config()

    _, param_configs = config_ops.get_configs_files(APP_ROOT, username)
    user_dataset = config_ops.get_datasets(APP_ROOT, username)
    dataset_params = sess.get_dataset_params()
    sess.set_targets(sess.get_targets(), sess.get_normalize(), sess.get_train_file())
    return render_template('gui.html', token=session['token'], page=1, user=username, user_dataset=user_dataset,
                           parameters=param_configs, cy_model=sys_ops.load_cy_model(model, username),
                           num_outputs=feature_util.calc_num_outputs(sess.get_df(), sess.get_targets()),
                           dataset_params=dataset_params, data=sess.get_data().to_json(), model_name=model)


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
    sess.set_split_df(",".join([str(train), str(val), str(test)]))
    sess.load_features()
    return jsonify(data=sess.get_data().to_json())


@app.route('/gui_features', methods=['POST'])
@login_required
@check_config
def gui_features():
    old_cats = sess.get_cat_list()
    sess.set_normalize(request.get_json()['normalize'])
    sess.set_feat_eng(str(sess.get_normalize()))
    cat_columns, default_values = feature_util.reorder_request(default_feature(request), get_cat_columns(request),
                                                               default_columns(request), sess.get_keys())
    sess.update_new_features(cat_columns, default_values)
    sess.set_column_categories(feature_util.write_features(old_cats, sess.get_data()))
    data = sess.get_data()[(sess.get_cat() != 'hash') & (sess.get_cat() != 'none')]
    return jsonify(data=data.to_json(), old_targets=sess.get('old_targets') if sess.check_key('old_targets') else [])


@app.route('/gui_targets', methods=['POST'])
@login_required
@check_config
def gui_targets():
    selected_rows = request.get_json()['targets']
    if feature_util.check_targets(sess.get_cat(), selected_rows):
        if 'split_df' in sess.get_config():
            train_file, validation_file, test_file = preprocessing.split_train_test(sess.get_split_df(),
                                                                                    sess.get_file(), selected_rows,
                                                                                    sess.get_df())
            sess.update_split(train_file, validation_file, test_file)

    sess.set_targets(selected_rows, sess.get_normalize(), sess.get_train_file())
    if not preprocessing.check_train(sess.get_train_file(), sess.get_targets()):
        return jsonify(error='Number of classes for the target should be greater than 1.')

    num_outputs = feature_util.calc_num_outputs(sess.get_df(), sess.get_targets())
    input_shape = feature_util.calc_num_inputs(sess.get_features(), sess.get_fs().group_by(sess.get_cat_list())[
        'none'])
    return jsonify(error=False, num_outputs=num_outputs, input_shape='[' + str(input_shape) + ']')


@app.route('/gui_editor', methods=['GET', 'POST'])
@login_required
@check_config
def gui_editor():
    sess.set_custom(request.get_json())
    return jsonify(explanation='ok')


@app.route('/save_canned', methods=['GET', 'POST'])
@login_required
@check_config
def save_canned():
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
        c_path, t_path = custom.save_model_config(sess.get_df(), sess.get_targets(), sess.get_model(), path,
                                                  sess.get_cy_model(), sess.get_cat_list(), model_name)
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
        sess.set_train_size()
        return redirect(url_for('run'))
    username = session['user']
    config_path = os.path.join(APP_ROOT, 'user_data', username, 'models', sess.get_model_name(), 'config.ini')
    sess.set_config_file(config_path)
    param_utils.set_form(form, sess.get_config_file())
    sess.set_train_size_from_pd()
    sess.add_cat_columns()
    sess.write_config()
    return render_template('parameters.html', title="Parameters", form=form, page=2, user=session['user'],
                           token=session['token'])


@app.route('/run', methods=['GET', 'POST'])
@login_required
@check_config
def run():
    username = session['user']
    config_ops.define_new_model(APP_ROOT, username, sess.get_writer(), sess.get_model_name())
    sess.write_custom_params()
    all_params_config = config_reader.read_config(sess.get_config_file())
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    all_params_config.set_email(db_ops.get_email(username))
    labels = feature_util.get_target_labels(sess.get_targets(), sess.get_cat(), sess.get_fs())
    export_dir = all_params_config.export_dir()

    checkpoints = run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file())
    th.run_tensor_board(username, sess.get_config_file())
    running = th.check_running(username)
    sess.run_or_pause(running)

    if request.method == 'POST':
        sess.run_or_pause(is_run(request))
        dtypes = sess.get_fs().group_by(sess.get_cat_list())
        sess.check_log_fp(all_params_config)
        th.handle_request(get_action(request), all_params_config, sess.get_features(), sess.get_targets(),
                          labels, sess.get_defaults(), dtypes, username, get_resume_from(request))
        return jsonify(True)
    dict_types, categoricals = run_utils.get_dictionaries(sess.get_defaults(), sess.get_cat_list(), sess.get_fs(),
                                                          sess.get_targets())
    sfeatures = feature_util.remove_targets(sess.get_defaults(), sess.get_targets())
    explain_disabled = run_utils.get_explain_disabled(sess.get_cat_list())
    return render_template('run.html', title="Run", page=3, features=sfeatures,
                           types=run_utils.get_html_types(dict_types), categoricals=categoricals,
                           checkpoints=checkpoints, port=th.get_port(username, sess.get_config_file()),
                           running=sess.get_status(), explain_disabled=explain_disabled, targets=sess.get_targets(),
                           user=username, token=session['token'], metric=sess.get_metric(),
                           has_test=sess.check_key('test_file'))


@app.route('/predict', methods=['POST'])
@login_required
@check_config
def predict():
    new_features, all_params_config, labels, dtypes = run_utils.create_result_parameters(request, sess)
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    final_pred = th.predict_estimator(all_params_config, sess.get_features(), sess.get_targets(), labels,
                                      sess.get_defaults(), dtypes, new_features, sess.get_df())
    return jsonify(error=True) if final_pred is None else jsonify(
        run_utils.get_predictions(sess.get_targets(), final_pred))


@app.route('/explain', methods=['POST', 'GET'])
@login_required
@check_config
def explain():
    if request.method == 'POST':
        new_features, all_params_config, labels, dtypes = run_utils.create_result_parameters(request, sess)
        input_check = explain_util.check_input(request.form['num_feat'], request.form['top_labels'], len(new_features),
                                               1 if labels is None else len(labels))
        if input_check is not None:
            return jsonify(explanation=input_check)
        if sess.mode_is_canned():
            all_params_config.set_canned_data(sess.get_canned_data())
        result = th.explain_estimator(all_params_config, sess.get_features(), sess.get_targets(), labels,
                                      sess.get_defaults(), dtypes, new_features, sess.get_df(),
                                      sess.get_cat(), int(request.form['num_feat']),
                                      int(request.form['top_labels']), request.form['exp_target'])
        return jsonify(explanation=explain_util.explain_return(sess, new_features, result))
    else:
        return render_template('explain.html', title="Explain", page=5, graphs=sess.get_dict_graps(),
                               predict_table=sess.get_dict_table(), features=sess.get_new_features(),
                               model=sess.get_model(), exp_target=sess.get_exp_target(), type=sess.get_type(),
                               user=session['user'], token=session['token'])


@app.route('/test', methods=['POST', 'GET'])
@login_required
@check_config
def test():
    if 'filename' in request.get_json():
        test_file = request.get_json()['filename'].split('.csv')[0]
        try:
            test_filename = sess.get_file().replace(sess.get_dataset_name() + '.csv', test_file + '-uploaded.csv')
            df = sys_ops.bytestr2df(request.get_json()['file'], test_filename)
            has_targets = sys_ops.check_df(df, sess.get_df(), sess.get_targets(), test_filename)
        except ValueError:
            return jsonify(result="The file contents are not valid.")
    else:
        test_filename = sess.get_test_file()
        has_targets = True
        df = pd.read_csv(test_filename)
    all_params_config, labels, dtypes = run_utils.create_result_test_parameters(request.get_json()['model'], sess)
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    final_pred = th.predict_test_estimator(all_params_config, sess.get_features(), sess.get_targets(), labels,
                                           sess.get_defaults(), dtypes, test_filename, sess.get_df())
    if final_pred is None:
        return jsonify(result='Model\'s structure does not match the new parameter configuration')

    predict_file = sys_ops.save_results(df, final_pred['preds'], sess.get_targets(), test_filename)
    sess.set_has_targets(has_targets)
    sess.set_predict_file(predict_file)

    store_predictions(has_targets, sess, final_pred, df)
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
    epochs = run_utils.get_step(all_params_config.train_size(), all_params_config.train_batch_size(),
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
    path = os.path.join(main_path, 'train')
    e = parse(script, path, dataset_name)
    if e is not True:
        e = str(e).split("Expecting: ")[0]
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
    file_path = sess.get_predict_file()
    df = pd.read_csv(file_path)
    predict_table = {'data': df.as_matrix().tolist(),
                     'columns': [{'title': v} for v in df.columns.values.tolist()]}
    labels = feature_util.get_target_labels(sess.get_targets(), sess.get_cat(), sess.get_fs())
    metrics = None

    if sess.get_has_targets():
        metrics = get_metrics('classification', sess.get_y_true(), sess.get_y_pred(), labels,
                              logits=sess.get_logits()) if sess.check_key('logits') \
            else get_metrics('regression', sess.get_y_true(), sess.get_y_pred(), labels,
                             target_len=len(sess.get_targets()))

    return render_template('test_prediction.html', token=session['token'], predict_table=predict_table, metrics=metrics,
                           targets=sess.get_targets())


@app.route("/deploy", methods=['GET', 'POST'])
@login_required
@check_config
def deploy():
    all_params_config = config_reader.read_config(sess.get_config_file())
    export_dir = all_params_config.export_dir()
    checkpoints = run_utils.ckpt_to_table(
        run_utils.get_eval_results(export_dir, sess.get_writer(), sess.get_config_file()))
    new_features, all_params_config, labels, dtypes = run_utils.create_result_parameters(request, sess,
                                                                                         default_features=True,
                                                                                         checkpoint=
                                                                                         checkpoints['Model'].values[
                                                                                             -1])
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    pred = th.predict_estimator(all_params_config, sess.get_features(), sess.get_targets(), labels,
                                sess.get_defaults(), dtypes, new_features, sess.get_df(), all=True)
    if pred is None:
        return redirect(url_for('run'))  # flash('Deploy error.', 'error')

    call, d, epred = sys_ops.gen_example(sess.get_targets(), sess.get_data(), sess.get_df(), 'model_name', pred)
    example = {'curl': call, 'd': d, 'output': epred}

    if request.method == 'POST' and 'model_name' in request.form:
        file_path = sys_ops.export_models(export_dir, get_selected_rows(request), request.form['model_name'])
        return send_file(file_path, mimetype='application/zip', attachment_filename=file_path.split('/')[-1],
                         as_attachment=True)
    return render_template('deploy.html', token=session['token'], checkpoints=checkpoints, page=6,
                           form=DeploymentForm(), example=example)


@app.route('/explain_feature', methods=['POST'])
@login_required
@check_config
def explain_feature():
    exp_target = request.get_json()['exp_target']
    exp_feature = request.get_json()['explain_feature']
    all_params_config, labels, dtypes = run_utils.create_result_test_parameters(request.get_json()['model'], sess)
    file_path, unique_val_column = explain_util.generate_ice_df(request, sess.get_df(), sess.get_file(),
                                                                sess.get_targets(), dtypes)
    if sess.mode_is_canned():
        all_params_config.set_canned_data(sess.get_canned_data())
    final_pred = th.predict_test_estimator(all_params_config, sess.get_features(), sess.get_targets(), labels,
                                           sess.get_defaults(), dtypes, file_path, sess.get_df())
    if final_pred is None:
        return jsonify(data='Error')

    lab, probs = explain_util.get_exp_target_prediction(sess.get_targets(), exp_target, final_pred, dtypes)
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
