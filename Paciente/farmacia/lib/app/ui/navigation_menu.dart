import 'package:farmacia/app/controllers/navigation_controller.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class NavigationMenu extends GetView<NavigationController> {
  const NavigationMenu({super.key});

  @override
  Widget build(BuildContext context) {
    return Obx(() => Scaffold(
          body: IndexedStack(
            index: controller.currentIndex,
            children: controller.pages,
          ),
          bottomNavigationBar: BottomNavigationBar(
            currentIndex: controller.currentIndex,
            onTap: controller.changeTab,
            items: const [
              BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Home'),
              BottomNavigationBarItem(icon: Icon(Icons.chat), label: 'Chat'),
              BottomNavigationBarItem(icon: Icon(Icons.local_pharmacy), label: 'Medicamentos'),
              BottomNavigationBarItem(icon: Icon(Icons.description), label: 'Perfil'),
              BottomNavigationBarItem(icon: Icon(Icons.quiz_outlined), label: 'Quizz'),
            ],
            selectedItemColor: Colors.red,
            unselectedItemColor: Colors.grey,
            backgroundColor: Colors.white,
            type: BottomNavigationBarType.fixed,
          ),
        ));
  }
}
