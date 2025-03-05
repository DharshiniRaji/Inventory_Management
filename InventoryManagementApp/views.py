from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View, CreateView, UpdateView, DeleteView
from django.contrib.auth import authenticate, login
from .forms import UserRegisterForm, InventoryItemForm, BillForm, ItemForm
from .models import InventoryItem, Category,Bill_details, Items_details
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from InventoryManagement.settings import LOW_QUANTITY
from django.contrib import messages
from weasyprint import HTML
import tempfile
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
import tempfile
import os


# Create your views here.
class Index(TemplateView):
    template_name = 'inventory/index.html'

class InventoryOption(TemplateView):
	template_name = 'inventory/inventory_option.html'

class Dashboard(LoginRequiredMixin, View):
	def get(self, request):
		items = InventoryItem.objects.all()
		low_inventory = InventoryItem.objects.filter(
			user=self.request.user.id,
			quantity__lte=LOW_QUANTITY
		)

		if low_inventory.count() > 0:
			if low_inventory.count() > 1:
				messages.error(request, f'{low_inventory.count()} items have low inventory')
			else:
				messages.error(request, f'{low_inventory.count()} item has low inventory')

		low_inventory_ids = InventoryItem.objects.filter(
			user=self.request.user.id,
			quantity__lte=LOW_QUANTITY
		).values_list('id', flat=True)
		return render(request, 'inventory/dashboard.html',  {'items': items, 'low_inventory_ids': low_inventory_ids})

class SignUpView(View):
	def get(self, request):
		form = UserRegisterForm()
		return render(request, 'inventory/signup.html', {'form': form})

	def post(self, request):
		form = UserRegisterForm(request.POST)

		if form.is_valid():
			form.save()
			user = authenticate(
				username=form.cleaned_data['username'],
				password=form.cleaned_data['password1']
			)

			login(request, user)
			return redirect('index')

		return render(request, 'inventory/signup.html', {'form': form})
	
class AddItem(LoginRequiredMixin, CreateView):
	model = InventoryItem
	form_class = InventoryItemForm
	template_name = 'inventory/item_form.html'
	success_url = reverse_lazy('dashboard')

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['categories'] = Category.objects.all()
		return context

	def form_valid(self, form):
		form.instance.user = self.request.user
		return super().form_valid(form)
	
class EditItem(LoginRequiredMixin, UpdateView):
	model = InventoryItem
	form_class = InventoryItemForm
	template_name = 'inventory/item_form.html'
	success_url = reverse_lazy('dashboard')

class DeleteItem(LoginRequiredMixin, DeleteView):
	model = InventoryItem
	template_name = 'inventory/delete_item.html'
	success_url = reverse_lazy('dashboard')
	context_object_name = 'item'
	

def generate_bill_number():
    """Generate a unique bill number"""
    latest_bill = Bill_details.objects.order_by('-id').first()
    if latest_bill:
        return f"MS{latest_bill.id + 1:03}"
    return "MS001"

def billing(request):
    if request.method == 'POST':
        bill_form = BillForm(request.POST)

        if bill_form.is_valid():
            bill = bill_form.save(commit=False)  # Do not save yet
            bill.bill_number = generate_bill_number()  # Assign bill number

            items = []  # Store items before bulk insert
            total_amount = 0  

            item_names = request.POST.getlist('item_name')
            prices = request.POST.getlist('price')
            quantities = request.POST.getlist('quantity')

            # Extract and validate items
            for i in range(len(item_names)):
                try:
                    item_name = item_names[i]
                    price = float(prices[i])
                    quantity = int(quantities[i])
                    total_price = price * quantity
                    total_amount += total_price  

                    print(f"Item {i+1}: Name={item_name}, Price={price}, Quantity={quantity}, Total Price={total_price}")

                    # Create item but do not save yet
                    items.append(Items_details(
                        item_name=item_name,
                        price=price,
                        quantity=quantity
                    ))
                except Exception as e:
                    print(f"Error processing item {i+1}: {e}")

            # Assign total amount to bill
            bill.total_amount = total_amount  

            # Calculate GST based on buyer location
            if not bill.without_gst:
                if bill.buyer_location.lower() == "tamil nadu":
                    bill.sgst_amount = round(total_amount * 0.025, 2)
                    bill.cgst_amount = round(total_amount * 0.025, 2)
                    bill.gst_amount = None  
                else:
                    bill.gst_amount = round(total_amount * 0.05, 2)
                    bill.sgst_amount = None  
                    bill.cgst_amount = None  

            bill.save()  # Save bill before assigning it to items
            print(f"Bill {bill.bill_number} saved successfully with total amount: {bill.total_amount}")

            # Now assign the bill to each item and save
            for item in items:
                item.bill = bill  
            
            Items_details.objects.bulk_create(items)  # Bulk insert all items
            print("Items saved successfully.")

            return render(request, 'inventory/billing.html', {
                'bill_form': BillForm(),
                'item_form': ItemForm(),
                'bill': bill,
                'items': items
            })

    else:
        bill_form = BillForm()
        item_form = ItemForm()

    return render(request, 'inventory/billing.html', {'bill_form': bill_form, 'item_form': item_form})

def bill_receipt(request, bill_id):
    bill = Bill_details.objects.get(id=bill_id)
    items = bill.items.all()
    grand_total = bill.total_amount + (bill.gst_amount or 0) + (bill.sgst_amount or 0) + (bill.cgst_amount or 0)
    return render(request, 'inventory/bill_receipt.html', {'bill': bill, 'items': items, 'grand_total': grand_total})

def generate_invoice(request, bill_id):
    bill = get_object_or_404(Bill_details, id=bill_id)
    items = bill.items.all()
    
    # Calculate grand total
    grand_total = bill.total_amount + (bill.gst_amount or 0) + (bill.sgst_amount or 0) + (bill.cgst_amount or 0)

    # Render invoice HTML template
    html_string = render(request, 'inventory/invoice_template.html', {
        'bill': bill, 
        'items': items, 
        'grand_total': grand_total
    }).content.decode('utf-8')

    # Generate PDF response
    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'inline; filename="invoice_{bill.bill_number}.pdf"'

    # Use NamedTemporaryFile with delete=False
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
        temp_pdf_path = temp_pdf.name

    try:
        HTML(string=html_string).write_pdf(temp_pdf_path)
        with open(temp_pdf_path, "rb") as pdf_file:
            response.write(pdf_file.read())
    finally:
        os.remove(temp_pdf_path)  # Ensure cleanup

    return response