import 'package:farmacia/app/ui/pages/chat_page.dart';
import 'package:farmacia/app/ui/pages/home_page.dart';
import 'package:farmacia/app/ui/pages/medicines_page.dart';
import 'package:farmacia/app/ui/pages/profile_page.dart';
import 'package:farmacia/app/ui/pages/quizz_page.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class NavigationController extends GetxController{
  final _currentIndex = 0.obs;
  int get currentIndex => _currentIndex.value;

  final List<Widget> pages = const [
    HomePage(),
    ChatPage(),
    MedicinesPage(),
    ProfilePage(),
    QuizzPage(),
  ];

  void changeTab(int index) {
    _currentIndex.value = index;
  }

  Widget get currentPage => pages[_currentIndex.value];
}