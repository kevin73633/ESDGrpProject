// Import the functions you need from the SDKs you need
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.13.1/firebase-app.js";
import  { getDatabase, ref, get, push, set, update, remove, child, onValue, onChildAdded, onChildChanged, onChildRemoved}  from "https://www.gstatic.com/firebasejs/10.13.1/firebase-database.js";
import  { getAuth, signInWithPopup, GoogleAuthProvider, onAuthStateChanged, signOut}  from "https://www.gstatic.com/firebasejs/10.13.1/firebase-auth.js";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAQjNGONrPGJ6nZOuLGrLbyJ6sOiTmZr28",
  authDomain: "esdproj-ae595.firebaseapp.com",
  databaseURL: "https://esdproj-ae595-default-rtdb.asia-southeast1.firebasedatabase.app",
  projectId: "esdproj-ae595",
  storageBucket: "esdproj-ae595.firebasestorage.app",
  messagingSenderId: "248176280827",
  appId: "1:248176280827:web:e09ebfb1dd1867f2fc1c5e"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth();
// Initialize Realtime Database and get a reference to the service

//REALTIME DATABASE
const db = getDatabase();
const coursesRef = ref(db, 'courses/');
const tasksRef = ref(db, 'tasks/');

var currUser = null;
var allCourses = [];
var allTaskLists = [];
var currCourse = null;
function CreateNewUser(user) {
    var initialGPA = 0.0;
    set(ref(db, 'users/' + user.uid), {
      username: user.displayName,
      GPA: initialGPA,
      courses: [],
    });
    currUser = new User(user.uid, user.displayName, initialGPA, {});
}
function logout () {
    console.log("Logging out");
    signOut(auth).then(() => {
        // Sign-out successful.
        //clear curruser and allcourses
        currUser = null;
        allCourses = null;
        sessionStorage.setItem("allCourses",  null);
        sessionStorage.setItem("currUser",  null);
        sessionStorage.setItem("allTaskLists",  null);
        window.location.href = "index.html"; 
        //
      }).catch((error) => {
        // An error happened.
    });
  }
function SetCurrentUser(user)
{
    currUser = new User(user.uid, user.username, user.gpa, user.courses, user.degree, user.currentYearAndSem);
}
function SetCurrentCourse(coursecode)
{
    currCourse = coursecode;
}
function GetTaskListByCourse(courseCode)
{
  for (let index = 0; index < allTaskLists.length; index++) {
    const element = allTaskLists[index];
    if (element.courseCode == courseCode)
    {
      return element.taskList;
    }
  }
}
function SetAllTaskLists(taskLists)
{
  allTaskLists = [];
  for (var tl of taskLists)
    {
      var taskListTemp = [];
      for (let index = 0; index < tl["taskList"].length; index++) {
        taskListTemp.push(new Task(tl["taskList"][index]["taskName"], tl["taskList"][index]["taskWeightage"]));
      }
      allTaskLists.push(new TaskList(tl["courseCode"], taskListTemp));
    }
  }
