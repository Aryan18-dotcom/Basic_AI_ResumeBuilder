from rest_framework import serializers
from .models import UserDetails, UserResume

class JobDescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserDetails
        fields = '__all__'

class ResumeSerializer(serializers.ModelSerializer):
    analysis_result = serializers.JSONField(read_only=True)
    
    class Meta:
        model = UserResume
        fields = '__all__'