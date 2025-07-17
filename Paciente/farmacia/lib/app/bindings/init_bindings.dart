import 'package:farmacia/app/controllers/login_controller.dart';
import 'package:farmacia/app/controllers/navigation_controller.dart';
import 'package:get/get.dart';

class InitBindings implements Bindings {
  @override
  void dependencies() {
    // TODO: implement dependencies
    Get.put(NavigationController(), permanent: true);
    Get.put(LoginController());
  }
}
