from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import HttpResponse
from django.utils.encoding import escape_uri_path
from cmpro.models import Commodity
from django.db import transaction
from django.urls import reverse
from cmpro.forms.model_form import *
import json
import xlrd

# Create your views here.


def page_show(request):
    """
    商品展示页
    :param request:
    :return:
    """
    page_content = {
        "stock_commodity": Commodity.objects.filter(stock__gt=0),  # 查询出库存大于0的
        "zero_stock_commodity": Commodity.objects.filter(stock=0),# 查询出库存为0的
    }
    return render(request, "data_page.html", page_content)


def actions(flag, commodity_id, request):
    """
    为了增加和减少的操作出现大量重复代码，写了这个来集中处理
    :param flag: 是增加还是减少
    :param id: 商品ID
    :param number: 变化的数量
    :return:
    """
    recv_data = {
        "tip": "",
    }
    number = request.POST.get("number")      # 这是需要变动的数值
    commodity_obj = Commodity.objects.filter(id=commodity_id)  # 数据库检索对应的商品
    if not commodity_obj:      # 判断ID是否合法
        recv_data["tip"] = "请选择正确的商品ID或刷新页面重新操作！"
        return recv_data
    if not number.isdigit():   # 判断输入的数值是否合法
        recv_data["tip"] = "请输入正整数！"
        return recv_data
    number = int(number)
    if flag == "add":
        new_stock = commodity_obj[0].stock + number       # 用之前的库存加上新输入的库存
        commodity_obj.update(stock=new_stock)
    else:
        if commodity_obj[0].stock < number:
            recv_data["tip"] = "输入的销售数量超过当前库存数量"
            return recv_data
        new_stock = commodity_obj[0].stock - number   #新库存等于原库存减去输入的库存，同时，减去的库存算到销量里面来
        new_sell = commodity_obj[0].sell + number
        commodity_obj.update(stock=new_stock,sell=new_sell)
    return recv_data


def add_stock(request, commodity_id):
    """
    用于给商品增加库存
    :param request:
    :param commodity_id:
    :return:
    """
    recv_data = actions(flag="add", commodity_id=commodity_id, request=request)
    recv_json = json.dumps(recv_data)
    return HttpResponse(recv_json)


def reduce_stock(request, commodity_id):
    """
    用于减少库存
    :param request:
    :param commodity_id:
    :return:
    """
    recv_data = actions(flag="reduce", commodity_id=commodity_id, request=request)
    recv_json = json.dumps(recv_data)
    return HttpResponse(recv_json)


def remove_commodity(request, commodity_id):
    """
    GET请求
    根据商品ID删除商品
    :param request:
    :return:
    """
    commodity_obj = Commodity.objects.filter(id=commodity_id)      # 过滤一下这个ID，看是否存在这个ID的商品
    if not commodity_obj:    # 如果商品不存在
        tip = "当前输入的商品ID不存在，请不要输入无效商品ID！"
        return render(request, "tips.html", {"tip": tip})
    if request.method == "GET":    # 这里是为了进行二次删除操作，防止用户是误点击了删除按钮
        # 把被选中需要删除的商品信息展示给用户看，让用户二次确认是否需要删单这个商品
        return render(request, "remove-commodity.html", {"commodity_obj": commodity_obj[0]})
    commodity_obj[0].delete()
    return redirect(reverse("index"))


def search_commodity(request):
    """
    用于用户搜索，仅提供条案搜索或商品名称搜索
    :param request:
    :return:
    """

    input_text = request.POST["search_text"]    # 获取用户输入的搜索关键词
    search_query = None
    if input_text.isdigit():
        search_query = Commodity.objects.filter(barcode__startswith=input_text)
    else:
        search_query = Commodity.objects.filter(title__startswith=input_text)
    page_content = {
        "stock_commodity": search_query.filter(stock__gt=0),  # 查询出库存大于0的
        "zero_stock_commodity": search_query.filter(stock=0),  # 查询出库存为0的
    }
    return render(request, "data_page.html", page_content)


def add_commodity(request):
    if request.method == "GET":
        form = CommodityModelForm()
        return render(request, "addpage.html", {"form": form})
    # 把form表单提交的数据传入modelform组件内
    form = CommodityModelForm(data=request.POST)
    if form.is_valid():
        # 如何数据合法，就进行保存
        Commodity.objects.create(
            title=request.POST.get("title"),
            stock=request.POST.get("stock"),
            sell=request.POST.get("sell"),
            barcode=request.POST.get("barcode"),
        )
        return redirect(reverse("index"))
    # 如果数据不合法，就返回错误信息
    return render(request, "addpage.html", {"form": form})


def bulk_save_data(input_file):
    """
    用于批量的往数据库导入数据
    :return:
    """
    data = xlrd.open_workbook(filename=None, file_contents=input_file.read())      # 读取文件
    table = data.sheet_by_index(0)  # 得到excel中数据表sheets1
    rows = table.nrows   # 总行数
    try:
        # 控制数据库事务交易
        with transaction.atomic():
            # 获取数据表中的每一行数据写入设计好的数据库表
            for row in range(2, rows):  # 从1开始是为了去掉表头
                row_values = table.row_values(row)  # 每一行的数据
                Commodity.objects.create(
                    title=row_values[0],
                    stock=row_values[1],
                    sell=row_values[2],
                    barcode=row_values[3],
                )
    except:
        return ('解析excel文件或者数据插入错误！')


def bulk_load(request):
    """获取导入的excel表格"""
    file_name = request.POST["inputFileName"]
    file_type = file_name.split('.')[1]  # 拿到文件后缀
    if file_type not in ['xlsx', 'xls']:   # 支持这两种文件格式
        return HttpResponse("文件格式不正确，请重新上传（仅支持excel表格）")
    input_file = request.FILES["inputFile"]
    bulk_save_data(input_file)
    return HttpResponse("数据导入成功")


def download(request):
    """
    用于下载excel表格
    :param request:
    :return:
    """
    file = open('测试表格.xlsx', 'rb')
    response = HttpResponse(file, content_type='application/octet-stream')
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(escape_uri_path('批量导入数据模板.xlsx'))
    return response

