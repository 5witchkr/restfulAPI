from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Feed, Reply, Like, Bookmark
import os
from config.settings import MEDIA_ROOT
from uuid import uuid4
from user.models import User
from common.common import CommonResponse, SuccessResponse, SuccessResponseWithData, ErrorResponse



# Create your views here.

class Mainpage(APIView):
    def post(self, request):
        Feeds = Feed.objects.all().order_by('-id')

        email = request.session.get('email', None)
        if email is None:
            return ErrorResponse("정보를 찾을 수 없음 로그인을 하세요.")
        nickname = User.objects.filter(email=email).first()
        if nickname is None:
            return ErrorResponse("유저정보를 찾을 수 없음.")


        pageNumber = request.data.get('pageNumber')
        isLastPage = True
        if pageNumber is not None and pageNumber >= 0:
            if Feeds.count() <= 10:
                pass
            elif Feeds.count() <= (1 + pageNumber) * 10:
                Feeds = Feeds[pageNumber * 10:]
            else:
                isLastPage = False
                Feeds = Feeds[pageNumber * 10:(1 + pageNumber) * 10]
        else:
            pass


        Feed_list = []

        for i in Feeds:
            replyObjectList = Reply.objects.filter(feedId=i.id)
            replyList = []
            for reply in replyObjectList:
                replyList.append(dict(replyFeed=reply.replyFeed,
                                      nickname=reply.nickname))

            Feed_list.append(dict(feedId=i.id,
                                  nickname=i.nickname,
                                  subject=i.subject,
                                  content=i.content,
                                  image=i.image,
                                  create_date=i.create_date,
                                  done=i.done,
                                  replyList=replyList
                                  ))

        return SuccessResponseWithData(dict(Feeds=Feed_list, isLastPage=isLastPage))


class FeedCreate(APIView):
    def post(self, request):

        email = request.session.get('email', None)
        if email is None:
            return ErrorResponse("정보를 찾을 수 없음 로그인을 하세요.")
        nickname = User.objects.filter(email=email).first()
        if nickname is None:
            return ErrorResponse("유저정보를 찾을 수 없음.")

        file = request.data.get('file', '')
        if file:
            file = request.FILES['file']
            uuid_name = uuid4().hex
            save_path = os.path.join(MEDIA_ROOT, uuid_name)

            with open(save_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            image = uuid_name
        else:
            image = request.data.get('image', '')

        subject = request.data.get('subject')
        content = request.data.get('content')

        Feed.objects.create(image=image, content=content, nickname=nickname, subject=subject)

        return SuccessResponse()



class FeedToggle(APIView):
    def post(self, request):

        email = request.session.get('email', None)
        if email is None:
            return ErrorResponse("정보를 찾을 수 없음 로그인을 하세요.")
        nickname = User.objects.filter(email=email).first()
        if nickname is None:
            return ErrorResponse("유저정보를 찾을 수 없음.")

        feedId = request.data.get('feedId', '')
        feed = Feed.objects.get(id=feedId)
        if str(feed.nickname) == str(nickname):
            if feed:
                feed.done = False if feed.done is True else True
                feed.save()
            return SuccessResponse()
        else:
            return ErrorResponse("권한이 없습니다.")



class FeedDelete(APIView):
    def post(self, request):

        email = request.session.get('email', None)
        if email is None:
            return ErrorResponse("정보를 찾을 수 없음 로그인을 하세요.")
        nickname = User.objects.filter(email=email).first()
        if nickname is None:
            return ErrorResponse("유저정보를 찾을 수 없음.")

        feedId = request.data.get('feedId', '')
        feed = Feed.objects.get(id=feedId)
        if str(feed.nickname) == str(nickname):
            if feed:
                feed.delete()
            return SuccessResponse()
        else:
            return ErrorResponse("권한이 없습니다.")


class UploadReply(APIView):
    def post(self, request):

        feedId = request.data.get('feedId', None)

        if Feed.objects.filter(id=feedId).first() is None:
            return ErrorResponse("글을 찾을 수 없음")

        replyFeed = request.data.get('replyFeed', None)

        email = request.session.get('email', None)
        if email is None:
            return ErrorResponse("정보를 찾을 수 없음 로그인을 하세요.")
        nickname = User.objects.filter(email=email).first()
        if nickname is None:
            return ErrorResponse("유저정보를 찾을 수 없음.")

        Reply.objects.create(feedId=feedId, replyFeed=replyFeed, nickname=nickname)

        return SuccessResponse()