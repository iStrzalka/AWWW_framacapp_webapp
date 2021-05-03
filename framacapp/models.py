from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


# Create your models here.
class AccountManager(BaseUserManager):
    def create_user(self, username, name, password=None):
        if not username:
            raise ValueError("Provide username")
        if not name:
            raise ValueError("Provide your name")
        user = self.model(
            username=username,
            name=name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, name, password=None):
        user = self.create_user(
            username=username,
            name=name,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def delete_user(self):
        self.User.delete()


class User(AbstractBaseUser):
    name = models.TextField(max_length=40)
    username = models.TextField(max_length=40, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['name']

    objects = AccountManager()

    def __str__(self):
        return f"Username : {self.username}"

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True


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
