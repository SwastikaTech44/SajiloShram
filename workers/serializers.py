from rest_framework import serializers

from .models import WorkerProfile


class WorkerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    municipality = serializers.StringRelatedField()
    skills = serializers.StringRelatedField(many=True)
    verified = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = WorkerProfile
        fields = [
            'id', 'username', 'daily_rate', 'municipality', 'ward_no',
            'skills', 'is_available', 'verified', 'rating',
        ]

    def get_verified(self, obj):
        return obj.nid_status == WorkerProfile.NIDStatus.VERIFIED

    def get_rating(self, obj):
        summary = obj.rating_summary()
        average = summary['average']
        return {
            'average': round(average, 1) if average is not None else None,
            'count': summary['count'],
        }