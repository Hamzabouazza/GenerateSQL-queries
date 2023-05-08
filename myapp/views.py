from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt



# Create your views here.

#GET to return a rendered home.html template
@csrf_exempt
def index(request):
    if request.method == 'GET':
        return render(request, 'home.html')
    #method is POST,calls the get_result(), to extract parameters from the POST request, uses them as inputs
    elif request.method == 'POST':
        data = get_result(request)
        #predict a response to a given question, and renders the home.html template with the predicted result data.
        return render(request, 'home.html', data)
    else:
        raise ValueError('Invalid request method')
    
#@csrf_exempt
def get_result(request):
   #retrieves the question and schema parameters from the POST request
    question = request.POST.get('question')
    schema = request.POST.get('schema')
    description = request.POST.get('description')
    # extracts the table_name and columns parameters from the schema 
    table_name, columns = settings.EXTRACT_SCHEMA(schema)
    #Call the predict() method of the LangChain class, passing the question, table_name and columns as parameters
    result = settings.LLM_CHAIN.predict(question=question, table_name = table_name, description=description, columns = columns)
    
    return {'result': result}

