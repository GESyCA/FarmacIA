import 'package:farmacia/app/controllers/medicine_controller.dart';
import 'package:farmacia/app/controllers/navigation_controller.dart';
import 'package:farmacia/app/controllers/profile_controller.dart';
import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AuthController extends GetxController {
  final AuthService _authService = AuthService(
    client: Supabase.instance.client,
  );

  final Rxn<User> _currentUser = Rxn<User>();

  final RxBool _isLoading = false.obs;
  get isLoading => _isLoading.value;

  @override
  void onInit() async {
    // TODO: implement onInit
    super.onInit();

    _currentUser.value = await _authService.getCurrentUser();

    _authService.authStateChanges().listen((data) {
      _currentUser.value = data.session?.user;
      update();
    });
  }

  bool get isAuthenticated => _currentUser.value != null;

  Future<void> signOut() async {
    try {
      _isLoading.value = true;
      if (Get.isRegistered<ProfileController>()) {
        Get.delete<ProfileController>();
        print("ProfileController deletado.");
      }

      if (Get.isRegistered<MedicineController>()) {
        Get.delete<MedicineController>();
        print("MedicineController deletado.");
      }

      if (Get.isRegistered<DatabaseService>()) {
        Get.delete<DatabaseService>();
        print("DatabaseService deletado.");
      }

      // Só para voltar para a primeira aba (Home)
      if (Get.isRegistered<NavigationController>()) {
        Get.find<NavigationController>().resetController();
      }

      Get.back();

      await _authService.signOut();
    } on Exception catch (e) {
      // TODO
      Get.snackbar(
        'Erro no Logout',
        'Não foi possível sair. Tente novamente.',
        backgroundColor: Colors.red.withOpacity(0.8),
        colorText: Colors.white,
      );
      print("Erro durante o signOut: $e");
    } finally {
      // Limpeza de recursos ou navegação
      _isLoading.value = false;
    }
  }
}
