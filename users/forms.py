from .models import VacationRequest, Employee
from django import forms
from django.contrib.auth.models import User


class VacationRequestForm(forms.ModelForm):
    backup_person = forms.ModelChoiceField(
        queryset=User.objects.none(),  # Initial queryset is empty
        required=False,  # Allow null values
        widget=forms.Select(attrs={"class": "form-select"}),  # Optional styling
    )

    class Meta:
        model = VacationRequest
        fields = [
            "comment",
            "start_date",
            "end_date",
            "backup_person",
            "compensatory_days",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)  # Get the logged-in user from the view
        self.employee = kwargs.pop("employee", None)  # Get the employee instance
        super().__init__(*args, **kwargs)

        # Filter backup_person choices based on the user's team
        if user:
            try:
                employee = Employee.objects.get(user=user)
                team_members = Employee.objects.filter(team=employee.team).exclude(
                    user=user
                )
                self.fields["backup_person"].queryset = User.objects.filter(
                    id__in=team_members.values_list("user_id", flat=True)
                )
            except Employee.DoesNotExist:
                self.fields["backup_person"].queryset = User.objects.none()

        # Override label_from_instance to display full names
        self.fields["backup_person"].label_from_instance = lambda obj: (
            f"{obj.first_name} {obj.last_name}"
            if obj.first_name and obj.last_name
            else obj.username
        )

    def clean_backup_person(self):
        backup_person = self.cleaned_data.get("backup_person")
        if backup_person:
            user = self.instance.employee
            if user:
                employee = Employee.objects.get(user=user)
                team_members = Employee.objects.filter(team=employee.team).exclude(
                    user=user
                )
                if backup_person not in team_members.values_list("user", flat=True):
                    raise forms.ValidationError(
                        "The selected backup person must belong to your team."
                    )
        return backup_person

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")
        compensatory_days = cleaned_data.get("compensatory_days")

        # Ensure dates are valid
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")

        # Ensure compensatory days do not exceed the number of requested days
        if compensatory_days and compensatory_days > (end_date - start_date).days + 1:
            raise forms.ValidationError(
                "Compensatory days cannot exceed the total number of requested days."
            )

        return cleaned_data


class VacationRequestUpdateForm(forms.ModelForm):
    class Meta:
        model = VacationRequest
        fields = ["status", "message"]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }
