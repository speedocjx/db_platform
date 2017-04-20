#-*-coding:utf-8-*-
from django.shortcuts import render
from myapp.models import Db_group,Db_name,Db_account,Db_instance,Oper_log,Upload,Task
from passforget.models import Passwd_forget
from django.http import HttpResponse,HttpResponseRedirect,StreamingHttpResponse,JsonResponse
from django.contrib.auth.models import User,Permission,ContentType,Group
import datetime,random,string,md5
from myapp.tasks import sendmail_forget
from myapp.form import Captcha
from captcha.fields import CaptchaField,CaptchaStore
from captcha.helpers import captcha_image_url
from mypro.settings import URL_FOR_PASSWD
# Create your views here.


def pass_rec(request):
    myform = Captcha()
    if request.method == 'POST' and request.POST.has_key('confirm_set'):
        username = request.POST['username']
        email = request.POST['email']
        myform = Captcha(request.POST)
        if myform.is_valid():
            try:
                user = User.objects.get(username=username)
            except Exception,e:
                info = "用户名错误"
                return render(request, 'pass_rec.html', locals())
            if user.email == email:
                random_key = ''.join(random.choice(string.ascii_letters+string.digits) for x in range(20))
                vc_values = md5.new(random_key+username).hexdigest()
                Passwd_forget.objects.filter(username=username,is_valid=1).update(is_valid = 0)
                rec = Passwd_forget(username=username,is_valid=1,vc_value=vc_values)
                rec.save()
                info = "密码重置链接已发送邮箱"
                title = "DB平台密码重置邮件"
                urls = URL_FOR_PASSWD + '/passforget/pass_forget/?username='+username+'&vc='+vc_values
                sendmail_forget.delay(email,title,urls)
            else :
                info = "用户名邮箱不对应"
        else :
            info = "验证码错误"
    elif request.GET.get('newsn') == '1':
        csn = CaptchaStore.generate_key()
        cimageurl = captcha_image_url(csn)
        return HttpResponse(cimageurl)
    return render(request, 'pass_rec.html', locals())

def pass_forget(request):
    try:
        vc = request.GET['vc']
        username = request.GET['username']
        record = Passwd_forget.objects.filter(vc_value=vc,username=username,is_valid=1,create_time__gte=datetime.datetime.now()-datetime.timedelta(minutes=30))[:1]
    except Exception,e:
        print e
        return HttpResponseRedirect("/")
    if record :
        if request.method == 'POST':
            try:
                tmp = User.objects.get(username=username)
                tmp.set_password(request.POST['passwd'].strip())
                tmp.save()
                Passwd_forget.objects.filter(username=username, is_valid=1).update(is_valid=0)
                set_result = "reset passwd ok"
            except:
                set_result = "reset passwd failed"
            return render(request, 'set_result.html', locals())
        else :
            return render(request, 'pass_forget.html', locals())
    else :
        return HttpResponseRedirect("/")


#
# def pass_forget(request):
#     set_result = "reset passwd failed"
#     return render(request, 'set_result.html', locals())