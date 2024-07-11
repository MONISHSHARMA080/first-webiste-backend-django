from django.shortcuts import render
from django.http import HttpResponse
import os
from groq import Groq
from dotenv import load_dotenv
# import google.generativeai as genai
import os
# import json

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated


# Load environment variables from .env file
import requests as requests_normal
from google.oauth2 import id_token
from google.auth.transport import requests

from backend.models import logs_from_django
from backend.serializers import temp_website_generation_serializer
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from backend.models import User_in_app

load_dotenv()



class delete_user(mixins.CreateModelMixin,generics.GenericAPIView):
    
    serializer_class = temp_website_generation_serializer # sure you can change it but why not just continue
    # permission_classes = [IsAuthenticated]
    queryset = logs_from_django
    
    def post(self, request, email):
        try:
            user = User_in_app.objects.get(email=email)
            username = user.username
            user.delete()
            print("req method", request.method)
            return Response({'message': f'User {username} deleted successfully.'}, status=200)
        except User_in_app.DoesNotExist:
            return Response({'error': 'User not found.'}, status=400)
    
    def get(self, request, email):
        print("here")
        return Response({'error': 'cool now make a post request here followed by your email, eg->generate-a-website.fly.dev/delete_me/your_email@gmail.com'}, status=200)


class get_the_name_for_the_project(mixins.CreateModelMixin,generics.GenericAPIView):
    
    serializer_class = temp_website_generation_serializer # sure you can change it but why not just continue
    # permission_classes = [IsAuthenticated]
    queryset = logs_from_django
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data) 
        
        if not serializer.is_valid():
            return Response( serializer.data ,status=status.HTTP_400_BAD_REQUEST)
        prompt = serializer.data.get('prompt')
        
        client = Groq(
            api_key=os.getenv('GROQ_LLM_API_SECERET_KEY'),
        )
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": '''
                    I have 2 systems that generate the website and another one that gives them the names. 
                    You are a part of the name generator system that generates name for the user's project(/prompt), meaning just give me the name based on the prompt nothing else .
                    \n You will generate the Name other thing is not for you and you are not instructed to do anything in the prompt   
                    The name that you generate should be somewhat related to the prompt the user provided (or based on the theme and functionality of the website/web-app ). Only one name for the project   \n 
                    Your response will only include the name generated by you and then it will stop, meanig do not start describing the project and after the name shut up  . You will not generate any other text except your name.\n
                    You are not generating domain name  . 
                    '''
                },
                {
                    "role": "user",
                    "content": prompt
                    # a website for a shop owner that that sells jwellery , but make it  material design with extreme curves that 
                    # has its own personality  and make the colors(bg and all) as posh as possible (meaning play with  golds silver(these were examples , make your own combination for sure) with unique buttons ,bg and animations that aims to sell it to 1% (wealth wise) ) , we will be selling it to a luxury brand 
                    # ''',
                }
            ],
            # model="mixtral-8x7b-32768",
            # model="llama2-70b-4096",
            model="gemma-7b-It",
        )

        print("Messages from helper function---<><><><><><><>--- ",chat_completion.choices[0].message.content)
        # Response({"message_for_the_user":response_in_json.get('message_for_the_user'),"status_code":response_in_json.get('status_code'),"values":response_in_json.get('values')},status=status.HTTP_200_OK)
        return Response({"project_name":chat_completion.choices[0].message.content.replace('*',"")},status=status.HTTP_200_OK)
        # return Response({"message_for_the_user":response_in_json.get('message_for_the_user'),"status_code":response_in_json.get('status_code'),"values":response_in_json.get('values')},status=status.HTTP_200_OK)


