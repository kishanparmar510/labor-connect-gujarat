from django import forms
from django.contrib.auth.models import User
from .models import WorkerProfile, Review, SKILL_CHOICES, LOCATION_CHOICES

class WorkerRegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, help_text="Used for logging in")
    password = forms.CharField(widget=forms.PasswordInput(), help_text="Choose a secure password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Password")
    email = forms.EmailField(required=False)

    class Meta:
        model = WorkerProfile
        fields = ['name', 'mobile_number', 'whatsapp_number', 'skill', 'experience', 'location', 'daily_rate', 'bio']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe your experience, working style, and availability...'}),
            'daily_rate': forms.NumberInput(attrs={'placeholder': 'Target daily wage (₹) optional'}),
            'mobile_number': forms.TextInput(attrs={'placeholder': '10-digit mobile number'}),
            'whatsapp_number': forms.TextInput(attrs={'placeholder': 'WhatsApp number (optional)'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another one.")
        return username

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        # Simple phone validation
        if not mobile.isdigit() or len(mobile) < 10 or len(mobile) > 12:
            raise forms.ValidationError("Please enter a valid mobile number.")
        if WorkerProfile.objects.filter(mobile_number=mobile).exists():
            raise forms.ValidationError("A profile with this mobile number already exists.")
        return mobile

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        # Create User
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data.get('email', ''),
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['name']
        )
        # Create Profile
        profile = super().save(commit=False)
        profile.user = user
        if commit:
            profile.save()
        return profile


class WorkerProfileForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        fields = ['name', 'mobile_number', 'whatsapp_number', 'experience', 'location', 'daily_rate', 'bio', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'daily_rate': forms.NumberInput(attrs={'placeholder': '₹'}),
        }

    def clean_mobile_number(self):
        mobile = self.cleaned_data.get('mobile_number')
        if not mobile.isdigit() or len(mobile) < 10 or len(mobile) > 12:
            raise forms.ValidationError("Please enter a valid mobile number.")
        
        # Ensure mobile is unique except for current profile
        qs = WorkerProfile.objects.filter(mobile_number=mobile)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("A profile with this mobile number already exists.")
        return mobile


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['customer_name', 'rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'rating-select'}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your honest review here...'}),
            'customer_name': forms.TextInput(attrs={'placeholder': 'Your Name'}),
        }
