from django import forms
from .models import VacationRequest


class VacationRequestForm(forms.ModelForm):
    class Meta:
        model = VacationRequest
        fields = ["start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.employee = kwargs.pop("employee", None)  # Get the employee instance
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        end_date = cleaned_data.get("end_date")

        # Check that start_date is before end_date
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date must be after start date.")

        # Check if requested days exceed available vacation days
        if self.employee:
            requested_days = (end_date - start_date).days + 1
            available_days = self.employee.calculate_available_vacation_days()

            print(f"Requested days: {requested_days}, Available days: {available_days}")

            if requested_days > available_days:
                raise forms.ValidationError(
                    f"You have requested {requested_days} days, but only {available_days} are available."
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
