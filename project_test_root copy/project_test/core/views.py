from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Collection, Stack
from .forms import CollectionName, UserInput
import json
from openai import OpenAI

client = OpenAI(api_key="")
#DONT FORGET TO REMOVE API KEY BEFORE UPLOADING ANYWHERE. 


def index(response, name):
    collections = Collection.objects.get(name = name) 


    #defined variable "collections" with objects accessed from Collection

    #stacks = collections.stack_set.get(id=1)
    #defined variable "stacks" with objects accessed from stack, which is tied to collections

    if response.method == "GET":
        form = UserInput
        context = {
            "form" : form,
            "collections" : collections,

        }

    elif response.method == "POST":
        form = UserInput(response.POST)

        if form.is_valid():
            cleaned_userinput = form.cleaned_data["userinput"]

            #json_converted = json.dumps(cleaned_userinput)    ##convert back into string for AI output later
            #dictionary_converted = json.loads(json_converted)    ##convert back into string for AI output later
            #collections.stack_set.create(text=json_converted)

            #insert AI Model here


            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Create 2 flashcards by summarizing the following user-provided paragraphs. "
                            "Each flashcard should contain a keyword on one side and a concise one-sentence "
                            "summarized description of the provided text on the other side. Ensure the summaries "
                            "are concise and derived only from the user-inputted information, without adding any "
                            "information from external sources. Each statement must be understood in isolation. "
                            "Include the subject of the statement somewhere in the text. Please generate flashcards "
                            "in the following JSON format: "
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

            collections.stack_set.create(text=flashcards_json)

            #make

            context = {
                "form": form,
                "collections": collections,
            }

    return render(response, "core/display.html", context)

    #this can be put inside each when you want to redirect after pressing save

#############################################################################################################################################

def home(response):
    all_collections = Collection.objects.all() 
    return render(response, "core/home.html", {"all_collections": all_collections}) 

#############################################################################################################################################

def create(response):
    if response.method == "POST":
        form = CollectionName(response.POST)

        if form.is_valid():
            cleaned_name = form.cleaned_data["collectionname"]
            t = Collection(name=cleaned_name) #name variable in Collection model
            t.save()

        return HttpResponseRedirect ("/%s" %t.name)

    else:
        form = CollectionName
    return render(response, "core/create.html", {"form":form}) 

#############################################################################################################################################

def flashcard(response, name, id):
    name = Collection.objects.get(name = name) 
    stack = Stack.objects.get(id=id) 
    stack_dict = json.loads(stack.text) ### unload JSON format as dictionary to be able to access dictionary values
    context = {
        "name":name,
        "stack_id":stack.id,
        "stack_dict" : json.dumps(stack_dict),
    }

    return render (response, "core/flashcard.html", context)

