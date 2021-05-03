import json
from time import sleep

from django.shortcuts import render, redirect
import os

from django.views.decorators.csrf import csrf_exempt

from .models import *
from django.shortcuts import get_object_or_404
from django.http import Http404, HttpResponse
from .forms import DirectoryForm, FileForm, RemoveDirForm, RemoveFileForm

from datetime import datetime

path_to_app = './framacapp'
path_to_linux = 'C:\\Windows\\System32\\wsl.exe'


# Create your views here.
# Checks whether directory or file is in database and whether it should be shown.
def check_dir(name, isfile, user):
    obj = None
    if isfile:
        try:
            obj = File.objects.get(name=name, owner=user)
        except File.DoesNotExist:
            return False
    else:
        try:
            obj = Directory.objects.get(name=name, owner=user)
        except Directory.DoesNotExist:
            return False

    if not obj.availability_flag:
        return False

    while obj.parent is not None:
        parent = obj.parent
        if not parent.availability_flag or not parent.owner == user:
            return False
        obj = parent

    return True


# Lists files from path.
def list_files(path, user):
    ret_str = "Files:<ul>"
    last_level = 0
    number = 0
    for root, dirs, files in os.walk(path):
        level = root.replace(path, '').count(os.sep)
        if not check_dir(os.path.basename(root), False, user) and level != 0:
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
            if not check_dir(f, True, user):
                continue
            ret_str += f'<li style="list-style-image:url(/static/icons/icon.png); height:\'20px\'" ' \
                       f'onclick="get_file_contents(\'{f}\')">{f}</li>\n'
    ret_str += "</ul></div>" * last_level
    ret_str += "</ul>"
    return ret_str


