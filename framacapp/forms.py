from django import forms

from .models import Directory, File


class DirectoryForm(forms.ModelForm):
    class Meta:
        model = Directory
        fields = [
            'name',
            'parent',
            'description',
            'owner'
        ]


class FileForm(forms.ModelForm):
    Provide_file = forms.FileField()

    class Meta:
        model = File
        fields = [
            'name',
            'parent',
            'description',
            'owner'
        ]


class RemoveDirForm(forms.Form):
    Remove_Directory = forms.ModelChoiceField(queryset=Directory.objects.filter(availability_flag=True))


class RemoveFileForm(forms.Form):
    Remove_File = forms.ModelChoiceField(queryset=File.objects.filter(availability_flag=True))
