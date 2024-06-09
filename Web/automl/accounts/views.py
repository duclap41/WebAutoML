import base64
import urllib
import io
import os
import traceback

import pandas as pd
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.core.files.storage import default_storage
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from pandas.core.frame import DataFrame

from AutoML import *
from . import models
from .forms import CreateUserForm, ChangeUserForm, UploadUserFileForm, create_choose_features_form


class AutoMLView:
    def __init__(self, data_frame: DataFrame):
        self._df = dataframe

    @classmethod
    def read_file(cls, data_file):
        """Read data file, uploaded from local, format file: csv, excel, json"""
        df = pd.DataFrame()
        file_path = default_storage.path(data_file.name)
        file_extension = os.path.splitext(file_path)[1]
        if file_extension.lower() == '.csv':
            df = pd.read_csv(file_path)
        elif file_extension.lower() in ['.xls', '.xlsx']:
            df = pd.read_excel(file_path)
        elif file_extension.lower() == '.json':
            df = pd.read_json(file_path)

        return df

    @classmethod
    def deploy_plot(cls, plot):
        """Handle a plots for web deployment, using buffer."""
        buffer = io.BytesIO()
        plot.savefig(buffer, format='png')
        plot.clf()
        buffer.seek(0)
        img_plot = buffer.getvalue()
        buffer.close()
        graphic = base64.b64encode(img_plot)
        graphic = graphic.decode('utf-8')

        return graphic

    @classmethod
    def deploy_dataframe(cls, data_frame):
        """Handle a Dataframe for web deployment """
        data = []
        columns = data_frame.columns.tolist()
        for _, row in data_frame.iterrows():
            data.append(row.tolist())
        return columns, data

    def deploy_overview(self) -> dict:
        """Deploy overview section to website"""
        eda = EDA(self._df)
        number_features = len(eda.columns)
        number_samples = eda.entries
        number_outliers, _, _ = eda.check_outliers()
        number_miss_value, _ = eda.check_miss_value()
        number_duplicate = eda.check_duplicate()
        number_imbalance, _ = eda.check_imbalance()

        # columns dtype
        df_cols_dtype = eda.examine()
        columns, data = AutoMLView.deploy_dataframe(df_cols_dtype)

        context = {'num_fts': number_features,
                   'num_samps': number_samples,
                   'num_outs': number_outliers,
                   'num_miss': number_miss_value,
                   'num_dups': number_duplicate,
                   'num_imbas': number_imbalance,
                   'columns': columns,
                   'data': data}
        return context

    def deploy_alert(self):
        """Deploy alert section to website"""
        eda = EDA(self._df)
        # Find constant, unique value
        dict_const_uniq = eda.check_constant_unique()
        data_const = dict_const_uniq['Constant']
        data_uniq = dict_const_uniq['Unique Values']

        # Missing values
        _, df_miss_value = eda.check_miss_value()
        cols_miss_value, data_miss_value = AutoMLView.deploy_dataframe(df_miss_value)

        # Imbalance columns
        _, df_imbalance = eda.check_imbalance()
        cols_imbalance, data_imbalance = AutoMLView.deploy_dataframe(df_imbalance)

        # Outliers
        _, df_out, plot_out = eda.check_outliers(size=(10, 6), rotate=30, title="Box Plot Outliers")
        cols_out, data_out = AutoMLView.deploy_dataframe(df_out)
        gfx_out = AutoMLView.deploy_plot(plot_out)

        context = {'data_const': data_const,
                   'data_uniq': data_uniq,
                   'cols_missval': cols_miss_value,
                   'data_missval': data_miss_value,
                   'cols_imbal': cols_imbalance,
                   'data_imbal': data_imbalance,
                   'cols_out': cols_out,
                   'data_out': data_out,
                   'gfx_out': gfx_out}
        return context

    def deploy_features(self, request):
        """Deploy features section to website"""
        eda = EDA(self._df)
        columns = eda.columns
        gfx_distri = None
        gfx_inter = None

        # Feature distribution
        col_distri = columns[1]
        if request.method == 'POST':
            if 'col_distri' in request.POST:
                col_distri = request.POST.get('col_distri')
        plot_distri = eda.distribution(column=col_distri, size=(8, 6))
        gfx_distri = AutoMLView.deploy_plot(plot_distri)

        # Features interaction
        col_inter1 = columns[1]
        col_inter2 = columns[2]
        if request.method == 'POST':
            if 'col_inter1' in request.POST:
                col_inter1 = request.POST.get('col_inter1')
            if 'col_inter2' in request.POST:
                col_inter2 = request.POST.get('col_inter2')
        plot_inter = eda.interaction(col_inter1, col_inter2)
        gfx_inter = AutoMLView.deploy_plot(plot_inter)

        # Feature Correlation
        _, plot_corr = eda.correlation(visual=True, rotate=30)
        gfx_corr = AutoMLView.deploy_plot(plot_corr)

        context = {'columns': columns,
                   'gfx_distri': gfx_distri,
                   'col_distri': col_distri,
                   'gfx_inter': gfx_inter,
                   'col_inter1': col_inter1,
                   'col_inter2': col_inter2,
                   'gfx_corr': gfx_corr,
                   }
        return request, context

    def deploy_suggestion(self):
        """Deploy suggestion section to website"""
        sg_process = SuggestPreprocess(self._df)

        sg_constant_unique = sg_process.sg_constant_unique()
        sg_miss_value = sg_process.sg_miss_value()
        sg_imbalance = sg_process.sg_imbalance()
        sg_outlier = sg_process.sg_outlier()
        sg_correlate = sg_process.sg_correlate()

        list_suggestion = [sg_constant_unique, sg_miss_value, sg_imbalance, sg_outlier, sg_correlate]

        # Drop empty suggestion
        for sg in list_suggestion:
            if len(sg) == 1:
                list_suggestion.remove(sg)

        context = {'suggestion': list_suggestion}
        return context

    @classmethod
    def deploy_history(cls, user_files):
        """Deploy history section to website"""
        context = {'files': user_files}
        return context

    def deploy_model(self, request):
        """Deploy model section to website"""
        def get_value_error(traceback_str):
            value_error_lines = []
            for line in traceback_str.split('\n'):
                if 'ValueError:' in line:
                    value_error_lines.append(line.strip())
            return value_error_lines

        data_frame = self._df
        md = Model(data_frame)
        columns = data_frame.columns
        col_model = []
        loading = True
        drop_columns = []
        choose_features = []
        cols_compare = []
        data_compare = []

        ChooseFeatureForm = create_choose_features_form(columns)
        if request.method == 'POST':
            col_model = request.POST.get('col_model')

            # Choose features
            form_choose_features = ChooseFeatureForm(request.POST)
            if form_choose_features.is_valid():
                drop_columns = [form_choose_features.fields[f'checkbox_{i}'].label for i in range(len(columns)) if
                                form_choose_features.cleaned_data[f'checkbox_{i}'] is False]
                choose_features = data_frame.drop(drop_columns + [col_model], axis=1).columns.tolist()

            # Run model
            error_message = None
            try:
                if md.check_type(target_col=col_model) in ["Discrete", "Categorical"]:
                    _, df_compare = md.classify_models(target_col=col_model, drop_features=drop_columns)
                    best_model = df_compare['Model'][0]
                    best_result = f"{df_compare['Accuracy'][0]} (Accuracy)"
                else:
                    _, df_compare = md.regressor_models(target_col=col_model, drop_features=drop_columns)
                    best_model = df_compare['Model'][0]
                    best_result = f"{df_compare['MAE'][0]} (MAE)"

                cols_compare, data_compare = AutoMLView.deploy_dataframe(df_compare)

                # save to database
                global curr_id
                if curr_id is not None:
                    user_file = get_object_or_404(models.UserFile, id=curr_id)

                else:
                    latest_user_file = models.UserFile.objects.order_by('-id').first()
                    user_file = get_object_or_404(models.UserFile, id=latest_user_file.id)

                user_file.best_model = best_model
                user_file.best_result = best_result
                user_file.last_target = col_model
                user_file.last_features = ', '.join(choose_features)
                user_file.save()

            except Exception as e:
                error_message = get_value_error(traceback.format_exc())

            loading = False

            if error_message is not None:
                context = {'columns': columns,
                           'col_picked': col_model,
                           'choose_features': choose_features,
                           'cols_compare': cols_compare,
                           'data_compare': data_compare,
                           'form': form_choose_features,
                           'loading': loading,
                           'error': error_message}
                return request, context

            context = {'columns': columns,
                       'col_picked': col_model,
                       'choose_features': choose_features,
                       'cols_compare': cols_compare,
                       'data_compare': data_compare,
                       'form': form_choose_features,
                       'loading': loading,
                       'error': error_message}
            return request, context

        else:
            form_choose_features = ChooseFeatureForm()

        context = {'columns': columns,
                   'col_model': col_model,
                   'loading': loading,
                   'form': form_choose_features}
        return request, context

