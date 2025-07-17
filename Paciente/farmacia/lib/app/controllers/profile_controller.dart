import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ProfileController extends GetxController{
  final PageController _pageController = PageController(initialPage: 0);
  PageController get pageController => _pageController;

  final RxInt _selectedIndex = 0.obs;
  int get selectedIndex => _selectedIndex.value;

  late final String _name;
  String get name => _name;

  final AuthService _authService = AuthService();

  @override
  void onInit() async {
    // TODO: implement onInit
    super.onInit();
    final user = await _authService.getCurrentUser();
    _name = user?.userMetadata?['nome'] ?? 'Usuário';
  }

  void onPageChanged(int index) {
    _selectedIndex.value = index;
  }

  void onTabTapped(int index) {
    _pageController.animateToPage(index,
        duration: const Duration(milliseconds: 300), curve: Curves.ease);
  }
}