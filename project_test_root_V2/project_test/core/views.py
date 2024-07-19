from django.shortcuts import render
from django.http import HttpResponseRedirect
from .models import Collection, Stack
from .forms import UserInput, CollectionName, StackQuantity
import json
import openai

####client = openai.OpenAI(api_key="")

# HOME PAGE #############################################################################################################################################

def home(response):
        
    if response.method == 'POST':
            
            #DELETE COLLECTION FUNCTION ###############################################################################################################
            
            collection_name = response.POST['name']
            collection = Collection.objects.get(name = collection_name) 

            collection.delete()
            all_collections = Collection.objects.all()

            context = {
                'all_collections':all_collections,
                'collection':collection
            }    
            return render(response, "core/home.html", context)
    
            ########################################################################################################################################

    else:

        all_collections = Collection.objects.all()
        stack = Stack.objects.all()

        context = {
            "all_collections": all_collections,
            "stack":stack,
        }
        return render(response, "core/home.html", context)

# CREATE FLASHCARD COLLECTION PAGE ############################################################################################################################################

def create(response):

    if response.method == "POST":
            form = CollectionName(response.POST)
            
            if form.is_valid():
                cleaned_name = form.cleaned_data["collectionname"]

                # ERROR MESSAGE FOR DUPLICATE COLLECTION NAME #####################################################################################################################
                if Collection.objects.filter(name=cleaned_name).exists():
                    error_message = f"Collection with name '{cleaned_name}' already exists."
                    all_collections = Collection.objects.all()

                    context = {
                        "form": form,
                        "collections": all_collections,
                        "error_message": error_message,
                    }
                    return render(response, "core/create.html", context)
                
                #########################################################################################################################################################################

                else:

                    new_collection = Collection(name=cleaned_name)
                    new_collection.save()
                    return HttpResponseRedirect(f"/{new_collection.name}")

    else:

        form = CollectionName()
    return render(response, "core/create.html", {"form": form})

# CREATE FLASHCARD STACK PAGE ############################################################################################################################################

def index(response, name):
    collections = Collection.objects.get(name = name) 

    if response.method == "GET":
        form = UserInput()
        quantity = StackQuantity()
        context = {
            "form": form,
            "quantity":quantity,
            "collections": collections,
        }

        return render(response, "core/display.html", context)

    elif response.method == "POST":

            form = UserInput(response.POST)
            quantity = StackQuantity(response.POST)

            user_input = response.POST['userinput']
            user_input_quantity = response.POST['stackquantity']


            #ERROR MESSAGE FOR EXCEEDING MAXIMUM CHARACTER LENGTH #############################################################################

            if len(user_input) > 2500:
                    error_message = f"{len(user_input)}/2500 characters. User input exceeds character limit. "
                    form = UserInput()
                    quantity = StackQuantity()
                    context = {
                        "form": form,
                        "quantity":quantity,
                        "collections": collections,
                        "error_message":error_message
                    }

                    return render(response, "core/display.html", context)

            #############################################################################################################################

            else:
             
                if form.is_valid() and quantity.is_valid():
                    cleaned_userinput = form.cleaned_data["userinput"]
                    stackquantity = quantity.cleaned_data["stackquantity"]

            
                    # Insert AI Model here
                    completion = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {
                                "role": "system",
                                "content": (
                                    f"Create only  {stackquantity}  flashcards by summarizing the following user-provided paragraphs. Each flashcard should contain a keyword on one side and a concise one-sentence summarized description of the provided text on the other side. Ensure the summaries are concise and derived only from the user-inputted information, without adding any information from external sources. Each statement must be understood in isolation. Include the subject of the statement somewhere in the text. Keep each explanation to be strictly 100 words maximum. Please generate flashcards in the following JSON format: "
                                    '{'
                                    '"Flashcard1": {"Front": "Insert keyword", "Back": "Insert explanation"}, '
                                    '"Flashcard2": {"Front": "Insert keyword", "Back": "Insert explanation"}'
                                    '}. Ensure the output is a valid JSON string.'
                                ),
                            },
                            {"role": "user", "content": cleaned_userinput},
                        ],
                        temperature=1
                    )

                    
                    ai_output = completion.choices[0].message.content

                    # Parse the AI output to a dictionary (assuming the output is valid JSON)
                    flashcards_dict = json.loads(ai_output)

                    # Convert the dictionary to a JSON string
                    flashcards_json = json.dumps(flashcards_dict)

                    new_stack = collections.stack_set.create(text=flashcards_json)

                    stack_dict = json.loads(new_stack.text)  # Unload JSON format as dictionary to be able to access dictionary values

                    context = {
                        "form": form,
                        "collections": collections,
                        "name": collections.name,
                        "stack_id": new_stack.id,
                        "stack_dict": json.dumps(stack_dict),
                    }

                    return render(response, "core/flashcard.html", context)

# FLASHCARD PAGE ############################################################################################################################################

def flashcard(response, name, id):

    collection = Collection.objects.get(name = name) 
    stack = Stack.objects.get(id=id) 
    stack_dict = json.loads(stack.text)  

    context = {
                "name": collection.name,
                "id":id,
                "stack_id": stack.id,
                "stack_dict": json.dumps(stack_dict),
            }

    return render(response, "core/flashcard.html", context)

