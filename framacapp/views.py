import json

from django.shortcuts import render
import os
from .models import *
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from .forms import DirectoryForm, FileForm, RemoveDirForm, RemoveFileForm

from datetime import datetime

path_to_app = './framacapp'
path_to_linux = 'C:\\Windows\\System32\\wsl.exe'


# Create your views here.
# Checks whether directory or file is in database and whether it should be shown.
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


# Lists files from path.
def list_files(path):
    ret_str = "Files:<ul>"
    last_level = 0
    number = 0
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        if not check_dir(os.path.basename(root), False) and level != 0:
            continue
        if level == 0:
            # ret_str += f'<li class="current">{indent}{os.path.basename(root)}/</li><ul>'
            pass
        else:
            if last_level >= level:
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


# Returns empty string if object is not empty.
def ifNoneEmpty(obj):
    if obj is None:
        return ""
    return obj


# Performs coloring on the string.
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


# Groups program elements.
def group_program_elements(program_elements):
    iter1 = program_elements.find('------------------------------------------------------------') + 61
    if iter1 == 60:
        return program_elements
    program_elements = program_elements.replace('<br>', '\n')
    iter1 = program_elements.find('------------------------------------------------------------', iter1) + 62

    program_elements = program_elements[iter1:]
    ret = ""
    for group in program_elements.split('\n------------------------------------------------------------\n'):
        if group == '':
            break
        iter1 = group.find('Goal') + 5
        iter2 = group.find('(', iter1) - 1
        proved = 'Unknown'
        if 'Valid' in group:
            proved = 'Valid'
        ret += f'<div class="app-elements-section {proved}"><pre class title="{group[iter1:iter2]}">'
        ret += group
        ret += '</pre></div>'
    return ret


def get_content_from_file(file, path):
    filepath = f'{path}'

    obj = file
    while obj.parent is not None:
        parent = obj.parent
        filepath = f'{parent.name}/{filepath}'
        if not parent.availability_flag:
            raise Http404
        obj = parent

    ret = ""
    with open(f'./framacapp/Files/{filepath}') as f:
        ret += f.read()
    return ret


def get_program_elements(path):
    program_elements = ""
    os.system(
        f'{path_to_linux} frama-c -wp -wp-print ./framacapp/Files/{path} >./framacapp/static/log/lastfile.txt')

    with open(f'{path_to_app}/static/log/lastfile.txt') as f:
        program_elements += f.read()
    program_elements = perform_coloring(program_elements)
    program_elements = group_program_elements(program_elements)
    return program_elements


def get_result_tab(request, filepath):
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
            f'{path_to_linux} frama-c -wp -wp-log="r:{path_to_app}/static/log/result.txt" {wp_rte} {prover} {wp_propflag}'
            f' {path_to_app}/Files/{filepath} >{path_to_app}/static/log/useless.txt')

        with open('./framacapp/static/log/result.txt') as f:
            result += f.read()
    return perform_coloring(result)


def get_result(request):
    print("was here")
    if request.is_ajax() and request.POST:
        result = get_result_tab(request, request.POST.get('filename'))
        return HttpResponse(json.dumps(result), content_type='application/json')
    else:
        raise Http404


def file_view(request, filename, *args, **kwargs):
    file = get_object_or_404(File, name=filename)

    if not file.availability_flag:
        raise Http404

    content = get_content_from_file(file, filename)
    program_elements = get_program_elements(filename)
    result = get_result_tab(request, filename)

    context = {
        'Files': list_files("./framacapp/Files"),
        'filecontent': content,
        'programelements': program_elements,
        'result': result,
        'resulturl': f"/file/{filename}",
    }
    return render(request, "main.html", context)


def add_file_view(request, *args, **kwargs):
    form = FileForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        file = form.save(commit=False)
        file.creation_date = datetime.now()
        file.availability_flag = True
        file.save()

        filepath = f'{file.name}'
        obj = file
        while obj.parent is not None:
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
        directory = form.save(commit=False)
        directory.creation_date = datetime.now()
        directory.availability_flag = True
        directory.save()

        filepath = f'{directory.name}'
        obj = directory
        while obj.parent is not None:
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
        obj = form.cleaned_data['Remove_Directory']
        obj.availability_flag = False
        obj.save()
        form = RemoveDirForm()

    form2 = RemoveFileForm(request.POST or None)
    if form2.is_valid():
        obj = form2.cleaned_data['Remove_File']
        obj.availability_flag = False
        obj.save()
        form2 = RemoveFileForm()

    context = {
        'form': form,
        'form2': form2,
        'Files': list_files("./framacapp/Files"),
    }
    return render(request, "remove_dir_file.html", context)
