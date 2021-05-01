import subprocess
import asyncio

from django.shortcuts import render
import os
from .models import *
from django.shortcuts import get_object_or_404
from django.http import Http404
import io
from .forms import DirectoryForm, FileForm, RemoveDirForm, RemoveFileForm

from datetime import datetime


# Create your views here.
def user_view(request, *args, **kwargs):
    user = User.objects.get(id=1)
    context = {
        'name': user.name
    }
    return render(request, "user.html", context)


def check_dir(name, isfile):
    obj = None
    if isfile:
        try:
            obj = File.objects.get(name=name)
        except File.DoesNotExist:
            return False
    else:
        try:
            obj = Directory.objects.get(name=name)
        except Directory.DoesNotExist:
            return False

    if not obj.availability_flag:
        return False

    while obj.parent is not None:
        parent = obj.parent
        if not parent.availability_flag:
            return False
        obj = parent

    return True


def list_files(startpath):
    ret_str = "Files:<ul>"
    last_level = 0
    number = 0
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        if not check_dir(os.path.basename(root), False) and level != 0:
            continue
        if level == 0:
            # ret_str += f'<li class="current">{indent}{os.path.basename(root)}/</li><ul>'
            pass
        elif last_level < level:
            ret_str += f'<li class="current" onclick="toggleChildren(\'List{number}\')" ' \
                       f'style="list-style-image:url(/static/icons/folder.jpg); height:\'20px\'">'
            ret_str += f'{os.path.basename(root)}/</li>'
            ret_str += f'<div class="sub_cat_box" id="List{number}"><ul>'
            number += 1
        else:
            ret_str += '</ul></div>' * (last_level - level + 1)
            ret_str += f'<li class="current" onclick="toggleChildren(\'List{number}\')" ' \
                       f'style="list-style-image:url(/static/icons/folder.jpg); height:\'20px\'">' \
                       f'{os.path.basename(root)}/</li>'
            ret_str += f'<div class="sub_cat_box" id="List{number}"><ul>'
            number += 1
        last_level = level
        for f in files:
            if not check_dir(f, True):
                continue
            ret_str += f'<li style="list-style-image:url(/static/icons/icon.png); height:\'20px\'" ' \
                       f'onclick="location.href = \'/file/{f}\';">{f}</li>\n'
    ret_str += "</ul></div>" * last_level
    ret_str += "</ul>"
    return ret_str


def home_view(request, *args, **kwargs):
    context = {
        'Files': list_files("./framacapp/Files"),
    }
    return render(request, "main.html", context)


def upload_file_view(request, *args, **kwargs):
    context = {

    }
    return render(request, "uploadfile.html", context)


def ifNoneEmpty(obj):
    if obj is None:
        return ""
    return obj


def perform_coloring(input_string):
    input_string = input_string.replace('\n', '<br>')
    input_string = input_string.replace('Valid', '<b style="color:green">Valid</b>')
    input_string = input_string.replace('Unknown', '<b style="color:red">Unknown</b>')
    input_string = input_string.replace('Failed', '<b style="color:red">Failed</b>')
    input_string = input_string.replace('Qed', '<b style="color:yellow">Qed</b>')
    input_string = input_string.replace('Alt-Ergo', '<b style="color:yellow">Alt-Ergo</b>')
    input_string = input_string.replace('Z3', '<b style="color:yellow">Z3</b>')
    input_string = input_string.replace('CVC4', '<b style="color:yellow">CVC4</b>')
    return input_string


def group_program_elements(str):
    iter = str.find('------------------------------------------------------------') + 61
    if iter == 60:
        return str
    str = str.replace('<br>', '\n')
    iter = str.find('------------------------------------------------------------', iter) + 62

    str = str[iter:]
    ret = ""
    for group in str.split('\n------------------------------------------------------------\n'):
        if group == '':
            break
        iter = group.find('Goal') + 5
        iter2 = group.find('(', iter) - 1
        proved = 'Unknown'
        if 'Valid' in group:
            proved = 'Valid'
        ret += f'<div class="app-elements-section {proved}"><pre class title="{group[iter:iter2]}">'
        ret += group
        ret += '</pre></div>'
    return ret


