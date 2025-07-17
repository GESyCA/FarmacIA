import 'package:farmacia/app/controllers/profile_controller.dart';
import 'package:farmacia/app/ui/widgets/achivements.dart';
import 'package:farmacia/app/ui/widgets/custom_app_bar.dart';
import 'package:farmacia/app/ui/widgets/statistics.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ProfilePage extends GetView<ProfileController> {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(title: 'Perfil'),
      body: Center(
        child: Container(
          width: MediaQuery.of(context).size.width,
          height: MediaQuery.of(context).size.height,
          decoration: BoxDecoration(
            color: Color(0xFFB9160C),
          ),
          child: Column(
            children: <Widget>[
              // header with tabs
              const SizedBox(
                height: 30,
              ),
              _showTabBar(),
              const SizedBox(
                height: 20,
              ),
              _profileCard(),
              const SizedBox(
                height: 32,
              ),
              Expanded(
                child: PageView(
                  controller: controller.pageController,
                  onPageChanged: controller.onPageChanged,
                  children: <Widget>[
                    Statistics(),
                    Achivements(),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Padding _showTabBar() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: LayoutBuilder(builder: (context, constraints) {
        double tabWidth = constraints.maxWidth / 2;
        return Container(
          height: 30,
          decoration: BoxDecoration(
            color: Colors.red[200],
            borderRadius: BorderRadius.circular(20),
          ),
          child: Stack(
            children: <Widget>[
              Obx(() => AnimatedPositioned(
                    duration: const Duration(milliseconds: 300),
                    curve: Curves.easeInOut,
                    top: 0,
                    left: controller.selectedIndex == 0 ? 0 : tabWidth,
                    right: controller.selectedIndex == 0 ? tabWidth : 0,
                    child: Container(
                      // half of the width of the container
                      width: tabWidth,
                      height: 30,
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                      ),
                    ),
                  )),
              Row(
                children: <Widget>[
                  _buildTabButton("ESTATÍSTICAS", 0),
                  _buildTabButton("CONQUISTAS", 1),
                ],
              ),
            ],
          ),
        );
      }),
    );
  }

  Widget _buildTabButton(String title, int index) {
    return Expanded(
      child: GestureDetector(
        onTap: () => controller.onTabTapped(index),
        child: Center(
          child: Obx(() => Text(
                title,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: controller.selectedIndex == index
                      ? Colors.black
                      : Colors.black54,
                ),
              )),
        ),
      ),
    );
  }

  Widget _profileCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Card(
        color: Colors.red[200],
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        elevation: 4,
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: 20, vertical: 15),
          child: Row(
            mainAxisSize: MainAxisSize.max,
            children: [
              CircleAvatar(
                radius: 32,
                backgroundColor: Colors.white,
                child:
                    Icon(Icons.person_outline, size: 30, color: Colors.black),
              ),
              //const SizedBox(width: 20),
              Expanded(
                child: Text(
                  controller.name,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
