from django.db import models


# Create your models here.
class User(models.Model):
    name = models.TextField(max_length=40)
    login = models.TextField(max_length=40)
    password = models.TextField(max_length=40)

    def __str__(self):
        return f"{self.name} : {self.login}"


class Directory(models.Model):
    name = models.TextField(max_length=40)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    availability_flag = models.BooleanField(default=True)

    def __str__(self):
        return f"Dir {self.name}, {self.owner}, {self.availability_flag}"


class File(models.Model):
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE, blank=True, null=True)
    name = models.TextField(max_length=40)
    description = models.TextField(blank=True, null=True)
    creation_date = models.DateTimeField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    availability_flag = models.BooleanField(default=True)

    def __str__(self):
        return f"File {self.name}, {self.owner}, {self.availability_flag}"


class Section(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE, blank=True, null=True)
    goal = models.TextField(max_length=40, blank=True, null=True)
    description = models.TextField(max_length=40, blank=True, null=True)
    prover = models.TextField(max_length=40, blank=True, null=True)
    status = models.TextField(max_length=40)
    data = models.TextField(max_length=40)

    def __str__(self):
        return f"Section for file {self.file.name}, prover : {self.prover}, status : {self.status}"
