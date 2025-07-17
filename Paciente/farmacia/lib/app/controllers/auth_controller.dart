import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AuthController extends GetxController{
  final AuthService _authService = AuthService();

  final Rxn<User> _currentUser = Rxn<User>();

  @override
  void onInit() async{
    // TODO: implement onInit
    super.onInit();

    _currentUser.value = await _authService.getCurrentUser();

    _authService.authStateChanges().listen((data) {
      _currentUser.value = data.session?.user;
      update();
    });
  }

  bool get isAuthenticated => _currentUser.value != null;
}