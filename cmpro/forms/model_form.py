from django import forms
from django.core.exceptions import ValidationError
from cmpro.models import *


class BootstrapModelForms(forms.ModelForm):
    """
    用于统一定制每个forms组件的html样式
    """
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForms, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["style"] = "width: 300px;"


class CommodityModelForm(BootstrapModelForms):
    """
    利用modelform来控制表
    """
    class Meta:
        """进行字段的自定制"""
        model = Commodity
        fields = ["title", "stock", "sell", "barcode"]

    def clean_title(self):
        """局部钩子校验商品名是否存在"""
        title = self.cleaned_data["title"]
        if Commodity.objects.filter(title=title):
            raise ValidationError("商品名已存在")
        else:
            return title

    def clean_barcode(self):
        """局部钩子校验商品名是否存在"""
        barcode = self.cleaned_data["barcode"]
        if barcode == "":raise ValidationError("商品条码不可为空")
        if Commodity.objects.filter(barcode=barcode):
            raise ValidationError("商品条码已存在")
        else:
            return barcode

