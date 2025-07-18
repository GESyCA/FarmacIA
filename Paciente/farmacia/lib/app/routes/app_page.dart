import 'package:farmacia/app/bindings/profile_binding.dart';
import 'package:farmacia/app/routes/app_routes.dart';
import 'package:farmacia/app/ui/navigation_menu.dart';
import 'package:farmacia/app/ui/pages/add_medicine_page.dart';
import 'package:farmacia/app/ui/pages/auth_page.dart';
import 'package:farmacia/app/ui/pages/chat_page.dart';
import 'package:farmacia/app/ui/pages/home_page.dart';
import 'package:farmacia/app/ui/pages/login_page.dart';
import 'package:farmacia/app/ui/pages/profile_page.dart';
import 'package:farmacia/app/ui/pages/quizz_page.dart';
import 'package:farmacia/app/ui/pages/register_page.dart';
import 'package:get/get.dart';

class AppPage {
  final List<GetPage> pages = [
    GetPage(
      name: Routes.home,
      page: () => HomePage(),
    ),
    GetPage(
      name: Routes.login,
      page: () => LoginPage(),
    ),
    GetPage(
      name: Routes.navigation,
      page: () => NavigationMenu(),
    ),
    GetPage(
      name: Routes.chat,
      page: () => ChatPage(),
    ),
    GetPage(
      name: Routes.add_medicine,
      page: () => AddMedicinePage(),
    ),
    GetPage(
      name: Routes.register,
      page: () => RegisterPage(),
    ),
    GetPage(
      name: Routes.initial,
      page: () => AuthPage(),
    ),
    GetPage(
      name: Routes.profile,
      page: () => ProfilePage(),
      binding: ProfileBinding()
    ),
    GetPage(
      name: Routes.quizz,
      page: () => QuizzPage(),
    ),
  ];
}