def home_view(request, *args, **kwargs):
    if request.user.is_anonymous:
        return redirect('/login')

    context = {
        'Files': list_files("./framacapp/Files", request.user),
        'User': request.user.username,
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
def group_program_elements(file, program_elements):
    iter1 = program_elements.find('------------------------------------------------------------') + 61
    if iter1 == 60:
        return program_elements
    program_elements = program_elements.replace('<br>', '\n')
    iter1 = program_elements.find('------------------------------------------------------------', iter1) + 62

    program_elements = program_elements[iter1:]
    ret = ""
    number = 0
    for group in program_elements.split('\n------------------------------------------------------------\n'):
        if group == '':
            break
        if 'Function' in group:
            continue
        description = group[:group.find(':')]

        iter1 = group.find('Goal') + 5
        iter2 = group.find('(', iter1) - 1
        goal = group[iter1:iter2]

        iter1 = group.find('>', group.find('Prover')) + 1
        iter2 = group.find('<', iter1)
        prover = group[iter1:iter2]

        status = 'Unknown'
        if 'Valid' in group:
            status = 'Valid'

        number_of_lines = group[:group.find('Prover')].count('\n')

        iter1 = group.find('Prover') + 7
        iter2 = group.find('returns', iter1) - 1
        prover_for_data = group[iter1:iter2]

        iter1 = iter2 + 9
        iter2 = group.find('(', iter1) - 1
        if iter2 == -2:
            iter2 = len(group) - 1
        status_for_data = group[iter1:iter2]
        data = f'<div class="show_hide_div">' \
               f'<div class="hidden_section {status}" id="hidden_section{number}" onclick="unhide_section({number})">' \
               f' Goal : <b style="color:white">{goal}</b><br>... ({number_of_lines} line(s))<br> Prover: {prover_for_data}<br> Status: {status_for_data}' \
               f'</div>' \
               f'<div class="app-elements-section {status}" id="section{number}" onclick="hide_section({number})">' \
               f'<pre class title="{goal}">{group}</pre>' \
               f'</div>' \
               f'</div>'
        ret += data
        Section.objects.create(file=file, goal=goal, description=description, prover=prover, status=status, data=data)
        number += 1
    return ret


def get_program_elements(file):
    ret = ""
    for data in Section.objects.filter(file=file):
        ret += data.data
    return ret


def get_filepath(file):
    path = file.name

    obj = file
    while obj.parent is not None:
        parent = obj.parent
        path = f'{parent.name}/{path}'
        if not parent.availability_flag:
            raise Http404
        obj = parent

    return path


def get_content_from_file(file):
    filepath = get_filepath(file)

    ret = ""
    with open(f'./framacapp/Files/{filepath}') as f:
        ret += f.read()
    return ret


def render_program_elements(file):
    path = get_filepath(file)
    Section.objects.filter(file=file).delete()

    program_elements = ""
    os.system(
        f'{path_to_linux} frama-c -wp -wp-print ./framacapp/Files/{path} >./framacapp/static/log/lastfile.txt')

    with open(f'{path_to_app}/static/log/lastfile.txt') as f:
        program_elements += f.read()

    program_elements = perform_coloring(program_elements)
    program_elements = group_program_elements(file, program_elements)
    return program_elements


def get_result_tab(request, filepath):
    prover = ifNoneEmpty(request.POST.get("prover"))
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


def run_prover(request):
    if request.is_ajax() and request.POST:
        filename = request.POST.get('filename')
        file = get_object_or_404(File, name=filename)

        if not file.availability_flag:
            raise Http404

        result = render_program_elements(file)
        data = {'result': result}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404


def get_result(request):
    if request.is_ajax() and request.POST:
        result = get_result_tab(request, request.POST.get('filename'))
        data = {'result': result}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404


def load_file(request):
    if request.is_ajax() and request.POST:
        filename = request.POST.get('filename')
        file = get_object_or_404(File, name=filename)

        if not file.availability_flag:
            raise Http404

        content = get_content_from_file(file)
        program_elements = get_program_elements(file)
        data = {'content': content, 'program_elements': program_elements}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404


def add_file(request):
    if request.is_ajax() and request.POST:
        whole_form = ""
        whole_form += '<p><label for="id_name">Name:</label><br>'
        whole_form += '<textarea name="name" cols="40" rows="2" maxlength"40" required id="id_name"></textarea></p>'

        whole_form += '<p><label for="id_parent">Parent:</label> <br>' \
                      '<select name="parent" id="id_parent">' \
                      '<option value="" selected>---------</option>'
        for possible_parent in Directory.objects.filter(availability_flag=True, owner=request.user):
            whole_form += f'<option value="{possible_parent.id}">{str(possible_parent)}</option>'
        whole_form += '</select></p>'

        whole_form += '<p><label for="id_description">Description:</label> <br> ' \
                      '<textarea name="description" cols="40" rows="5" id="id_description"></textarea></p>'

        whole_form += '<p><label for="id_Provide_file">Provide file:</label> <br> ' \
                      '<input type="file" name="Provide_file" required id="id_Provide_file"></p>'

        whole_form += '<input type="button" onclick="add_filep()" value="Submit">'
        data = {'form': whole_form}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404


@csrf_exempt
def add_filep(request):
    name = request.POST.get('name')
    parent = request.POST.get('id_parent')
    if parent:
        parent = Directory.objects.get(id=parent)
    description = request.POST.get('description)')
    owner = request.user

    filepath = f'{name}'
    if parent:
        obj = parent
        while obj is not None:
            filepath = f'{obj.name}/{filepath}'
            obj = obj.parent

    with open(f'framacapp/Files/{filepath}', 'wb+') as f:
        for chunk in request.FILES.get('file').chunks():
            f.write(chunk)

    if parent:
        File.objects.create(parent=parent, name=name, description=description, creation_date=datetime.now(),
                            availability_flag=True, owner=owner)
    else:
        File.objects.create(name=name, description=description, creation_date=datetime.now(),
                            availability_flag=True, owner=owner)
    data = {'message': ''}
    return HttpResponse(json.dumps(data), content_type='application/json')


def add_dir(request):
    if request.is_ajax() and request.POST:
        whole_form = ""
        whole_form += '<p><label for="id_name">Name:</label><br>'
        whole_form += '<textarea name="name" cols="40" rows="2" maxlength"40" required id="id_namedir"></textarea></p>'

        whole_form += '<p><label for="id_parent">Parent:</label> <br>' \
                      '<select name="parent" id="id_parentdir">' \
                      '<option value="" selected>---------</option>'
        for possible_parent in Directory.objects.filter(availability_flag=True, owner=request.user):
            whole_form += f'<option value="{possible_parent.id}">{str(possible_parent)}</option>'
        whole_form += '</select></p>'

        whole_form += '<p><label for="id_description">Description:</label> <br> ' \
                      '<textarea name="description" cols="40" rows="5" id="id_descriptiondir"></textarea></p>'

        whole_form += '<input type="button" onclick="add_dirp()" value="Submit">'
        data = {'form': whole_form}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404


@csrf_exempt
def add_dirp(request):
    name = request.POST.get('name')
    parent = request.POST.get('id_parent')
    if parent:
        parent = Directory.objects.get(id=parent)
    description = request.POST.get('description)')
    owner = request.user

    filepath = f'{name}/'
    if parent:
        obj = parent
        while obj is not None:
            filepath = f'{obj.name}/{filepath}'
            obj = obj.parent

    os.mkdir(f'{path_to_app}/Files/{filepath}')

    if parent:
        Directory.objects.create(parent=parent, name=name, description=description, creation_date=datetime.now(),
                                 availability_flag=True, owner=owner)
    else:
        Directory.objects.create(name=name, description=description, creation_date=datetime.now(),
                                 availability_flag=True, owner=owner)
    data = {'message': ''}
    return HttpResponse(json.dumps(data), content_type='application/json')


def remove(request):
    if request.is_ajax() and request.POST:
        whole_form = ""
        whole_form += '<p><label for="id_Remove_Directory">Remove directory:</label><br>' \
                      '<select name="Remove_Directory" required id="id_Remove_Directory">' \
                      '<option value="" selected>---------</option>'

        for directory in Directory.objects.filter(availability_flag=True, owner=request.user):
            whole_form += f'<option value="{directory.id}">{str(directory)}</option>'
        whole_form += '</select></p>'

        whole_form += '<input type="button" onclick="remove(\'dir\')" value="Submit">'

        whole_form += '<p><label for="id_Remove_File">Remove file:</label><br>' \
                      '<select name="Remove_File" required id="id_Remove_File">' \
                      '<option value="" selected>---------</option>'

        for file in File.objects.filter(availability_flag=True, owner=request.user):
            whole_form += f'<option value="{file.id}">{str(file)}</option>'
        whole_form += '</select></p>'

        whole_form += '<input type="button" onclick="remove(\'file\')" value="Submit">'
        data = {'form': whole_form}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404


def removep(request):
    if request.is_ajax():
        id = request.POST.get('id')
        if not id:
            id = -1
        if request.POST.get('isfile') is True:
            File.objects.filter(id=id).update(availability_flag=True)
        else:
            Directory.objects.filter(id=id).update(availability_flag=True)
        data = {'message': ''}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404


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


def reload_tree(request):
    if request.is_ajax():
        sleep(1)
        data = {'tree': list_files("./framacapp/Files", request.user)}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        raise Http404
