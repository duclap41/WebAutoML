import os
import traceback

from django.core.exceptions import SuspiciousOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, FileResponse
from django.views import generic
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from . import models

from .forms import CreateUserForm, ChangeUserForm, UploadUserFileForm, create_choose_features_form
from django.urls import reverse_lazy

import io
import pandas as pd
from AutoML import *
import urllib, base64

class AutoMLView:
    def __init__(self):...

    @classmethod
    def deploy_plot(cls, plot):
        """Deploy plot to website, using buffer."""
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
    def deploy_dataframe(cls, dataframe):
        data = []
        columns = dataframe.columns.tolist()
        for _, row in dataframe.iterrows():
            data.append(row.tolist())
        return columns, data

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
                # return redirect('home')
                return redirect('upload')

            else:
                messages.info(request, 'Username hoặc mật khẩu không đúng')
                # return render(request, 'accounts/signin.html', context)


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

    context = {'form':form}
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

    context = {'form':form}
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

    context = {'form':form}
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
        df = pd.read_csv(user_file.data_file)
        dataframe = df
        columns, data = AutoMLView.deploy_dataframe(df)

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
                df = pd.read_csv(user_file.data_file)
                dataframe = df
                columns, data = AutoMLView.deploy_dataframe(df)

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
    #overview
    eda = EDA(dataframe)
    number_features = len(eda.columns)
    number_samples = eda.entries
    number_outliers, _, _ = eda.checkOutliers()
    number_missval, _ = eda.checkMissing()
    number_duplicate = eda.checkDuplicate()
    number_imbalance, _ = eda.checkImbalance()

    #columns dtype
    df_cols_dtype = eda.examine()
    columns, data = AutoMLView.deploy_dataframe(df_cols_dtype)

    context = {'num_fts': number_features,
               'num_samps': number_samples,
               'num_outs': number_outliers,
               'num_miss': number_missval,
               'num_dups': number_duplicate,
               'num_imbas': number_imbalance,
               'columns': columns,
               'data': data}
    return render(request, 'accounts/overview.html', context)

@login_required(login_url='signin')
def alert(request):
    global dataframe
    eda = EDA(dataframe)

    # Find constant, unique value
    dict_const_uniq = eda.check_constant_unique()
    data_const = dict_const_uniq['Constant']
    data_uniq = dict_const_uniq['Unique Values']

    # Missing values
    _, df_missval = eda.checkMissing()
    cols_missval, data_missval = AutoMLView.deploy_dataframe(df_missval)

    # Imbalance columns
    _, df_imbal = eda.checkImbalance()
    cols_imbal, data_imbal = AutoMLView.deploy_dataframe(df_imbal)

    # Outliers
    _, df_out, plot_out = eda.checkOutliers(size=(10,6), rotate=30, title="Box Plot Outliers")
    cols_out, data_out = AutoMLView.deploy_dataframe(df_out)
    gfx_out = AutoMLView.deploy_plot(plot_out)

    context = {'data_const': data_const,
               'data_uniq': data_uniq,
               'cols_missval': cols_missval,
               'data_missval': data_missval,
               'cols_imbal': cols_imbal,
               'data_imbal': data_imbal,
               'cols_out': cols_out,
               'data_out': data_out,
               'gfx_out': gfx_out}
    return render(request, 'accounts/alert.html', context)

@login_required(login_url='signin')
def features(request):
    global dataframe
    eda = EDA(dataframe)
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
    _, plot_corr = eda.correlation(rotate=30)
    gfx_corr = AutoMLView.deploy_plot(plot_corr)

    context = {'columns': columns,
               'gfx_distri': gfx_distri,
               'col_distri': col_distri,
               'gfx_inter': gfx_inter,
               'col_inter1': col_inter1,
               'col_inter2': col_inter2,
               'gfx_corr': gfx_corr,
               }
    return render(request, 'accounts/features.html', context)

@login_required(login_url='signin')
def reproduction(request):
    context = {}
    return render(request, 'accounts/reproduction.html', context)

@login_required(login_url='signin')
def history(request):
    user_files = models.UserFile.objects.all()
    context = {'files': user_files}
    return render(request, 'accounts/history.html', context)

@login_required(login_url='signin')
def model(request):
    def get_value_error(traceback_str):
        value_error_lines = []
        for line in traceback_str.split('\n'):
            if 'ValueError:' in line:
                value_error_lines.append(line.strip())
        return value_error_lines

    global dataframe
    md = Model(dataframe)
    columns = dataframe.columns
    col_model = columns[1]
    loading = True
    drop_columns = []

    ChooseFeatureForm = create_choose_features_form(columns)
    if request.method == 'POST':
        col_model = request.POST.get('col_model')

        # Choose features
        form_choose_features = ChooseFeatureForm(request.POST)
        if form_choose_features.is_valid():
            drop_columns = [form_choose_features.fields[f'checkbox_{i}'].label for i in range(len(columns)) if
                             form_choose_features.cleaned_data[f'checkbox_{i}'] is False]

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
            user_file.save()

        except Exception as e:
            error_message = get_value_error(traceback.format_exc())

        loading = False

        if error_message is not None:
            context = {'columns': columns,
                       'col_picked': col_model,
                       'choose_features': [],
                       'cols_compare': [],
                       'data_compare': [],
                       'form': form_choose_features,
                       'loading': loading,
                       'error': error_message}
            return render(request, 'accounts/model.html', context)

        context = {'columns': columns,
                   'col_picked': col_model,
                   'choose_features': dataframe.drop(drop_columns + [col_model], axis=1).columns.tolist(),
                   'cols_compare': cols_compare,
                   'data_compare': data_compare,
                   'form': form_choose_features,
                   'loading': loading,
                   'error': error_message}
        return render(request, 'accounts/model.html', context)

    else:
        form_choose_features = ChooseFeatureForm()

    context = {'columns': columns,
               'col_model': col_model,
               'loading': loading,
               'form': form_choose_features}
    return render(request, 'accounts/model.html', context)
