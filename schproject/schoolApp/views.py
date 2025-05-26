from django.shortcuts import render
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Student, Teacher, Course, Enrollment
from .serializers import (
    StudentSerializer, TeacherSerializer, CourseSerializer, EnrollmentSerializer,
    StudentCreateSerializer, TeacherCreateSerializer, CourseCreateSerializer,
    EnrollmentCreateSerializer, UserRegistrationSerializer, LoginSerializer,
    StudentRegistrationSerializer, TeacherRegistrationSerializer
)

# Helper function to get user type
def get_user_type(user):
    """Determine user type based on profile"""
    if user.is_superuser or user.is_staff:
        return 'admin'
    
    try:
        student = Student.objects.get(user=user)
        return 'student', student.id
    except Student.DoesNotExist:
        pass
    
    try:
        teacher = Teacher.objects.get(user=user)
        return 'teacher', teacher.id
    except Teacher.DoesNotExist:
        pass
    
    return 'admin', None

# Authentication Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_student(request):
    """Register a new student with user account"""
    serializer = StudentRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()
        token, created = Token.objects.get_or_create(user=student.user)
        return Response({
            'token': token.key,
            'user_id': student.user.id,
            'username': student.user.username,
            'email': student.user.email,
            'first_name': student.user.first_name,
            'last_name': student.user.last_name,
            'user_type': 'student',
            'profile_id': student.id,
            'student_id': student.student_id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_teacher(request):
    """Register a new teacher with user account"""
    serializer = TeacherRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        teacher = serializer.save()
        token, created = Token.objects.get_or_create(user=teacher.user)
        return Response({
            'token': token.key,
            'user_id': teacher.user.id,
            'username': teacher.user.username,
            'email': teacher.user.email,
            'first_name': teacher.user.first_name,
            'last_name': teacher.user.last_name,
            'user_type': 'teacher',
            'profile_id': teacher.id,
            'employee_id': teacher.employee_id
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_user(request):
    """Register a basic user (admin)"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': 'admin',
            'profile_id': None
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login(request):
    """Single login endpoint for all user types"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Get user type and profile info
        user_info = get_user_type(user)
        if len(user_info) == 2:
            user_type, profile_id = user_info
        else:
            user_type = user_info
            profile_id = None
        
        response_data = {
            'token': token.key,
            'user_id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'user_type': user_type,
            'profile_id': profile_id
        }
        
        # Add specific profile info
        if user_type == 'student':
            student = Student.objects.get(user=user)
            response_data['student_id'] = student.student_id
        elif user_type == 'teacher':
            teacher = Teacher.objects.get(user=user)
            response_data['employee_id'] = teacher.employee_id
        
        return Response(response_data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def logout_user(request):
    """Logout user by deleting token"""
    # Try to get token from different sources
    token_key = None
    
    # Method 1: From Authorization header
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header and auth_header.startswith('Token '):
        token_key = auth_header.split(' ')[1]
    
    # Method 2: From request body
    elif 'token' in request.data:
        token_key = request.data.get('token')
    
    # Method 3: If user is authenticated, get from user
    elif hasattr(request, 'user') and request.user.is_authenticated:
        try:
            token_key = request.user.auth_token.key
        except:
            pass
    
    if not token_key:
        return Response({'error': 'No token provided'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = Token.objects.get(key=token_key)
        token.delete()
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({'error': f'Error logging out: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def user_profile(request):
    """Get current user profile with role info"""
    user = request.user
    user_info = get_user_type(user)
    
    if len(user_info) == 2:
        user_type, profile_id = user_info
    else:
        user_type = user_info
        profile_id = None
    
    profile_data = None
    
    if user_type == 'student':
        try:
            student = Student.objects.get(user=user)
            profile_data = StudentSerializer(student).data
        except Student.DoesNotExist:
            pass
    elif user_type == 'teacher':
        try:
            teacher = Teacher.objects.get(user=user)
            profile_data = TeacherSerializer(teacher).data
        except Teacher.DoesNotExist:
            pass
    
    return Response({
        'user_type': user_type,
        'profile_id': profile_id,
        'profile': profile_data
    })

# Custom permission classes
class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            Student.objects.get(user=request.user)
            return True
        except Student.DoesNotExist:
            return False

class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            Teacher.objects.get(user=request.user)
            return True
        except Teacher.DoesNotExist:
            return False

class IsStudentOrTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        try:
            Student.objects.get(user=request.user)
            return True
        except Student.DoesNotExist:
            try:
                Teacher.objects.get(user=request.user)
                return True
            except Teacher.DoesNotExist:
                return False

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)
    
# Student Views with role-based permissions
class StudentListView(generics.ListAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def create_student(request):
    """Create a new student with user account (Admin only)"""
    serializer = StudentCreateSerializer(data=request.data)
    if serializer.is_valid():
        student = serializer.save()
        token, created = Token.objects.get_or_create(user=student.user)
        
        response_data = StudentSerializer(student).data
        response_data['token'] = token.key
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only admin or the student themselves can modify
            return [IsAdminOrReadOnly()]
        return [permissions.IsAuthenticated()]

# Teacher Views with role-based permissions
class TeacherListView(generics.ListAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def create_teacher(request):
    """Create a new teacher with user account (Admin only)"""
    serializer = TeacherCreateSerializer(data=request.data)
    if serializer.is_valid():
        teacher = serializer.save()
        token, created = Token.objects.get_or_create(user=teacher.user)
        
        response_data = TeacherSerializer(teacher).data
        response_data['token'] = token.key
        
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated]

# Course Views with role-based permissions
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([IsTeacher])
def create_course(request):
    """Create a new course (Teachers only)"""
    # Automatically assign the logged-in teacher
    teacher = Teacher.objects.get(user=request.user)
    
    serializer = CourseCreateSerializer(data=request.data)
    if serializer.is_valid():
        course = serializer.save(teacher=teacher)
        response_data = CourseSerializer(course).data
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CourseDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Only the course teacher or admin can modify
            return [IsTeacher()]
        return [permissions.IsAuthenticated()]

# Enrollment Views with role-based permissions
class EnrollmentListView(generics.ListAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

@api_view(['POST'])
@permission_classes([IsAdminOrReadOnly])
def create_enrollment(request):
    """Create a new enrollment (Admin only)"""
    serializer = EnrollmentCreateSerializer(data=request.data)
    if serializer.is_valid():
        student_id = serializer.validated_data['student'].id
        course_id = serializer.validated_data['course'].id
        
        if Enrollment.objects.filter(student_id=student_id, course_id=course_id).exists():
            return Response(
                {'error': 'Student is already enrolled in this course'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        enrollment = serializer.save()
        response_data = EnrollmentSerializer(enrollment).data
        return Response(response_data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class EnrollmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]

# Student-specific endpoints
@api_view(['GET'])
@permission_classes([IsStudent])
def my_courses(request):
    """Get courses for the currently logged-in student"""
    student = Student.objects.get(user=request.user)
    enrollments = Enrollment.objects.filter(student=student)
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsStudent])
def enroll_student(request):
    """Enroll the currently logged-in student in a course"""
    student = Student.objects.get(user=request.user)
    course_id = request.data.get('course_id')
    
    if not course_id:
        return Response({'error': 'Course ID is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if Enrollment.objects.filter(student=student, course=course).exists():
        return Response(
            {'error': 'Already enrolled in this course'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    enrollment = Enrollment.objects.create(student=student, course=course)
    serializer = EnrollmentSerializer(enrollment)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['DELETE'])
@permission_classes([IsStudent])
def unenroll_student(request, enrollment_id):
    """Unenroll the currently logged-in student from a course"""
    student = Student.objects.get(user=request.user)
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id, student=student)
        enrollment.delete()
        return Response({'message': 'Successfully unenrolled'}, status=status.HTTP_200_OK)
    except Enrollment.DoesNotExist:
        return Response({'error': 'Enrollment not found'}, status=status.HTTP_404_NOT_FOUND)

# Teacher-specific endpoints
@api_view(['GET'])
@permission_classes([IsTeacher])
def my_students(request):
    """Get students for courses taught by the currently logged-in teacher"""
    teacher = Teacher.objects.get(user=request.user)
    courses = Course.objects.filter(teacher=teacher)
    enrollments = Enrollment.objects.filter(course__in=courses)
    serializer = EnrollmentSerializer(enrollments, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsTeacher])
def my_courses_teacher(request):
    """Get courses taught by the currently logged-in teacher"""
    teacher = Teacher.objects.get(user=request.user)
    courses = Course.objects.filter(teacher=teacher)
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsTeacher])
def update_grade(request, enrollment_id):
    """Update grade for an enrollment (teachers only for their courses)"""
    teacher = Teacher.objects.get(user=request.user)
    try:
        enrollment = Enrollment.objects.get(id=enrollment_id, course__teacher=teacher)
        
        grade = request.data.get('grade')
        if not grade:
            return Response({'error': 'Grade is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment.grade = grade
        enrollment.save()
        
        serializer = EnrollmentSerializer(enrollment)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except Enrollment.DoesNotExist:
        return Response(
            {'error': 'Enrollment not found or you do not have permission'}, 
            status=status.HTTP_404_NOT_FOUND
        )

# Dashboard views with role-based access
@api_view(['GET'])
@permission_classes([IsStudent])
def student_dashboard(request):
    """Get dashboard data for student"""
    student = Student.objects.get(user=request.user)
    enrollments = Enrollment.objects.filter(student=student)
    
    dashboard_data = {
        'student_info': StudentSerializer(student).data,
        'total_courses': enrollments.count(),
        'enrollments': EnrollmentSerializer(enrollments, many=True).data,
        'recent_enrollments': EnrollmentSerializer(
            enrollments.order_by('-enrollment_date')[:5], many=True
        ).data
    }
    
    return Response(dashboard_data)

@api_view(['GET'])
@permission_classes([IsTeacher])
def teacher_dashboard(request):
    """Get dashboard data for teacher"""
    teacher = Teacher.objects.get(user=request.user)
    courses = Course.objects.filter(teacher=teacher)
    enrollments = Enrollment.objects.filter(course__in=courses)
    
    dashboard_data = {
        'teacher_info': TeacherSerializer(teacher).data,
        'total_courses': courses.count(),
        'total_students': enrollments.count(),
        'courses': CourseSerializer(courses, many=True).data,
        'recent_enrollments': EnrollmentSerializer(
            enrollments.order_by('-enrollment_date')[:10], many=True
        ).data
    }
    
    return Response(dashboard_data)

# General endpoints (accessible by authenticated users)
@api_view(['GET'])
def student_courses(request, student_id):
    """Get all courses for a specific student"""
    try:
        student = Student.objects.get(id=student_id)
        enrollments = Enrollment.objects.filter(student=student)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    except Student.DoesNotExist:
        return Response({'error': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def course_students(request, course_id):
    """Get all students enrolled in a specific course"""
    try:
        course = Course.objects.get(id=course_id)
        enrollments = Enrollment.objects.filter(course=course)
        serializer = EnrollmentSerializer(enrollments, many=True)
        return Response(serializer.data)
    except Course.DoesNotExist:
        return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
def courses_by_teacher(request, teacher_id):
    """Get all courses taught by a specific teacher"""
    try:
        teacher = Teacher.objects.get(id=teacher_id)
        courses = Course.objects.filter(teacher=teacher)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
    except Teacher.DoesNotExist:
        return Response({'error': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

# Search endpoints
@api_view(['GET'])
def search_courses(request):
    """Search courses by name or code"""
    query = request.GET.get('q', '')
    if query:
        courses = Course.objects.filter(
            name__icontains=query
        ) | Course.objects.filter(
            code__icontains=query
        )
    else:
        courses = Course.objects.all()
    
    serializer = CourseSerializer(courses, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsTeacher])
def search_students(request):
    """Search students by name or student ID (Teachers only)"""
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.filter(
            user__first_name__icontains=query
        ) | Student.objects.filter(
            user__last_name__icontains=query
        ) | Student.objects.filter(
            student_id__icontains=query
        )
    else:
        students = Student.objects.all()
    
    serializer = StudentSerializer(students, many=True)
    return Response(serializer.data)
