from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm

from .models import Master


class MasterCreationForm(AdminUserCreationForm):
    class Meta(AdminUserCreationForm.Meta):
        model = Master
        fields = ("phone",)


class MasterChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Master
        fields = "__all__"