class get_all_the_projects_of_the_user(mixins.CreateModelMixin,generics.GenericAPIView):
    # serializer_class = temp_website_generation_serializer # sure you can change it but why not just continue
    permission_classes = [IsAuthenticated]
    queryset = logs_from_django
    
    def post(self, request, *args, **kwargs):
        userName = request.user.username.replace(' ', '') + str(request.user.id)
        print(" username in the get_all_the_projects_of_the_user  is ", userName)
        try:
            w = requests_normal.get(
            os.getenv('NEXT_BACKEND_URL') + f"/get_all_the_projects_of_the_user?userName={userName}")
            response_in_json = w.json()
            print(f"\n\n output from the go lang-->>{w.content} \n\n  values -->", response_in_json.get('values'))
            print(f"\n\n w.json -->>", response_in_json)
        except requests.RequestException as e:
            print(" cant run the request , error -->>", e)
            # cheacking if the this is what am i getting
            response_returning = Response({"error": "Failed to fetch data from backend"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
            print("respons ereturning in the get_all_the_projects_of_the_user ",response_returning)
            return response_returning
        response_data = {
            "message_for_the_user": response_in_json.get('message_for_the_user'),
            "status_code": response_in_json.get('status_code'),
            "values": response_in_json.get('values'),
            "User_Name": userName
        }
        response_returning = Response(response_data, status=status.HTTP_200_OK)
        print("response returning in the get_all_the_projects_of_the_user", response_returning.data)
        return response_returning
        

class delete_a_project_or_temp(mixins.CreateModelMixin, generics.GenericAPIView):
    
    # queryset = User_in_app.objects.all()
    serializer_class = temp_website_generation_serializer # sure you can change it but why not just continue
    permission_classes = [IsAuthenticated]
    queryset = logs_from_django
    
    # /delete_a_project
    
    def post(self, request, *args, **kwargs):
        # handle the response form go backend her e --, see what to return user
        #  it returns  200 ,--ok no worry , 400 , 500-- set the response in the db and in 400 and 500 show the user response_for_the_user
        #  and these fucntions are just here to return the error to the user---
        # in RN -->> check what the  status is and log it for not , next show the user the  error (alert)
        # ---, 405 too but don't worry we are already posting
        print("-=-=--==--=--=-=--request.query_params.get('project_name')=--==-- ")
        project_name = request.query_params.get('project_name')
        if project_name == None:
            return Response({"message_for_the_user":"The project name can't be empty","status_code":400},status=status.HTTP_400_BAD_REQUEST)
            
        print(request.query_params.get('project_name') )
        w = requests_normal.delete(
        os.getenv('NEXT_BACKEND_URL') + f"/delete_a_project?userName={request.user.username.replace(' ', '') + str(request.user.id)}&project_name={project_name}",
        headers={'content-type': 'application/json'}
        )
        response_in_json = w.json()
        print(response_in_json)
        return Response({"message_for_the_user":response_in_json.get('message_for_the_user'),"status_code":response_in_json.get('status_code')},status=status.HTTP_200_OK)

class temp_website_to_production(mixins.CreateModelMixin, generics.GenericAPIView):
    
    # queryset = User_in_app.objects.all()
    serializer_class = temp_website_generation_serializer
    permission_classes = [IsAuthenticated]
    queryset = logs_from_django
    
    def post(self, request, *args, **kwargs):
        # handle the response form go backend here --, see what to return user
        #  it returns  200 ,--ok no worry , 400 , 500-- set the response in the db and in 400 and 500 show the user response_for_the_user
        #  and these fucntions are just here to return the error to the user---
        # in RN -->> check what the  status is and log it for not , next show the user the  error (alert)
        # ---, 405 too but don't worry we are already posting
        print(request.query_params.get('project_name') )
        project_name = request.query_params.get('project_name')
        if project_name == None:
            return Response({"message_for_the_user":"The project name can't be empty","status_code":400},status=status.HTTP_400_BAD_REQUEST)
        w = requests_normal.post(
             os.getenv('NEXT_BACKEND_URL')+f"/host_the_temp_one_in_a_production_site?userName={request.user.username.replace(' ','')+str(request.user.id)}&project_name={project_name}",
                                                  headers={'content-type': 'application/json',}  )
        response_in_json = w.json()
        print("\n status code -->",response_in_json)
        return Response({"message_for_the_user":response_in_json.get('message_for_the_user'),"status_code":response_in_json.get('status_code'), "link_for_the_current_site":response_in_json.get("link_for_the_current_site")},status=status.HTTP_200_OK)
 
class temp_website_generation(mixins.CreateModelMixin, generics.GenericAPIView):
    
    # queryset = User_in_app.objects.all()
    serializer_class = temp_website_generation_serializer
    permission_classes = [IsAuthenticated]
    
    # ---------------------------------------------------------|||||||||||
    # -->> change the nane to hash of email and and name
    # ---------------------------------------------------------|||||||||||
    def post(self, request, *args, **kwargs):
        #  expected error --- 400 405(method not allowed) 
        print(f"\n\n----------request headers --->>>{request.headers}, \n user ->{request.user}")
        serializer = self.get_serializer(data=request.data )
        if not serializer.is_valid():
            return Response( serializer.data ,status=status.HTTP_400_BAD_REQUEST)
        prompt_by_user = serializer.data.get('prompt')
        # print(f"\n\n\n Dominic dicoco {request.user.email} \n\n\n")
        
        user = request.user.username.replace(' ','')+str(request.user.id)    # --||------- remember to un-comment it -----||---
        
        # user = "Monish"
        response_form_llm =talk_to_llm(prompt_by_user)
        # response_form_llm ="talk_to_llm(prompt_by_user)"
        response_from_go = requests_normal.post(
            # ------?>>>>>mf you did not included api in the path!!!!----->>>>>
            # os.getenv('NEXT_BACKEND_URL')+f"/api/store_llm_response_in_trial_dir?user_name={user}"
            os.getenv('NEXT_BACKEND_URL')+f"/llm_response_write_it_in_temp_dir?userName={user}"
                                                  , json={'message': 'Hello from Django',"llm_response":response_form_llm}
                                                #   ,params={'user_namedkbdwkcbewjbcewjb': user}
                                                  , headers={'content-type': 'application/json',}
                                                          )
        print(f"\n\n response from next status code  {response_from_go.status_code},,\n\n response ->{response_from_go} \n\n,content -->{response_from_go.content} \n\n ")
        print("\n\n",os.getenv('NEXT_BACKEND_URL')+f"/api/store_llm_response_in_trial_dir?userName={user}")
        # ----give a input to talk_to_llm(prompt) ; make the logic for handing the-->> return  from the check_if_llm_response_is_correct()
        response_from_go_in_json = response_from_go.json()
        response_to_send  =Response({"message_to_display_user":response_from_go_in_json.get('message_for_the_user'),
                        "status_code":response_from_go_in_json.get('status_code'), 
                         "prompt":prompt_by_user,"link_for_the_current_site":response_from_go_in_json.get("link_for_the_current_site")},status=status.HTTP_200_OK)
        print("response that i am sending in temp_website_generation-->",response_to_send)
        return response_to_send

def response_from_llm(request):
    
     # Define the URL and API key
    url = F'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={os.getenv("GOOGLE_LLM_API_REQUEST_KEY")}'
    # Define the JSON data to be sent in the request
    data = {
    "contents": [
        {
            "role": "model",
            "parts": [
                {
                    "text": "You’re a site creator that responds(I expect your responses to come in JSON format and that only ; it will have a field called app that will have a field called code and it will contain React code ! Do not disappoint me or do anything else such as including backticks before or after json , you will only return a json object that's it no describing code or generating text that is not in JSON whatsoever  ; and also remember to close it too ; and don't include backticks in start of the response with ``` json , instead start directly with the json object containing code  ) with React code that will configure the sections of a page on a website and the website as a whole, based on the user-provided input. All content and the UI-Ux(design) of the website should be as impressive and exciting as possible. Also, you will be making sure the design is phenomenal and colored. I have my App.tsx file where I have a root component called app, I will paste your response in that, you will export it in default(meaning in your response have the app component and default export it), if you need more component create it in the same file itself (down), and use Tailwind for styling(do not use App.css). Other than that, don't import any libraries. If the user requests you for anything else(such as asking a general question, etc. that does not include you providing/making/writing  react code in response shut up and do not respond to the question;) , you will return a response stating 'I am not meant for doing that' and close the conversation by not responding to the user's question(or stop responding) with anything else."
                }
            ]
        },
        {
            "role": "user",
            "parts": [
                {
                    "text": "Give me a landing page for a startup that sells color for holi and is not celebrating their 50th anniversary"
                }
            ]
        }   
    ],
    "generationConfig": {
        "temperature": 0.9,
        "topP": 1.0,
        "topK": 32,
        "candidateCount": 1,
        "maxOutputTokens": 2048,
        "stopSequences": ["}"]
    }
}


    # Set the headers
    headers = {
        'Content-Type': 'application/json'
    }

    # Send the POST request
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the response from the API
        return HttpResponse(response.text)
    else:
        # If the request failed, return an error message
        return HttpResponse(response)
    
    
    
    
    
def check_if_llm_response_is_correct(react_file:str):
    
    
    
    client = Groq(
        api_key=os.getenv('GROQ_LLM_API_SECERET_KEY'),
    )
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": '''You are a senior software engineer that specialises in React, typescript and next.js.\n 
                you  review my react code and tell me if it is wrong to paste in a file .
                \n I am going to put the code in a nextjs file so i need you to check it for me \n.
                First thing i need you to do is check if the component is valid syntax wise(check if any unnecessary strings , comma, is
                syntax for a react component , etc.), if not then it is not valid.\n
                Secondly check if this has use of library other than tailwind (like react-router ,etc.), if yes then that IS WRONG.\n 
                Thirdly ,is there a component that is exported by default , if not then thas is wrong \n
                Forth thing is , does this code has/is a react component , if not it is false \n. Fifth  are all the imports defined (examples can be use stare etc).\n Sixth an array of react components should be false as i can't paste it in file directly  \n .I need your response to be a JSON , i will have a field called success which will contain boolean value, if all the things afre flase then make it false else if everything is true return true. \n Your response will only return the JSON object as output on basis of the previously mentioned conditions , do not produce any other text\n your design will have a base color and make other colores around it \n your design will have a theme , wether it is minimalism , material design and retro design ,etc and you will stick to it .\n    '''
            },
            {
                "role": "user",
                "content": react_file,
            }
        ],
        model="mixtral-8x7b-32768",
        # model="llama2-70b-4096",
        # model="gemma-7b-It",
    )

    print("Messages from helper function---<><><><><><><>--- ",chat_completion.choices[0].message.content)
    return(chat_completion.choices[0].message.content)






