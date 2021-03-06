from django import forms
from .models import Address, ColorVariation, OrderItem, Product, SizeVariation
from django.contrib.auth import get_user_model

User = get_user_model()


class AddToCartForm(forms.ModelForm):
    color = forms.ModelChoiceField(queryset=ColorVariation.objects.none())
    size = forms.ModelChoiceField(queryset=SizeVariation.objects.none())
    quantity = forms.IntegerField(min_value=1)

    class Meta:
        model = OrderItem
        fields = ["quantity", "color", "size"]

    def __init__(self, *args, **kwargs):
        self.product_id = kwargs.pop("product_id")
        product = Product.objects.get(id=self.product_id)
        super().__init__(*args, **kwargs)

        self.fields["color"].queryset = product.available_colors.all()
        self.fields["size"].queryset = product.available_sizes.all()

    def clean(self):
        product = Product.objects.get(id=self.product_id)
        quantity = self.cleaned_data["quantity"]
        if product.stock < quantity:
            raise forms.ValidationError(f"maximum stock available: {product.stock}")


class AddressForm(forms.Form):

    sname = forms.CharField(required=False)
    shipping_zip_code = forms.CharField(required=False, max_length=7)
    sadress = forms.CharField(required=False)

    ###################################
    bname = forms.CharField(required=False)
    billing_zip_code = forms.CharField(required=False, max_length=7)
    badress = forms.CharField(required=False)

    ###################################

    selected_shipping_address = forms.ModelChoiceField(
        Address.objects.none(), required=False
    )

    selected_billing_address = forms.ModelChoiceField(
        Address.objects.none(), required=False
    )

    def __init__(self, *args, **kwargs):
        user_id = kwargs.pop("user_id")
        super().__init__(*args, **kwargs)
        user = User.objects.get(id=user_id)

        shipping_address_qs = Address.objects.filter(user=user, address_type="S")
        billing_address_qs = Address.objects.filter(user=user, address_type="B")

        self.fields["selected_shipping_address"].queryset = shipping_address_qs
        self.fields["selected_billing_address"].queryset = billing_address_qs

    def clean(self):
        selected_shipping_address = self.cleaned_data.get(
            "selected_shipping_address", None
        )

        if selected_shipping_address is None:
            if not self.cleaned_data.get("sname", None):
                self.add_error("sname", "empty")

            shipping_zip_code = self.cleaned_data.get("shipping_zip_code", None)
            if not len(shipping_zip_code) == 7:
                self.add_error("shipping_zip_code", "empty")

            if not self.cleaned_data.get("sadress", None):
                self.add_error("sadress", "empty")

        ##########################################################
        selected_billing_address = self.cleaned_data.get(
            "selected_billing_address", None
        )

        if selected_billing_address is None:
            if not self.cleaned_data.get("bname", None):
                self.add_error("bname", "empty")

            billing_zip_code = self.cleaned_data.get("billing_zip_code", None)
            if not len(billing_zip_code) == 7:
                self.add_error("billing_zip_code", "empty")

            if not self.cleaned_data.get("badress", None):
                self.add_error("badress", "empty")

        ##########################################################
