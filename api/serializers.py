from rest_framework import serializers
from .models import *


class CategorieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categorie
        fields = ["id",
                  "name",
                  "description",
                  ]


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
        depth = 1


class CategorieVideosSerializer(serializers.ModelSerializer):
    videos = serializers.SerializerMethodField('get_videos')

    def get_videos(self, categorie):
        qs = Video.objects.filter(categorie=categorie)
        serializer = VideoSerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = Categorie
        fields = ["id",
                  "name",
                  "description",
                  "videos"
                  ]


class MonAbonnementSerializer(serializers.ModelSerializer):
    class Meta:
        model = MonAbonnement
        fields = '__all__'


class MonVideoAllSerializer(serializers.ModelSerializer):
    # video = VideoSerializer() # pas besoin puis que je mets depth

    class Meta:
        model = MonVideo
        fields = '__all__'
        depth = 1


class MonVideoClientSerializer(serializers.ModelSerializer):
    video = VideoSerializer()

    class Meta:
        model = MonVideo
        fields = ['id', 'video']


class ClientSerializer(serializers.ModelSerializer):
    monAbonnement = MonAbonnementSerializer()
    # mesVideos = MonVideoClientSerializer(many=True)

    mesVideos = serializers.SerializerMethodField('get_paid_videos')

    def get_paid_videos(self, client):
        qs = client.mesVideos.filter(payer=True)
        serializer = MonVideoClientSerializer(instance=qs, many=True)
        return serializer.data

    class Meta:
        model = Client
        fields = ["id",
                  "email",
                  "username",
                  "monAbonnement",
                  "mesVideos"
                  ]
