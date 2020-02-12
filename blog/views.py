from django.shortcuts import render, HttpResponse, redirect
from django.contrib import auth
from django.http import JsonResponse
from blog.utils import validCode
from blog import models
from blog.utils import Myforms
import json
from django.db.models import F
from django.db import transaction
from django.core.mail import send_mail
from cnblog import settings
import threading
from bs4 import BeautifulSoup
from django.contrib.auth.decorators import login_required
from blog.utils.geetest import GeetestLib
import os

pc_geetest_id = "b46d1900d0a894591916ea94ea91bd2c"
pc_geetest_key = "36fc3fe98530eea08dfc6ce76e3d24c4"


def login1(request):
    """
    普通验证码登录
    :param request:
    :return:
    """
    if request.method == "POST":
        response = {'user': None, 'msg': None}

        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code")
        valid_code_str = request.session.get("valid_code_str")

        if valid_code.upper() == valid_code_str.upper():
            user = auth.authenticate(username=user, password=pwd)  # 验证用户
            if user:
                auth.login(request, user)  # 注册session： request.user == "当前登录对象"
                response['user'] = user.username
            else:
                response['msg'] = "用户名或密码错误！"
        else:
            response['msg'] = "验证码错误！"

        return JsonResponse(response)

    return render(request, 'login.html')


def login(request):
    """
    滑动验证码登录
    :param request:
    :return:
    """

    if request.method == "POST":
        response = {'user': None, 'msg': None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        gt = GeetestLib(pc_geetest_id, pc_geetest_key)
        challenge = request.POST.get(gt.FN_CHALLENGE)
        validate = request.POST.get(gt.FN_VALIDATE)
        seccode = request.POST.get(gt.FN_SECCODE, '')
        status = request.session[gt.GT_STATUS_SESSION_KEY]
        user_id = request.session['user_id']
        if status:
            result = gt.success_validate(challenge, validate, seccode, user_id=user_id)
        else:
            result = gt.failback_validate(challenge, validate, seccode)

        if result:
            user = auth.authenticate(username=user, password=pwd)
            # print(user)
            if user:
                auth.login(request, user)
                response['user'] = user.username
            else:
                response['msg'] = "用户名或密码错误！"
        return JsonResponse(response)

    return render(request, 'login.html')


def pcgetcaptcha(request):
    user_id = 'test'
    gt = GeetestLib(pc_geetest_id, pc_geetest_key)
    status = gt.pre_process(user_id)
    request.session[gt.GT_STATUS_SESSION_KEY] = status
    request.session["user_id"] = user_id
    response_str = gt.get_response_str()
    print(response_str, "???")
    return HttpResponse(response_str)


def get_valid_code_img(request):
    '''
    验证码图片
    :param request:
    :return:
    '''

    img_data = validCode.get_valid_code_img(request)
    return HttpResponse(img_data)


def register(request):
    """
    注册
    :param request:
    :return:
    """
    if request.is_ajax():
        print(request.POST)
        form = Myforms.UserForm(request.POST)

        response = {"user": None, "msg": None}
        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")

            # 生成用户
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            avatar_obj = request.FILES.get("avatar")

            extra = {}
            if avatar_obj:
                extra["avatar"] = avatar_obj

            models.UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)

        else:
            response['msg'] = form.errors

        return JsonResponse(response)

    form = Myforms.UserForm()
    return render(request, "register.html", {"form": form})


def index(request):
    """
    系统首页
    :param request: 
    :return: 
    """

    article_list = models.Article.objects.all().order_by("-create_time")
    return render(request, "index.html", {'article_list': article_list})


def logout(request):
    """
    注销
    :param request:
    :return:
    """
    auth.logout(request)  # 相当于执行 request.session.flush()

    return redirect("/login")


def home_site(request, username, **kwargs):
    """
    个人站点
    :param request:
    :param username:
    :return:
    """

    user = models.UserInfo.objects.filter(username=username).first()
    if not user:
        return render(request, "not_found.html")

    # 查询当前站点对象
    blog = user.blog

    # 基于 __
    article_list = models.Article.objects.filter(user=user)

    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")

        if condition == "category":
            article_list = article_list.filter(category__title=param)
        elif condition == "tag":
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split("/")
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    return render(request, "home_site.html", {"username": username, "blog": blog, "article_list": article_list})


def article_detail(request, username, article_id):
    """
    文章详情页
    :param request: 
    :param username: 
    :param article_id: 
    :return: 
    """""
    user = models.UserInfo.objects.filter(username=username).first()
    blog = user.blog
    article_obj = models.Article.objects.filter(pk=article_id).first()
    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(request, "article_detail.html", locals())


