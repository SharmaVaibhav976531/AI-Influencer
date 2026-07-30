from django.db.models import Count, Case, When, IntegerField
from django.db.models.functions import TruncDate

def get_chart_data(influencer_qs, classification_qs, upload_qs):
    # 1. Language Distribution (Pie)
    lang_data = influencer_qs.values('language_detected').annotate(count=Count('id')).order_by('-count')
    language_chart = {
        'labels': [item['language_detected'] or 'Unknown' for item in lang_data],
        'data': [item['count'] for item in lang_data]
    }
    
    # 2. Platform Distribution (Bar)
    plat_data = influencer_qs.values('platform').annotate(count=Count('id')).order_by('-count')
    platform_chart = {
        'labels': [item['platform'] for item in plat_data],
        'data': [item['count'] for item in plat_data]
    }
    
    # 3. Overall Score Distribution (Bar)
    score_buckets = classification_qs.annotate(
        bucket=Case(
            When(overall_score__lte=20, then=1),
            When(overall_score__lte=40, then=2),
            When(overall_score__lte=60, then=3),
            When(overall_score__lte=80, then=4),
            default=5,
            output_field=IntegerField()
        )
    ).values('bucket').annotate(count=Count('id')).order_by('bucket')
    
    score_labels = ['0-20', '21-40', '41-60', '61-80', '81-100']
    score_data = [0] * 5
    for item in score_buckets:
        score_data[item['bucket'] - 1] = item['count']
    score_chart = {'labels': score_labels, 'data': score_data}
    
    # 4. Recommendation Distribution (Pie)
    rec_data = classification_qs.values('recommendation').annotate(count=Count('id')).order_by('-count')
    recommendation_chart = {
        'labels': [item['recommendation'] for item in rec_data],
        'data': [item['count'] for item in rec_data]
    }
    
    # 5. Orientation Distribution (Bar)
    orient_data = classification_qs.values('orientation_match').annotate(count=Count('id'))
    orient_labels = ['Supportive', 'Unknown/Neutral']
    orient_data_map = [0, 0]
    for item in orient_data:
        if item['orientation_match']:
            orient_data_map[0] = item['count']
        else:
            orient_data_map[1] = item['count']
    orientation_chart = {'labels': orient_labels, 'data': orient_data_map}
    
    # 6. Followers Distribution (Bar)
    fol_buckets = influencer_qs.annotate(
        bucket=Case(
            When(followers__lte=10000, then=1),
            When(followers__lte=50000, then=2),
            When(followers__lte=100000, then=3),
            When(followers__lte=500000, then=4),
            When(followers__lte=1000000, then=5),
            default=6,
            output_field=IntegerField()
        )
    ).values('bucket').annotate(count=Count('id')).order_by('bucket')
    
    fol_labels = ['0-10K', '10K-50K', '50K-100K', '100K-500K', '500K-1M', '1M+']
    fol_data = [0] * 6
    for item in fol_buckets:
        fol_data[item['bucket'] - 1] = item['count']
    followers_chart = {'labels': fol_labels, 'data': fol_data}
    
    # 7. Upload Trend (Line)
    upload_trend = upload_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    upload_trend_chart = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in upload_trend if item['date']],
        'data': [item['count'] for item in upload_trend if item['date']]
    }
    
    # 8. Classification Trend (Line)
    class_trend = classification_qs.annotate(date=TruncDate('created_at')).values('date').annotate(count=Count('id')).order_by('date')
    classification_trend_chart = {
        'labels': [item['date'].strftime('%Y-%m-%d') for item in class_trend if item['date']],
        'data': [item['count'] for item in class_trend if item['date']]
    }
    
    return {
        'language': language_chart,
        'platform': platform_chart,
        'score': score_chart,
        'recommendation': recommendation_chart,
        'orientation': orientation_chart,
        'followers': followers_chart,
        'upload_trend': upload_trend_chart,
        'classification_trend': classification_trend_chart,
    }