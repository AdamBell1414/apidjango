from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Student, Teacher, Course, Enrollment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'date_joined']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password_confirm']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # Try to authenticate with username first
            user = authenticate(username=username, password=password)
            
            # If username auth fails, try email
            if not user:
                try:
                    from django.contrib.auth.models import User
                    user_obj = User.objects.get(email=username)
                    user = authenticate(username=user_obj.username, password=password)
                except User.DoesNotExist:
                    pass
            
            if user:
                if user.is_active:
                    data['user'] = user
                    return data
                else:
                    raise serializers.ValidationError('User account is disabled.')
            else:
                raise serializers.ValidationError('Invalid credentials.')
        else:
            raise serializers.ValidationError('Username and password required.')


# Simple registration serializers (flat structure)
class StudentRegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    # Student fields
    student_id = serializers.CharField()
    phone_number = serializers.CharField()
    date_of_birth = serializers.DateField()
    address = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Username already exists")
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        
        # Check if student_id already exists
        if Student.objects.filter(student_id=attrs['student_id']).exists():
            raise serializers.ValidationError("Student ID already exists")
        
        return attrs
    
    def create(self, validated_data):
        # Extract user data
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'password': validated_data['password']
        }
        
        # Extract student data
        student_data = {
            'student_id': validated_data['student_id'],
            'phone_number': validated_data['phone_number'],
            'date_of_birth': validated_data['date_of_birth'],
            'address': validated_data['address']
        }
        
        # Create user
        user = User.objects.create_user(**user_data)
        
        # Create student
        student = Student.objects.create(user=user, **student_data)
        
        return student

class TeacherRegistrationSerializer(serializers.Serializer):
    # User fields
    username = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    
    # Teacher fields
    employee_id = serializers.CharField()
    phone_number = serializers.CharField()
    subject_specialization = serializers.CharField()
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        
        # Check if username already exists
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError("Username already exists")
        
        # Check if email already exists
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError("Email already exists")
        
        # Check if employee_id already exists
        if Teacher.objects.filter(employee_id=attrs['employee_id']).exists():
            raise serializers.ValidationError("Employee ID already exists")
        
        return attrs
    
    def create(self, validated_data):
        # Extract user data
        user_data = {
            'username': validated_data['username'],
            'email': validated_data['email'],
            'first_name': validated_data['first_name'],
            'last_name': validated_data['last_name'],
            'password': validated_data['password']
        }
        
        # Extract teacher data
        teacher_data = {
            'employee_id': validated_data['employee_id'],
            'phone_number': validated_data['phone_number'],
            'subject_specialization': validated_data['subject_specialization']
        }
        
        # Create user
        user = User.objects.create_user(**user_data)
        
        # Create teacher
        teacher = Teacher.objects.create(user=user, **teacher_data)
        
        return teacher

# Nested structure serializers (for admin use)
class StudentCreateSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    
    class Meta:
        model = Student
        fields = ['user', 'student_id', 'phone_number', 'date_of_birth', 'address']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserRegistrationSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            student = Student.objects.create(user=user, **validated_data)
            return student
        else:
            raise serializers.ValidationError(user_serializer.errors)

class TeacherCreateSerializer(serializers.ModelSerializer):
    user = UserRegistrationSerializer()
    
    class Meta:
        model = Teacher
        fields = ['user', 'employee_id', 'phone_number', 'subject_specialization']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserRegistrationSerializer(data=user_data)
        if user_serializer.is_valid():
            user = user_serializer.save()
            teacher = Teacher.objects.create(user=user, **validated_data)
            return teacher
        else:
            raise serializers.ValidationError(user_serializer.errors)

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'user', 'student_id', 'phone_number', 'date_of_birth', 'address', 'enrollment_date']

class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Teacher
        fields = ['id', 'user', 'employee_id', 'phone_number', 'subject_specialization', 'hire_date']

class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['name', 'code', 'description', 'teacher', 'credits']

class CourseSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    
    class Meta:
        model = Course
        fields = ['id', 'name', 'code', 'description', 'teacher', 'credits', 'created_at']

class EnrollmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'grade']

class EnrollmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrollment_date', 'grade']