def digg(request):
    """
    点赞功能
    :param request:
    :return:
    """
    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))

    user_id = request.user.pk
    obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()

    response = {"state": True}
    if not obj:
        models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
        queryset = models.Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F("up_count") + 1)
        else:
            ret = queryset.update(down_count=F("down_count") + 1)
            print(ret)
        print(queryset.first().up_count)
        response["up_count"] = queryset.first().up_count

    else:
        response["state"] = False
        response["handled"] = obj.is_up

    return JsonResponse(response)


def get_comment_tree(request):
    """
    评论树
    :param request:
    :return:
    """
    response = {}
    if request.method == "POST":
        article_id = request.POST.get("article_id")
        parent_id = request.POST.get("pid")
        content = request.POST.get("content")
        user_id = request.user.pk
        if not user_id:
            response['username'] = None
            return JsonResponse(response, safe=False)
        article_obj = models.Article.objects.filter(pk=article_id).first()
        article_user = models.UserInfo.objects.filter(pk=article_obj.user_id).first()

        with transaction.atomic():
            comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                                        parent_comment_id=parent_id)
            models.Article.objects.filter(pk=article_id).update(comm_count=F("comm_count") + 1)

        response['create_time'] = comment_obj.create_time.strftime("%Y-%m-%d %X")
        response['username'] = request.user.username  # 评论者
        response['content'] = content
        response['username_avatar'] = str(request.user.avatar)  # 评论者头像
        response['pk'] = comment_obj.pk
        if parent_id:
            parent = models.Comment.objects.filter(pk=parent_id)     # 父级评论
            response['parent_user'] = parent.values("user__username").first()['user__username']
            response['parent_avatar'] = parent.values("user__avatar").first()['user__avatar']
            response['parent_id'] = parent_id

        # 邮件通知有评论内容
        t = threading.Thread(target=send_mail, args=("您的文章%s新增了一条评论内容" % article_obj.title,
                                                     content,
                                                     settings.EMAIL_HOST_USER,
                                                     [article_user.email, "8104xxxx@qq.com"]))
        t.start()
    else:
        article_id = request.GET.get("article_id")
        response = list(
            models.Comment.objects.filter(article_id=article_id, parent_comment_id__isnull=False).order_by("pk").values(
                "pk", "content",
                "parent_comment_id",
                "create_time",
                "user_id",
                "user__avatar", "user__username", "parent_comment__user", "parent_comment__user__username",
                "parent_comment__user__avatar"))

    return JsonResponse(response, safe=False)       # 非字典类型序列化必须设置safe=False


@login_required
def cn_backend(request):
    """
    后台管理页面
    :param request: 
    :return: 
    """
    article_list = models.Article.objects.filter(user=request.user)

    return render(request, "backend/backend.html", {"article_list": article_list})


@login_required
def add_article(request):
    """
    后台管理添加文章
    :param request: 
    :return: 
    """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        # 防止xss攻击，过滤标签
        from blog.utils import xssfilter
        res = xssfilter.XSSFilter().process(content).decode("utf-8")

        desc = BeautifulSoup(res, 'lxml').text[0:150] + "...."
        models.Article.objects.create(title=title, desc=desc, content=res, user=request.user)
        return redirect("/cn_backend/")
    return render(request, "backend/add_article.html")


def upload(request):
    """
    编辑器文件上传
    :param request:
    :return:
    """
    img_obj = request.FILES.get("upload_img")
    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", img_obj.name)
    with open(path, "wb") as f:
        for line in img_obj:
            f.write(line)
    print(img_obj)
    response = {
        "error": 0,  # error值为0表示没有发生错误
        "url": "/media/add_article_img/%s" % img_obj.name
    }
    return HttpResponse(json.dumps(response))


@login_required
def edit(request, article_id):
    """
    编辑文章
    :param request:
    :param article_id:
    :return:
    """
    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get("content")
        with transaction.atomic():
            models.Article.objects.filter(pk=article_id).update(title=title, content=content)
        return redirect("/cn_backend/")
    article = models.Article.objects.filter(pk=article_id).first()
    print(article.title)
    return render(request, 'backend/edit_article.html', {'article': article})


@login_required
def delete(request, article_id):
    """
    删除文章
    :param request:
    :param article_id:
    :return:
    """
    models.Article.objects.filter(pk=article_id).delete()
    return HttpResponse('ok')