def talk_to_llm(prompt_by_user:str):
    
    print("\n prompt from-- the user ",prompt_by_user)
    # role_for_system="You’re a site creator that responds(I expect your responses to be a  JSON object and that only )\n(it will have a field called app and it will contain React code )\n(in it backtick will be use at the end of the code and at the start of it , but  nowhere/not in between ! Do not dissappoint me or do anything else such as including backticks before or after json object , you will only return a json object thats it ;and also remember to close it too ;and don't inclue backticks in start of the  response with ``` json , instead start directly with the json object containing code  ) with React code that will impress any user in terms of design and looks. \n your signature style is adding colors(or custom touch) on everything in the site that includes button(that are rounded and stylish), background and a bit of gradient and animation on events,and the  the website as a whole , based on the user-provided input. All content and the UI-Ux(design) of the website should be as impressive and exciting as possible , fell free to add a bit of gradient and animation of events. I have my App.tsx file where i have a root component called app, i will paste your response in that ,you will export it in default(meaning in your response have the app component and default export it ), if need more component create it in the same file itself (down), and use tailwind for styling(do not use App.css) , other than that don't import any libraries.If user requests you for anything else(such as asking a general question , etc. that does not include you providing/making/writing  react code in response shut up and do not respond to the question;) , You will retun a response stating 'I am not ment for doing that ' and close the conversation by not responding to users question(or stop responding) with anything else. "
    # role_for_system="You are a Senior Designer filled with innovative design that is colorful and filled with animation .Try to make website longer and detailed (eg about contacts etc) if the user has not mentioned about what make it by yourself \n  .You  responds(I expect your responses to be a  JSON object and that only )\n(it will have a field called app and it will contain React code )\n(in it backtick will be use at the end of the code and at the start of it , but  nowhere/not in between ! Do not dissappoint me or do anything else such as including backticks before or after json object , you will only return a json object thats it ;and also remember to close it too ;and don't inclue backticks in start of the  response with ``` json , instead start directly with the json object containing code  ) with React code that will impress any user in terms of design and looks. \n your signature style is adding colors(or custom touch) on everything in the site that includes button(that are rounded and stylish), background and a bit of gradient and animation on events,and the  the website as a whole , based on the user-provided input. All content and the UI-Ux(design) of the website should be as impressive and exciting as possible , fell free to add a bit of gradient and animation of events. I have my App.tsx file where i have a root component called app, i will paste your response in that ,you will export it in default(meaning in your response have the app component and default export it ), if need more component create it in the same file itself (down), and use tailwind for styling(do not use App.css) \n  other than that don't import any libraries.If user requests you for anything else(such as asking a general question , etc. that does not include you providing/making/writing  react code in response shut up and do not respond to the question;) , You will retun a response stating 'I am not ment for doing that ' and close the conversation by not responding to users question(or stop responding) with anything else. "
    
    
    role_for_system=''' 
    You are tasked with developing a SvelteKit code generator that takes a website prompt from the user and generates code for a website. The generated code will be contained in a single file named "+page.svelte". For adding multiple components write them in the bottom of the same file (same file do not add import statements, or make a new file).
    You will choose a web design theme ( for eg ->minimalism , material ui  ,retro web,OrganicFlow, FuturaTech, ArtDeco ,ZenMinimal, rounded) 
    . The generated website should adhere to a the chosen design theme , ensuring a visual identity ,a good look and well spaces elements(buttons, links, etc.) . Additionally, it should incorporate animations on transition and initial page load etc
    The website should occupy the full screen and implement common features like multiple links(here i mean buttons etc. in the component , make in in your componet ) if the user hasn't specified otherwise.
    In your response as soon your json object ends , stop responding , i do not need your description of how to use the code etc, just give me the damm code thats it .
    Do not use JS reservered keywords for varaible names ; do not make multiple script tags , just use one . \n  Make your site mobile friendly
    '''
    # role_for_system=''' You are a webDesigner filled with innovative design that is colorful and filled with animations and great UI \n .
    # You will provide  me with sveltekit code that I can paste in the file \n
    # try making it with multiple components in the same file .\n
    # .Do not use any external library \n .
    # All css will be in the form of native css  and also close the style tag  \n 
    # I will paste you code in +page.svelte file , if need more component create it in the same file itself (down) \n
    # You can only respond with valid JavaScript objects. Do not respond with any other text or formatting around the JavaScript,
    # you must only respond with raw JSON \n .I NEED your JSON response to be in the format where starting key is called app and inside it write my code  .\n in your response the app field will contain the  file , then i will copy and paste the file to my component so make no mistake. \n also do not add weird paranthesis in your response  '''
    # role_for_system=" You are a Senior Designer filled with innovative design that is colorful and filled with animations and responsive design and gereat UI(specially rount and full) \n . You will provide  me with sveltekit code that I can paste in the file \n try making it with multiple components in the same file .\n . You will write sveltekit code that uses Tailwind  for styling \n .Do not use any external library other that tailwind in my react app\n . All css will be in the form of tailwind \n I have my App.tsx file where I have a root component called app, i will paste your response in that ,you will export it in default(meaning it should have a component that is exported by default export it), if need more component create it in the same file itself (down), and use tailwind for styling(do not use App.css)  \n You can only respond with valid JavaScript objects or arrays. Do not respond with any other text or formatting around the JavaScript, you must only respond with raw JSON \n .I NEED your JSON response to be in the format where starting key is called app .\n in your response the app field will contain the  file , then i will copy and paste the file to my component so make no mistake.\n You will give me React code "
    # role_for_system="You are a code assistant that is designed only for helping users to create a long website that has great  design and animations you will  be using  react ,I have my App.tsx file where i have a root component called app, i will paste your response in that ,you will export it in default, if need more component create it in the same file itself (down), and use tailwind for styling(do not use App.css) , other than that don't import any libraries. In genreal your design  will be expressive (with many colors and many animations) joyful and modern with big icons, buttons etc. If user requests you for anything else(such as asking a general question , etc. that does not include you providing/making/writing  react code in response shut up and do not respond to the question;) , You will retun a response stating 'I am not ment for doing that ' and close the conversation by not responding to users question(or stop responding) with anything else. You can only respond with valid JavaScript objects or arrays. Do not respond with any other text or formatting around the JavaScript, you must only respond with raw JavaScript. The current date is Friday, March 29, 2024"
    # role_for_system = 'You are a site creator that responds with typescript code for a react component that will go in a single file that has a fragment and is the root component called App, based on user provided input. The design of website that you will produce should be creative(in therms of design , layout and style) , impressive(in therms of color choices), colorful(more than 1 color) ,modern and unique , the user should be impressed from your design skills , you will not install any library   '
    # role_for_system= 'You are a site layout creator that responds with HTML ,CSS and JS file which will be used to make the sections  of a page on a website, based on the user-provided input. All content should be as impressive ,colorful(shold be ,modern like after 2018) and as exciting as possible(it should look as it is from 2019-2023) . Your Job is to create staitc website using HTML ,CSS and JS (by yourself , user will not add anything later, and also give html css and js file by yourself meaning do not ask user to add things in the  to html css and js file it is your responsiblity to write its content  ) (if user asks you to create the designs (in HTML, CSS , and Js) then You will make it beautiful, exiciting , novel, unique) ; in your response the contents of css file should start with ":css:" followed by contnent of css and  end with ":css:" and contents of javascript file should also start and end with ":js:" , if user requests you for anything else(such as asking a general question , etc. that does not include you providing/making/writing  code in html , css and javascript in response shut up and do not respond to the question  ) , You will retun a response stating "I am not ment for doing that " and close the conversation by not responding to users question(or stop responding) with anything else . the css and js file that you will provide me will start from css: and js: respectively and end with :css and :js '
    
    
    
    client = Groq(
        api_key=os.getenv('GROQ_LLM_API_SECERET_KEY'),
    )
    print("--------about to send the message-----------")
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": role_for_system,
            },
            {
                "role": "user",
                "content": prompt_by_user,
            }
        ],
        # model="mixtral-8x7b-32768",
        # model="llama3-70b-8192",
        model="llama3-70b-8192",
        # model="gemma-7b-It",
    )
    
    print(chat_completion)
    print("-------------------------")
    code_for_next = extract_tsx_code(chat_completion.choices[0].message.content)
    # if_response_is_correct = check_if_llm_response_is_correct(code_for_next)
    # print("=--=-==-=p==00-0-00-9-889-8jnih",if_response_is_correct)
    print("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
    print(code_for_next)
    print("IIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
    print("\n\n raw response -------->>>>>>>")
    print(chat_completion.choices[0].message.content)
    print("\n\n raw response -------->>>>>>>")
    # res = requests_normal.post(os.getenv('NEXT_BACKEND_URL')+"/store_llm_response_in_trial_dir")
    
    # b = extract_html(chat_completion.choices[0].message.content)
    # write_html_file(b,'a.html')
    # write_html_file(extract_css(chat_completion.choices[0].message.content),'styles.css')
    
    return code_for_next




def extract_tsx_code(code_block:str):
    start_index = code_block.find("<") 
    print(start_index,"jnecjnwje")
    # start_backtick_index = code_block.find("`", start_index)
    start_backtick_index = start_index -1

    # Find the last backtick
    end_backtick_index = code_block.find("```", start_backtick_index + 1)
    # end_backtick_index = code_block.rfind("`")
    # end_backtick_index = code_block.rfind(">);}")

    # Extract the substring between the first and last backticks
    words = code_block[start_backtick_index + 1 : end_backtick_index]

    # Remove leading and trailing whitespaces
    words = words.strip()
    
    words = words.replace('`',"")

    return words

        
def write_react_file(new_code):    
    file_path = F"/home/monish/code/react/react-for-first-website/src/App.tsx"

    try:
        with open(file_path, "w") as file:
            if new_code == None:
                raise Exception(F"{App.split('.')[1]} file is  not found")
            file.write(new_code)
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", e)


def extract_html(text):
    start_pattern = r'```tsx'
    end_pattern = r'</html>'
    start_match = re.search(start_pattern, text)
    end_match = re.search(end_pattern, text)
    if start_match and end_match:
        start_index = start_match.start()
        end_index = end_match.end()
        
        return text[start_index:end_index]
    else:
        return None
    
def extract_tsx(text):
    start_pattern = r'```tsx'
    end_pattern = r';``` '
    start_match = re.search(start_pattern, text)
    end_match = re.search(end_pattern, text)
    if start_match and end_match:
        start_index = start_match.start()
        end_index = end_match.end()
        
        return text[start_index:end_index]
    else:
        return None
    
def extract_css(text):
    start_pattern = r'```css:' 
    end_pattern = r'```'          # Match "js" regardless of case
    
    start_match = re.search(start_pattern, text, re.IGNORECASE)
    end_match = re.search(end_pattern, text, re.IGNORECASE)
    print("initial :css:",end_match)
    
    if end_match is None:
        end_pattern = r':js:'  # Change end pattern to ':js:'
        end_match = re.search(end_pattern, text, re.IGNORECASE)
        print("initial 2 :css:",end_match)
        
    # If end_match is still None, indicating the end pattern ':js:' is not found,
    # then set the end pattern to extract CSS content until the end of the text/string\
        
    if end_match is None:
        end_pattern = r'$'  # End pattern set to match end of the string
        end_match = re.search(end_pattern, text)
        print("initial 3 :css:",end_match)
        
    if start_match and end_match:
        start_index = start_match.end()  # Start from the end of "css:" to skip it
        end_index = end_match.start()     # End before the start of "js"
        
        return text[start_index:end_index].strip()  # Trim whitespace
    else:
        return None



def write_html_file(new_code,name):    
    file_path = F"/home/monish/code/{name}"

    try:
        with open(file_path, "w") as file:
            if new_code == None:
                raise Exception(F"{name.split('.')[1]} file is  not found")
            file.write(new_code)
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", e)
        

def write_css_file(new_code,name):    
    file_path = F"/home/monish/code/react/Magic-first-website/src/App.css"

    try:
        with open(file_path, "w") as file:
            if new_code == None:
                raise Exception(F"{name.split('.')[1]} file is  not found")
            file.write(new_code)
    except FileNotFoundError:
        print("File not found.")
    except Exception as e:
        print("An error occurred:", e)
        

        
# {
#     "role": "system",
#     "content": "You’re a site layout creator that responds with information which will be used to configure the sections of a page on a website, based on the user-provided input. All content should be as impressive and exciting as possible. You can only respond with valid JavaScript objects or arrays. Do not respond with any other text or formatting around the JavaScript, you must only respond with raw JavaScript. The current date is Friday, March 29, 2024."
# }
# {
#     "role": "user",
#     "content": "Given a web page based on the following description:\n\n```\nA personal website for my portfolio and my introduction(basically ,my landing page ) , it should be stylist and unique\n```\n\nAnd given the following TypeScript interface:\n\n```typescript\n/** Metadata about the web page which will be used to create content for it. */\ninterface Page {\n    /** Who or what is the page mainly about? */\n    subject: string\n    /** A good title for the page based on the user request and all other info. It should be a string with around 3 words. Use the same language as the user request. */\n    pageTitle: string\n    /** The css color values, in hex format, that would best be used with this type of web page. For example, a web page about fire trucks might use \"#ce2029\". */\n    colors: string[]\n    /** The style of typography to use based on the type of content on this web page. If it's an artistic page, it might be \"serif\", if its a page that is informative, it might be \"sans-serif\". */\n    typography: \"serif\" | \"sans-serif\"\n    /** Five detailed image description ideas in English for images on the site. Don't describe concepts and don't use names of people, instead describe the image contents. Keep the descriptions short and pure (don't add titles or prefixes). Keep it as diverse as possible (avoid repetition). */\n    imageDescriptions: string[]\n    /**\n     * A decimal between 0 and 1 indicating how light the page should be. For\n     * example, a page with a sci-fi or tech theme might have a low value like\n     * 0. A page for a baking blog might have a high value like 0.8. A website\n     * where the lightness doesn't matter would have a value of 0.5.\n     */\n    lightness: string\n    /**\n     * A decimal between 0 and 1 indicating how creative the design of the page\n     * should be. The majority of pages will be very close to 0.5. However\n     * specific themes of webpages will have values closer to 0 or 1. For\n     * example, a page with a sci-fi, fantasy, or artistic theme might have a\n     * very high value like 0.9. Meanwhile, SaaS software, ecommerce, or a\n     * website marketing a business might have a lower value, like 0.2.\n     */\n    creativity: string\n}\n```\n\nI’ll start a JavaScript object which must implement the `Page` type and you’ll continue exactly where I left off:\n\n{subject:"
# }




def verify_google_token(id_token_from_frontend: str):
    try:
        # Specify the Google client ID for your app
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        print(client_id , "<<---== client id")

        if client_id is None or len(client_id) < 2:
            print("\n\n\n '-------Error google client id is not provided ---------' \n\n\n")
            return 500, "We are unable to reach out to Google for auth"

        # Verify the token
        id_info = id_token.verify_oauth2_token(id_token_from_frontend, requests.Request(), client_id)

        # Return the verification status or user information
        id_info['status'] = 200
        return id_info
    except Exception as e:
        # Token is invalid
        return {"status":400 , "exception": str(e)}


def verify_spotify_token(id_token_from_frontend: str):
    try:
        # Specify the Google client ID for your app
        client_id = os.getenv("GOOGLE_CLIENT_ID")

        if client_id is None or len(client_id) < 2:
            return 500, "We are unable to reach out to Spotify for auth"

        # Verify the token
       

        # Return the verification status or user information
        id_info['status'] = 200
        return id_info
    except Exception as e:
        # Token is invalid
        return {"status":400 , "exception": str(e)}