def file_view(request, filename, *args, **kwargs):
    file = get_object_or_404(File, name=filename)

    if not file.availability_flag:
        raise Http404

    filepath = f'{filename}'

    obj = file
    while obj.parent != None:
        parent = obj.parent
        filepath = f'{parent.name}/{filepath}'
        if not parent.availability_flag:
            raise Http404
        obj = parent

    filecontent = ""
    with open(f'./framacapp/Files/{filepath}') as f:
        filecontent += f.read()

    program_elements = ""

    path = os.getcwd() + '\\framacapp\\Files\\' + filepath

    os.system(
        f'C:\Windows\System32\wsl.exe frama-c -wp -wp-print ./framacapp/Files/{filepath} >./framacapp/static/log/lastfile.txt')

    with open('./framacapp/static/log/lastfile.txt') as f:
        program_elements += f.read()

    for item in request.POST.items():
        print(item)

    prover = ifNoneEmpty(request.POST.get("prover_name"))
    if prover != '':
        prover = f' -wp-prover {prover} '
    wp_rte = ifNoneEmpty(request.POST.get("wp_rte"))
    if wp_rte == 'on':
        wp_rte = ' -wp-rte '
    wp_propflag = ifNoneEmpty(request.POST.get("wp_propflag"))
    if wp_propflag != '':
        wp_propflag = f' -wp-prop="{wp_propflag}" '

    result = ''
    if prover + wp_rte + wp_propflag != '':
        os.system(
            f'C:\Windows\System32\wsl.exe frama-c -wp -wp-log="r:./framacapp/static/log/result.txt" {wp_rte} {prover} {wp_propflag}'
            f' ./framacapp/Files/{filepath} >./framacapp/static/log/useless.txt')

        with open('./framacapp/static/log/result.txt') as f:
            result += f.read()

    program_elements = perform_coloring(program_elements)
    result = perform_coloring(result)

    program_elements = group_program_elements(program_elements)

    context = {
        'Files': list_files("./framacapp/Files"),
        'filecontent': filecontent,
        'programelements': program_elements,
        'result': result,
        'resulturl': f"/file/{filename}",
    }
    return render(request, "main.html", context)


def add_file_view(request, *args, **kwargs):
    form = FileForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        dir = form.save(commit=False)
        dir.creation_date = datetime.now()
        dir.availability_flag = True
        dir.save()

        filepath = f'{dir.name}'
        obj = dir
        while obj.parent != None:
            parent = obj.parent
            filepath = f'{parent.name}/{filepath}'
            obj = parent
        with open(f'framacapp/Files/{filepath}', 'wb+') as f:
            for chunk in request.FILES["Provide_file"].chunks():
                f.write(chunk)
        form = FileForm()
    context = {
        'form': form
    }
    return render(request, "add_file.html", context)


def add_dir_view(request, *args, **kwargs):
    form = DirectoryForm(request.POST or None)
    if form.is_valid():
        dir = form.save(commit=False)
        dir.creation_date = datetime.now()
        dir.availability_flag = True
        dir.save()

        filepath = f'{dir.name}'
        obj = dir
        while obj.parent != None:
            parent = obj.parent
            filepath = f'{parent.name}/{filepath}'
            obj = parent
        os.mkdir(f'framacapp/Files/{filepath}')
        form = DirectoryForm()
    context = {
        'form': form
    }
    return render(request, "add_dir.html", context)


def remove_file_dir_view(request, *args, **kwargs):
    form = RemoveDirForm(request.POST or None)
    if form.is_valid():
        # form.save()
        obj = form.cleaned_data['Remove_Directory']
        obj.availability_flag = False
        obj.save()
        print(obj)
        # obj.save()
        form = RemoveDirForm()

    form2 = RemoveFileForm(request.POST or None)
    if form2.is_valid():
        # obj = form2.save(commit=False)
        # obj.availability_flag = False
        # obj.save()
        obj = form2.cleaned_data['Remove_File']
        print(obj)
        obj.availability_flag = False
        obj.save()
        form2 = RemoveFileForm()

    context = {
        'form': form,
        'form2': form2,
        'Files': list_files("./framacapp/Files"),
    }
    return render(request, "remove_dir_file.html", context)
