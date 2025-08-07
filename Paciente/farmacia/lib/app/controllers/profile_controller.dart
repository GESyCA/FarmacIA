import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ProfileController extends GetxController {
  final PageController _pageController = PageController(initialPage: 0);
  PageController get pageController => _pageController;

  final RxInt _selectedIndex = 0.obs;
  int get selectedIndex => _selectedIndex.value;

  late final String _name;
  String get name => _name;

  final AuthService _authService =
      AuthService(client: Supabase.instance.client);

  final DatabaseService databaseService;

  ProfileController({required this.databaseService});

  final RxList<String> _medicineNames = <String>[].obs;
  List<String> get medicineNames => _medicineNames;

  @override
  void onInit() async {
    // TODO: implement onInit
    super.onInit();
    final user = await _authService.getCurrentUser();
    _name = user?.userMetadata?['nome'] ?? 'Usuário';
    await fetchMedicineNames();
  }

  fetchMedicineNames() async {
    _medicineNames.value = await databaseService.getMedicineNames();
  }

  void onPageChanged(int index) {
    _selectedIndex.value = index;
  }

  void onTabTapped(int index) {
    _pageController.animateToPage(index,
        duration: const Duration(milliseconds: 300), curve: Curves.ease);
  }
}
