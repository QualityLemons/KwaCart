from django import forms


class IdeaGenerationForm(forms.Form):
    initial_thought = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Your individual reflection (1 min)...'}),
        label="Phase 1: Self-Reflection"
    )
