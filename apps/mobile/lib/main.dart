import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'screens/splash_screen.dart';
import 'screens/home_screen.dart';
import 'screens/course_screen.dart';
import 'screens/lesson_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/login_screen.dart';
import 'services/auth_service.dart';
import 'services/course_service.dart';
import 'providers/auth_provider.dart';
import 'providers/course_provider.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  await SharedPreferences.getInstance();
  
  runApp(const MathVerseApp());
}

class MathVerseApp extends StatelessWidget {
  const MathVerseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => CourseProvider()),
      ],
      child: MaterialApp.router(
        title: 'MathVerse',
        theme: ThemeData(
          primarySwatch: Colors.indigo,
          useMaterial3: true,
          fontFamily: 'Inter',
        ),
        routerConfig: _router,
      ),
    );
  }
}

final GoRouter _router = GoRouter(
  initialLocation: '/',
  routes: [
    GoRoute(
      path: '/',
      builder: (context, state) => const SplashScreen(),
    ),
    GoRoute(
      path: '/login',
      builder: (context, state) => const LoginScreen(),
    ),
    GoRoute(
      path: '/home',
      builder: (context, state) => const HomeScreen(),
    ),
    GoRoute(
      path: '/courses/:courseId',
      builder: (context, state) {
        final courseId = int.parse(state.pathParameters['courseId']!);
        return CourseScreen(courseId: courseId);
      },
    ),
    GoRoute(
      path: '/lessons/:lessonId',
      builder: (context, state) {
        final lessonId = int.parse(state.pathParameters['lessonId']!);
        return LessonScreen(lessonId: lessonId);
      },
    ),
    GoRoute(
      path: '/profile',
      builder: (context, state) => const ProfileScreen(),
    ),
  ],
  redirect: (context, state) {
    final authProvider = context.read<AuthProvider>();
    final isAuthenticated = authProvider.isAuthenticated;
    
    // If not authenticated and not on login/splash, redirect to login
    if (!isAuthenticated && !['/', '/login'].contains(state.location)) {
      return '/login';
    }
    
    // If authenticated and on splash/login, redirect to home
    if (isAuthenticated && ['/', '/login'].contains(state.location)) {
      return '/home';
    }
    
    return null;
  },
);