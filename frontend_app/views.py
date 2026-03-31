import requests
from django.shortcuts import render, redirect

API_URL = "http://flask-api-env.eba-3cez76i2.us-east-1.elasticbeanstalk.com"
BOOKMARK_API_URL = "http://54.87.146.239:8000/api/public/bookmarks/"


def register_view(request):
    if request.method == "POST":
        try:
            response = requests.post(
                f"{API_URL}/register",
                json={
                    "username": request.POST.get("username"),
                    "email": request.POST.get("email"),
                    "password": request.POST.get("password")
                },
                timeout=15
            )

            data = response.json()

            if response.status_code == 200:
                return redirect("/")

            return render(request, "register.html", {"message": data.get("message", "Registration failed")})

        except requests.exceptions.Timeout:
            return render(request, "register.html", {"message": "Backend request timed out."})
        except requests.exceptions.ConnectionError:
            return render(request, "register.html", {"message": "Flask backend is not reachable."})
        except Exception as e:
            return render(request, "register.html", {"message": f"Registration error: {str(e)}"})

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


def task_list(request):
    if "user_id" not in request.session:
        return redirect("/")

    user_id = request.session["user_id"]
    tasks = []

    try:
        response = requests.get(f"{API_URL}/tasks/{user_id}", timeout=15)
        tasks = response.json() if response.status_code == 200 else []
    except Exception as e:
        print("Task list error:", str(e))
        tasks = []

    return render(request, "tasks.html", {"tasks": tasks})


def add_task(request):
    if "user_id" not in request.session:
        return redirect("/")

    message = ""

    if request.method == "POST":
        try:
            response = requests.post(
                f"{API_URL}/tasks",
                json={
                    "user_id": request.session["user_id"],
                    "title": request.POST.get("title"),
                    "description": request.POST.get("description"),
                    "priority": request.POST.get("priority"),
                    "due_date": request.POST.get("due_date")
                },
                timeout=15
            )

            print("Add task status:", response.status_code)
            print("Add task text:", response.text)

            if response.status_code in [200, 201]:
                return redirect("/tasks/")
            else:
                try:
                    data = response.json()
                    message = data.get("message", "Failed to create task.")
                except Exception:
                    message = f"Failed to create task. Response: {response.text[:200]}"

        except requests.exceptions.Timeout:
            message = "Task creation timed out. Please try again."
        except requests.exceptions.ConnectionError:
            message = "Backend is not reachable."
        except Exception as e:
            message = f"Task creation error: {str(e)}"

    return render(request, "add_task.html", {"message": message})


def update_task_status(request, task_id):
    if "user_id" not in request.session:
        return redirect("/")

    if request.method == "POST":
        try:
            requests.put(
                f"{API_URL}/tasks/update/{task_id}",
                json={
                    "status": request.POST.get("status")
                },
                timeout=15
            )
        except Exception as e:
            print("Update task status error:", str(e))

    return redirect("/tasks/")


def delete_task(request, task_id):
    if "user_id" not in request.session:
        return redirect("/")

    try:
        requests.delete(f"{API_URL}/tasks/delete/{task_id}", timeout=15)
    except Exception as e:
        print("Delete task error:", str(e))

    return redirect("/tasks/")


def reminder_view(request):
    if "user_id" not in request.session:
        return redirect("/")

    message = ""

    if request.method == "POST":
        try:
            response = requests.post(
                f"{API_URL}/reminders",
                json={
                    "task_id": request.POST.get("task_id"),
                    "reminder_time": request.POST.get("reminder_time")
                },
                timeout=15
            )

            try:
                message = response.json().get("message", "Reminder saved")
            except Exception:
                message = "Reminder save failed"

        except Exception as e:
            message = f"Reminder error: {str(e)}"

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


def add_bookmark(request, task_id):
    if "user_id" not in request.session:
        return redirect("/")

    if request.method == "POST":
        user_id = request.session["user_id"]
        title = request.POST.get("title", "Untitled Task")

        payload = {
            "user_id": user_id,
            "item_id": str(task_id),
            "title": title,
            "type": "task"
        }

        try:
            response = requests.post(
                BOOKMARK_API_URL,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "accept": "application/json"
                },
                timeout=15
            )

            print("Bookmark API status:", response.status_code)
            print("Bookmark API text:", response.text)

        except Exception as e:
            print("Bookmark API error:", str(e))

    return redirect("/tasks/")


def view_bookmarks(request):
    if "user_id" not in request.session:
        return redirect("/")

    user_id = request.session["user_id"]
    bookmarks = []
    message = ""

    try:
        response = requests.get(
            f"{BOOKMARK_API_URL}?user_id={user_id}",
            headers={"accept": "application/json"},
            timeout=15
        )

        print("View bookmarks status:", response.status_code)
        print("View bookmarks text:", response.text)

        if response.status_code == 200:
            bookmarks = response.json().get("bookmarks", [])
        else:
            message = "Failed to fetch bookmarks."

    except Exception as e:
        message = f"Error fetching bookmarks: {str(e)}"
        print("View bookmarks error:", str(e))

    return render(request, "bookmarks.html", {
        "bookmarks": bookmarks,
        "message": message
    })


def delete_bookmark(request, bookmark_id):
    if "user_id" not in request.session:
        return redirect("/")

    user_id = request.session["user_id"]

    try:
        response = requests.get(
            f"{BOOKMARK_API_URL}{bookmark_id}/?user_id={user_id}",
            headers={"accept": "application/json"},
            timeout=5
        )
        print("Delete bookmark status:", response.status_code)
        print("Delete bookmark text:", response.text)

    except Exception as e:
        print("Delete bookmark error:", str(e))

    return redirect("/bookmarks/")


def logout_view(request):
    request.session.flush()
    return redirect("/")