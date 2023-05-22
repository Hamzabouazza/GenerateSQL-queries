from django.shortcuts import render
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os


# Create your views here.


# GET to return a rendered home.html template
def index(request):
    if request.method == "GET":
        return render(request, "home.html")
    # method is POST,calls the get_result(), to extract parameters from the POST request, uses them as inputs
    elif request.method == "POST":
        data = get_result(request)
        # predict a response to a given question, and renders the home.html template with the predicted result data.
        return render(request, "home.html", data)
    else:
        raise ValueError("Invalid request method")


# @csrf_exempt
def get_result(request):
    # retrieves the question and schema parameters from the POST request
    question = request.POST.get("question")
    # Get the directory that this file (views.py) is in
    dir_path = os.path.dirname(os.path.realpath(__file__))
        
   # Combine the directory path and your json file name to get the path
    json_file_path = os.path.join(dir_path, 'data.json')
    with open(json_file_path, "r") as f:
        data = json.load(f)
    data = json.dumps(data,indent=4)
    data = json.loads(data)
    # Call the predict() method of the LangChain class, passing the question, table_name and columns as parameters
    result = settings.LLM_CHAIN.predict(
        question=question,
        json_file_content=data,
    )

    return {"result": result}


def get_data(schema, question, description):
    if schema:
        # extracts the table_name and columns parameters from the schema
        table_name, columns = settings.EXTRACT_SCHEMA(schema)
    else:
        with open(os.getcwd() + "\\nltosql\\nltosql\\data.json", "r") as f:
            data = json.load(f)
            table_name = ""
            for tbl in data.keys():
                if tbl in question:
                    table_name = tbl
                    column_names = data[tbl].keys()
                    column_types = [data[tbl][col]["type"] for col in column_names]
                    column_descriptions = [
                        data[tbl][col]["description"] for col in column_names
                    ]
                    columns = [
                        tbl + "." + column_name + " " + column_types[index]
                        for index, column_name in enumerate(column_names)
                    ]
                    description = [
                        tbl + "." + column_name + ":" + column_descriptions[index]
                        for index, column_name in enumerate(column_names)
                    ]
            if table_name == "":
                raise ValueError("Table not found")

    columns = ",".join(columns)
    description = ",".join(description)

    return table_name, columns, description
