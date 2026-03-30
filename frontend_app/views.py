import requests
from django.shortcuts import render, redirect

API_URL = "http://flask-api-env.eba-3cez76i2.us-east-1.elasticbeanstalk.com"


def register_view(request):
    if request.method == "POST":
        response = requests.post(f"{API_URL}/register", json={
            "username": request.POST.get("username"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password")
        })

        data = response.json()

        if response.status_code == 200:
            return redirect("/")

        return render(request, "register.html", {"message": data.get("message")})

    return render(request, "register.html")


def login_view(request):
    if request.method == "POST":
        try:
            response = requests.post(
                f"{API_URL}/login",
                json={
                    "username": request.POST.get("username"),
                    "password": request.POST.get("password")
                },
                timeout=15
            )

            print("Login API status:", response.status_code)
            print("Login API text:", response.text)

            try:
                data = response.json()
            except Exception:
                return render(request, "login.html", {
                    "message": f"Backend returned invalid response: {response.text[:200]}"
                })

            if response.status_code == 200:
                request.session["user_id"] = data["user_id"]
                request.session["username"] = data["username"]
                return redirect("/dashboard/")

            return render(request, "login.html", {
                "message": data.get("message", "Login failed")
            })

        except requests.exceptions.ConnectionError:
            return render(request, "login.html", {
                "message": "Flask backend is not reachable. Make sure app.py is running."
            })
        except requests.exceptions.Timeout:
            return render(request, "login.html", {
                "message": "Backend request timed out."
            })
        except Exception as e:
            return render(request, "login.html", {
                "message": f"Login error: {str(e)}"
            })

    return render(request, "login.html")


def dashboard(request):
    if "user_id" not in request.session:
        return redirect("/")

    return render(request, "dashboard.html", {"username": request.session.get("username")})


def task_list(request):
    if "user_id" not in request.session:
        return redirect("/")

    user_id = request.session["user_id"]
    response = requests.get(f"{API_URL}/tasks/{user_id}")
    tasks = response.json() if response.status_code == 200 else []

    return render(request, "tasks.html", {"tasks": tasks})


def add_task(request):
    if "user_id" not in request.session:
        return redirect("/")

    if request.method == "POST":
        requests.post(f"{API_URL}/tasks", json={
            "user_id": request.session["user_id"],
            "title": request.POST.get("title"),
            "description": request.POST.get("description"),
            "priority": request.POST.get("priority"),
            "due_date": request.POST.get("due_date")
        })
        return redirect("/tasks/")

    return render(request, "add_task.html")


def update_task_status(request, task_id):
    if "user_id" not in request.session:
        return redirect("/")

    if request.method == "POST":
        requests.put(f"{API_URL}/tasks/update/{task_id}", json={
            "status": request.POST.get("status")
        })

    return redirect("/tasks/")


def delete_task(request, task_id):
    if "user_id" not in request.session:
        return redirect("/")

    requests.delete(f"{API_URL}/tasks/delete/{task_id}")
    return redirect("/tasks/")


def reminder_view(request):
    if "user_id" not in request.session:
        return redirect("/")

    message = ""

    if request.method == "POST":
        response = requests.post(f"{API_URL}/reminders", json={
            "task_id": request.POST.get("task_id"),
            "reminder_time": request.POST.get("reminder_time")
        })

        try:
            message = response.json().get("message", "Reminder saved")
        except Exception:
            message = "Reminder save failed"

    return render(request, "reminder.html", {"message": message})


def calendar_sync(request):
    if "user_id" not in request.session:
        return redirect("/")

    message = ""
    event_link = ""

    if request.method == "POST":
        try:
            response = requests.post(
                f"{API_URL}/calendar-sync",
                json={"task_id": request.POST.get("task_id")},
                timeout=30
            )

            data = response.json()

            if response.status_code == 401 and data.get("auth_url"):
                return redirect(data["auth_url"])

            message = data.get("message", "")
            event_link = data.get("event_link", "")

        except Exception as e:
            message = str(e)

    return render(request, "calendar_sync.html", {
        "message": message,
        "event_link": event_link
    })
    

def dashboard(request):
    if "user_id" not in request.session:
        return redirect("/")

    weather_data = {}

    try:
        response = requests.get(f"{API_URL}/weather?city=Dublin", timeout=10)
        if response.status_code == 200:
            weather_data = response.json()
    except Exception:
        weather_data = {}

    return render(request, "dashboard.html", {
        "username": request.session.get("username"),
        "weather": weather_data
    })
    
def logout_view(request):
    request.session.flush()
    return redirect("/")