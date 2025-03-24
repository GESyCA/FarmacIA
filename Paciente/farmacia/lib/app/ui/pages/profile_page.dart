import 'package:flutter/material.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  final PageController _pageController = PageController(initialPage: 0);
  int _selectedIndex = 0;
  final String _name = "Antônio Neto";

  void _onPageChanged(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  void _onTabTapped(int index) {
    _pageController.animateToPage(index,
        duration: const Duration(milliseconds: 300), curve: Curves.ease);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        centerTitle: true,
        title: const Text("Perfil"),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_circle),
            onPressed: () {
              Navigator.pushNamed(context, '/login');
            },
          ),
        ],
      ),
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
                height: 42,
              ),
              Expanded(
                child: PageView(
                  controller: _pageController,
                  onPageChanged: _onPageChanged,
                  children: <Widget>[
                    Container(
                      color: Colors.white,
                      child: Center(
                        child: Text("Estatísticas"),
                      ),
                    ),
                    Container(
                      color: Colors.white,
                      child: Center(
                        child: Text("Conquistas"),
                      ),
                    ),
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
              AnimatedPositioned(
                duration: const Duration(milliseconds: 300),
                curve: Curves.easeInOut,
                top: 0,
                left: _selectedIndex == 0 ? 0 : tabWidth,
                right: _selectedIndex == 0 ? tabWidth : 0,
                child: Container(
                  // half of the width of the container
                  width: tabWidth,
                  height: 30,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                  ),
                ),
              ),
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
        onTap: () => _onTabTapped(index),
        child: Center(
          child: Text(
            title,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: _selectedIndex == index ? Colors.black : Colors.black54,
            ),
          ),
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
                  _name,
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
