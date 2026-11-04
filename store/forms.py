from django import forms
from .models import ReviewRatings


class ReviewForms(forms.ModelForm):

    class Meta:
        model = ReviewRatings
        fields = ['subject', 'review', 'raiting']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['subject'].required = True
        self.fields['review'].required = True

    def clean_raiting(self):
        rating = self.cleaned_data['raiting']

        if rating not in [1, 2, 3, 4, 5]:
            raise forms.ValidationError(
                "Rating must be between 1 and 5 stars."
            )

        return rating
