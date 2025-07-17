import 'package:farmacia/app/controllers/auth_controller.dart';
import 'package:farmacia/app/controllers/login_controller.dart';
import 'package:farmacia/app/controllers/navigation_controller.dart';
import 'package:farmacia/app/controllers/register_controller.dart';
import 'package:get/get.dart';

class InitBindings implements Bindings {
  @override
  void dependencies() {
    Get.put(NavigationController(), permanent: true);
    Get.put(LoginController());
    Get.put(RegisterController());
    Get.put(AuthController(), permanent: true);
  }
}
