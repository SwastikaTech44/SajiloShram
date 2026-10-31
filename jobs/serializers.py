from rest_framework import serializers

from .models import Job


class JobSerializer(serializers.ModelSerializer):
    employer = serializers.CharField(source='employer.username', read_only=True)
    worker = serializers.CharField(source='worker.username', read_only=True)
    status_label = serializers.CharField(source='get_status_display', read_only=True)
    review = serializers.SerializerMethodField()

    class Meta:
        model = Job
        fields = [
            'id', 'employer', 'worker', 'description', 'agreed_wage',
            'start_date', 'work_location', 'terms', 'accepted_at',
            'status', 'status_label', 'created_at', 'updated_at', 'review',
        ]

    def get_review(self, obj):
        review = getattr(obj, 'review', None)
        if review is None:
            return None
        return {'rating': review.rating, 'comment': review.comment}