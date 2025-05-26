from django.urls import path
from . import views

# urlpatterns = [
#     # Authentication URLs - Role-based registration
#     path('auth/register/student/', views.register_student, name='register-student'),
#     path('auth/register/teacher/', views.register_teacher, name='register-teacher'),
#     path('auth/register/admin/', views.register_user, name='register-admin'),
    
#     # Authentication URLs - Role-based login
#     path('auth/login/', views.login_user, name='login'),
#     path('auth/login/student/', views.login_student, name='login-student'),
#     path('auth/login/teacher/', views.login_teacher, name='login-teacher'),
#     path('auth/login/admin/', views.login_admin, name='login-admin'),
    
#     path('auth/logout/', views.logout_user, name='logout'),
#     path('auth/profile/', views.user_profile, name='user-profile'),
    
#     # Student URLs
#     path('students/', views.StudentListView.as_view(), name='student-list'),
#     path('students/create/', views.create_student, name='student-create'),
#     path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
#     path('students/<int:student_id>/courses/', views.student_courses, name='student-courses'),
    
#     # Teacher URLs
#     path('teachers/', views.TeacherListView.as_view(), name='teacher-list'),
#     path('teachers/create/', views.create_teacher, name='teacher-create'),
#     path('teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher-detail'),
#     path('teachers/<int:teacher_id>/courses/', views.courses_by_teacher, name='teacher-courses'),
    
#     # Course URLs
#     path('courses/', views.CourseListView.as_view(), name='course-list'),
#     path('courses/create/', views.create_course, name='course-create'),
#     path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course-detail'),
#     path('courses/<int:course_id>/students/', views.course_students, name='course-students'),
#     path('courses/search/', views.search_courses, name='search-courses'),
    
#     # Enrollment URLs
#     path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment-list'),
#     path('enrollments/create/', views.create_enrollment, name='enrollment-create'),
#     path('enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment-detail'),
#     path('enrollments/<int:enrollment_id>/grade/', views.update_grade, name='update-grade'),
    
#     # Student-specific URLs (requires student authentication)
#     path('student/my-courses/', views.my_courses, name='student-my-courses'),
#     path('student/enroll/', views.enroll_student, name='student-enroll'),
#     path('student/unenroll/<int:enrollment_id>/', views.unenroll_student, name='student-unenroll'),
#     path('student/dashboard/', views.student_dashboard, name='student-dashboard'),
    
#     # Teacher-specific URLs (requires teacher authentication)
#     path('teacher/my-courses/', views.my_courses_teacher, name='teacher-my-courses'),
#     path('teacher/my-students/', views.my_students, name='teacher-my-students'),
#     path('teacher/dashboard/', views.teacher_dashboard, name='teacher-dashboard'),
    
#     # Search URLs
#     path('search/students/', views.search_students, name='search-students'),
# ]



from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('auth/register/student/', views.register_student, name='register_student'),
    path('auth/register/teacher/', views.register_teacher, name='register_teacher'),
    path('auth/register/admin/', views.register_user, name='register_admin'),
    
    # General login (with optional user_type)
    path('auth/login/', views.login, name='login_user'),
    
    # # Role-specific login endpoints
    # path('auth/login/student/', views.login_student, name='login_student'),
    # path('auth/login/teacher/', views.login_teacher, name='login_teacher'),
    # path('auth/login/admin/', views.login_admin, name='login_admin'),
    
    path('auth/logout/', views.logout_user, name='logout_user'),
    path('auth/profile/', views.user_profile, name='user_profile'),
    
    # Student URLs
    path('students/', views.StudentListView.as_view(), name='student_list'),
    path('students/create/', views.create_student, name='create_student'),
    path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student_detail'),
    path('students/my-courses/', views.my_courses, name='my_courses'),
    path('students/enroll/', views.enroll_student, name='enroll_student'),
    path('students/unenroll/<int:enrollment_id>/', views.unenroll_student, name='unenroll_student'),
    path('students/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('students/<int:student_id>/courses/', views.student_courses, name='student_courses'),
    
    # Teacher URLs
    path('teachers/', views.TeacherListView.as_view(), name='teacher_list'),
    path('teachers/create/', views.create_teacher, name='create_teacher'),
    path('teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher_detail'),
    path('teachers/my-students/', views.my_students, name='my_students'),
    path('teachers/my-courses/', views.my_courses_teacher, name='my_courses_teacher'),
    path('teachers/update-grade/<int:enrollment_id>/', views.update_grade, name='update_grade'),
    path('teachers/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('teachers/<int:teacher_id>/courses/', views.courses_by_teacher, name='courses_by_teacher'),
    
    # Course URLs
    path('courses/', views.CourseListView.as_view(), name='course_list'),
    path('courses/create/', views.create_course, name='create_course'),
    path('courses/<int:pk>/', views.CourseDetailView.as_view(), name='course_detail'),
    path('courses/<int:course_id>/students/', views.course_students, name='course_students'),
    path('courses/search/', views.search_courses, name='search_courses'),
    
    # Enrollment URLs
    path('enrollments/', views.EnrollmentListView.as_view(), name='enrollment_list'),
    path('enrollments/create/', views.create_enrollment, name='create_enrollment'),
    path('enrollments/<int:pk>/', views.EnrollmentDetailView.as_view(), name='enrollment_detail'),
    
    # Search URLs
    path('search/students/', views.search_students, name='search_students'),
]