@login_required(login_url='signin')
def home(request):
    return render(request, 'accounts/homepage.html')


@login_required(login_url='signin')
def contact(request):
    return HttpResponse('Contact Page')


def signin(request):
    if request.user.is_authenticated:
        return redirect('upload')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')

            else:
                messages.info(request, 'Username hoặc mật khẩu không đúng')

    context = {}
    return render(request, 'accounts/signin.html', context)


def logoutUser(request):
    logout(request)
    return redirect('signin')


def signup(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Tài khoản ' + user + ' đã được tạo thành công')

    context = {'form': form}
    return render(request, 'accounts/signup.html', context)


@login_required(login_url='signin')
def editprofile(request):
    if request.method == 'POST':
        form = ChangeUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            user = form.cleaned_data.get('username')
            messages.success(request, 'Tài khoản ' + user + ' đã được cập nhật thành công')
    else:
        form = ChangeUserForm(instance=request.user)

    context = {'form': form}
    return render(request, 'accounts/editprofile.html', context)


@login_required(login_url='signin')
def changepassword(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Tài khoản đã cập nhật mật khẩu thành công')
    else:
        form = PasswordChangeForm(user=request.user)

    context = {'form': form}
    return render(request, 'accounts/changepassword.html', context)


dataframe = pd.DataFrame()
curr_id = None


@login_required
def upload(request):
    global dataframe
    if 'file_id' in request.GET:
        form = UploadUserFileForm()
        file_id = request.GET['file_id']
        global curr_id
        curr_id = file_id
        user_file = models.UserFile.objects.get(pk=file_id)

        dataframe = AutoMLView.read_file(user_file.data_file)
        columns, data = AutoMLView.deploy_dataframe(dataframe)

        context = {'form': form,
                   'data': data,
                   'columns': columns}
        return render(request, 'accounts/upload.html', context)
    else:
        # upload file
        if request.method == 'POST':
            form = UploadUserFileForm(request.POST, request.FILES)
            if form.is_valid():
                user_file = form.save(commit=False)
                user_file.user = request.user
                user_file.save()
                messages.info(request, 'Upload File thành công')

                # load new dataset
                dataframe = AutoMLView.read_file(user_file.data_file)
                columns, data = AutoMLView.deploy_dataframe(dataframe)

                context = {'form': form,
                           'data': data,
                           'columns': columns}
                return render(request, 'accounts/upload.html', context)
        else:
            form = UploadUserFileForm()

        context = {'form': form}
        return render(request, 'accounts/upload.html', context)


@login_required(login_url='signin')
def profile(request):
    context = {}
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='signin')
def overview(request):
    global dataframe
    ml_view = AutoMLView(dataframe)
    context = ml_view.deploy_overview()

    return render(request, 'accounts/overview.html', context)


@login_required(login_url='signin')
def alert(request):
    global dataframe
    ml_view = AutoMLView(dataframe)
    context = ml_view.deploy_alert()

    return render(request, 'accounts/alert.html', context)


@login_required(login_url='signin')
def features(request):
    global dataframe
    ml_view = AutoMLView(dataframe)
    request, context = ml_view.deploy_features(request)
    return render(request, 'accounts/features.html', context)


@login_required(login_url='signin')
def suggestion(request):
    global dataframe
    ml_view = AutoMLView(dataframe)
    context = ml_view.deploy_suggestion()
    return render(request, 'accounts/suggestion.html', context)


@login_required(login_url='signin')
def history(request):
    user_files = models.UserFile.objects.all()
    context = AutoMLView.deploy_history(user_files)
    return render(request, 'accounts/history.html', context)


@login_required(login_url='signin')
def model(request):
    global dataframe
    ml_view = AutoMLView(dataframe)
    request, context = ml_view.deploy_model(request)

    return render(request, 'accounts/model.html', context)