function SetAllCourses(courses)
{
    allCourses = [];
    for (var course of courses)
    {
      allCourses.push(new Course(course.courseCode, course.courseName, course.courseCategory, course.recommendedYearAndSem, course.courseDescription));
    }
    for (var course in currUser.courses)
    {
      var courseCode = course;
      var yearAndSemTaken = currUser.courses[course];
      var fullCourse = Course.GetByCourseCode(courseCode);
      if (fullCourse != null)
      {
        fullCourse.status = "yes";
        fullCourse.enrolled_year = yearAndSemTaken;
      }
    }
}
function CreateNewCourse(course) {
  console.log(course);
  set(ref(db, 'courses/' + course.courseCode), {
    courseCode: course.courseCode,
    courseName: course.courseName,
    courseCategory: course.courseCategory,
    courseDescription: course.courseDescription,
    recommendedYearAndSem: course.recommendedYearAndSem,
  });
}
function CreateNewTaskList(courseCode, TaskList) {
  set(ref(db, 'tasks/' + courseCode), {
    taskList: TaskList,
  });
}
class TaskList
{
  constructor(courseCode, taskList)
  {
    this.courseCode = courseCode,
    this.taskList = taskList
  }
}
class Task
{
  constructor(taskName, taskWeightage)
  {
    this.taskName = taskName;
    this.taskWeightage = taskWeightage;
  }
}
class Course
{
  constructor(courseCode, courseName, courseCategory, recommendedYearAndSem = "Y1S1", courseDescription = "") {
    this.courseCode = courseCode;
    this.courseName = courseName;
    this.courseCategory = courseCategory;
    this.courseDescription = courseDescription;
    this.recommendedYearAndSem = recommendedYearAndSem;
    this.status = "no";
    this.enrolled_year = null;
  }
  static GetByCourseCode(courseCode)
  {
    for (let index = 0; index < allCourses.length; index++) {
      const element = allCourses[index];
      if (element.courseCode == courseCode)
      {
        return element;
      }
    }
  }
  static GetAllCoursesForDegree()
  {
    var returnedCourseList = [];
    for (let index = 0; index < allCourses.length; index++) {
      const element = allCourses[index];
      if (element.courseCategory.includes(currUser.degree))
      {
        returnedCourseList.push(element)
      }
    }
    return returnedCourseList;
  }
  static GetAllCoursesInYearAndSem(yearAndSemTaken)
  {
    var returnedCourseList = [];
    for (let index = 0; index < allCourses.length; index++) {
      const element = allCourses[index];
      if (currUser.courses[element.courseCode] != null && currUser.courses[element.courseCode] == yearAndSemTaken)
      {
        returnedCourseList.push(element)
      }
    }
    return returnedCourseList;
  }
  GetDegreeSpecificCourseCategory()
  {
    if (this.courseCategory.includes(","))
    {
        var coursesInCategories = this.courseCategory.split(",");
        for (let index = 0; index < coursesInCategories.length; index++) {
            const element = coursesInCategories[index];
            if (element == currUser.degree)
            {
              return element;
            }
        }
        return coursesInCategories[0];

    }
    else
      return this.courseCategory;
  }
  GetDegreeSpecificRecommendedDate()
  {
    if (this.recommendedYearAndSem.includes(","))
      {
          var coursesInCategories = this.recommendedYearAndSem.split(",");
          for (let index = 0; index < coursesInCategories.length; index++) {
              const element = coursesInCategories[index];
              if (element.split("_")[1] == currUser.degree)
              {
                return element.split("_")[0];
              }
          }
          return coursesInCategories[0].split("_")[0];
  
      }
      else
      {
        if (this.recommendedYearAndSem.includes("_"))
          return this.recommendedYearAndSem.split("_")[0];
        return this.recommendedYearAndSem;
      }
  }
}
class User
{
  constructor(uid, username, gpa, courses, degree = null, currentYearAndSem = "Y1S1") {
    this.uid = uid;
    this.username = username;
    this.gpa = gpa;
    this.courses = courses;
    this.degree = degree;
    this.currentYearAndSem = currentYearAndSem;
  }
  SetInitialValues(username = this.username, gpa = this.gpa, degree = this.degree, currentYearAndSem = this.currentYearAndSem)
  {
    this.username = username;
    this.gpa = gpa;
    this.degree = degree;
    this.currentYearAndSem = currentYearAndSem;
    set(ref(db, 'users/' + this.uid), {
      username: this.username,
      GPA: this.gpa,
      degree: this.degree,
      currentYearAndSem: this.currentYearAndSem
    });
    sessionStorage.setItem("currUser",  JSON.stringify(currUser));
  }
  SetProfileValues(gpa = this.gpa, degree = this.degree, currentYearAndSem = this.currentYearAndSem)
  {
    this.gpa = gpa;
    this.degree = degree;
    this.currentYearAndSem = currentYearAndSem;
    const updates = {};
    updates[`users/${this.uid}/GPA`] = gpa;
    updates[`users/${this.uid}/degree`] = degree;
    updates[`users/${this.uid}/currentYearAndSem`] = currentYearAndSem;

    update(ref(db), updates);
    sessionStorage.setItem("currUser",  JSON.stringify(currUser));
  }
  AddNewCourse(courseCode, yearAndSemTaken)
  {
    if (currUser.courses == null)
      currUser.courses = {};
    // Get a key for a new Post.
    var localuser =  ref(db,`users/${this.uid}`);

    // Write the new post's data simultaneously in the posts list and the user's post list.
    const updates = {};
    updates[`users/${this.uid}/courses/${courseCode}`] = yearAndSemTaken;
    var exists = false;
    for (var course in currUser.courses)
    {
      if (courseCode == course)
      {
        currUser.courses[course] = yearAndSemTaken;
        exists = true;
      }
    }
    if (exists == false)
    {
      var newCourse = {};
      newCourse[courseCode] = yearAndSemTaken;
      currUser.courses[courseCode] = yearAndSemTaken;
    }
    Course.GetByCourseCode(courseCode).enrolled_year = yearAndSemTaken;
    Course.GetByCourseCode(courseCode).status = "yes";
    console.log(this.courses);
    this.SortCourses();
    sessionStorage.setItem("currUser",  JSON.stringify(currUser));
    return update(ref(db), updates);
  }
  GetAllCourseYearAndSemTaken()
  {
    var tempCourses = {};
    for (var course in currUser.courses)
    {
      tempCourses[course] = currUser.courses[course];
    }
    return tempCourses;
  }
  DeleteCourse(courseCode)
  {
    var temp = [];
    for (var course in currUser.courses)
    {
      var yearAndSemTaken = currUser.courses[course];
      var sem = yearAndSemTaken.split("S")[1];
      var backChar = "";
      if (sem == "3a" || sem == "3b")
      {
        backChar = sem[1];
        sem = "3";
      }
      temp.push({"courseCode" : course, "year" : yearAndSemTaken.split("S")[0].split("Y")[1], "Sem" : sem, "backChar" : backChar}) 
    }
    currUser.courses = {};
    for (var course in temp)
    {
      var curr = temp[course];
      if (curr.courseCode != courseCode)
      {
        currUser.courses[curr.courseCode] = "Y" + curr.year + "S" + curr.Sem + curr.backChar;
      }
      else
      {
        Course.GetByCourseCode(courseCode).enrolled_year = null;
        Course.GetByCourseCode(courseCode).status = "no";
      }
    }
    remove(ref(db, 'users/' + currUser.uid + "/courses/" + courseCode));
    this.SortCourses();
    sessionStorage.setItem("currUser",  JSON.stringify(currUser));
  }
  SortCourses()
  {
    var temp = [];
    for (var course in currUser.courses)
    {
      var yearAndSemTaken = currUser.courses[course];
      var sem = yearAndSemTaken.split("S")[1];
      var backChar = "";
      if (sem == "3a" || sem == "3b")
      {
        backChar = sem[1];
        sem = "3";
      }
      temp.push({"courseCode" : course, "year" : yearAndSemTaken.split("S")[0].split("Y")[1], "Sem" : sem, "backChar" : backChar}) 
    }
    temp.sort(function (a, b) {
      return a.year - b.year || a.Sem - b.Sem || a.backChar.localeCompare(b.backChar);
    });
    currUser.courses = {};
    for (var course in temp)
    {
      var curr = temp[course];
      currUser.courses[curr.courseCode] = "Y" + curr.year + "S" + curr.Sem + curr.backChar;
    }
    sessionStorage.setItem("currUser",  JSON.stringify(currUser));
  }
}

export
{
    firebaseConfig,
    app,
    auth,
    db,
    User,
    Course,
    coursesRef,
    CreateNewCourse,
    currUser,
    currCourse,
    SetCurrentCourse,
    allCourses,
    SetAllCourses,
    CreateNewUser,
    SetCurrentUser,
    CreateNewTaskList,
    TaskList,
    Task,
    tasksRef,
    allTaskLists,
    SetAllTaskLists,
    GetTaskListByCourse,
    logout,

}