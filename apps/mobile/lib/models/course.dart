import 'package:json_annotation/json_annotation.dart';

part 'course.g.dart';

@JsonSerializable()
class Course {
  final int id;
  final String title;
  final String? description;
  final String level;
  final String subject;
  final double price;
  final bool is_free;
  final String? thumbnail_url;
  final bool is_published;
  final int creator_id;
  final String created_at;
  final String? updated_at;
  @JsonKey(name: 'enrollment_count')
  final int? enrollmentCount;

  Course({
    required this.id,
    required this.title,
    this.description,
    required this.level,
    required this.subject,
    required this.price,
    required this.is_free,
    this.thumbnail_url,
    required this.is_published,
    required this.creator_id,
    required this.created_at,
    this.updated_at,
    this.enrollmentCount,
  });

  factory Course.fromJson(Map<String, dynamic> json) => _$CourseFromJson(json);
  Map<String, dynamic> toJson() => _$CourseToJson(this);
}

@JsonSerializable()
class Lesson {
  final int id;
  final String title;
  final String? description;
  final String? content;
  final int order_index;
  final int course_id;
  final String? video_url;
  final int? video_duration;
  final String? animation_scene_path;
  final String? animation_class;
  final bool is_published;
  final String created_at;
  final String? updated_at;

  Lesson({
    required this.id,
    required this.title,
    this.description,
    this.content,
    required this.order_index,
    required this.course_id,
    this.video_url,
    this.video_duration,
    this.animation_scene_path,
    this.animation_class,
    required this.is_published,
    required this.created_at,
    this.updated_at,
  });

  factory Lesson.fromJson(Map<String, dynamic> json) => _$LessonFromJson(json);
  Map<String, dynamic> toJson() => _$LessonToJson(this);
}

@JsonSerializable()
class User {
  final int id;
  final String email;
  final String username;
  final String full_name;
  final String role;
  final bool is_active;
  final bool is_verified;
  final String? avatar_url;

  User({
    required this.id,
    required this.email,
    required this.username,
    required this.full_name,
    required this.role,
    required this.is_active,
    required this.is_verified,
    this.avatar_url,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}