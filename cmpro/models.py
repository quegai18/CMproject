from django.db import models

# Create your models here.


class Commodity(models.Model):
    """
    商品详情表：
        目前只写了以下几个字段进行展示，其他的功能扩展等以后迭代了再进行修改
    """
    title = models.CharField(
        max_length=32,
        verbose_name="商品名称",
        null=False,                  # 数据库中不可以为空
        blank=False,                 # 页面表单中不可以为空
        unique=True,                # 商品名称必须唯一
    )
    stock = models.IntegerField(verbose_name="库存数量", default=0)
    sell = models.IntegerField(verbose_name="出货数量", default=0)
    barcode = models.BigIntegerField(verbose_name="商品条码", blank=False, unique=True, null=False)
