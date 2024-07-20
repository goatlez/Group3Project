from django import forms

class CollectionName(forms.Form):
    collectionname = forms.CharField(label = "Flashcard collection name:", max_length = 35)

class UserInput(forms.Form):
    userinput = forms.CharField(label = "Text to convert:", max_length = 10000)

class StackQuantity(forms.Form):
    stackquantity = forms.IntegerField(label = "Flashcard quantity:", max_value=15)

