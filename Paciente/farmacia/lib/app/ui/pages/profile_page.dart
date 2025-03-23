import 'package:flutter/material.dart';

class ProfilePage extends StatefulWidget {
  const ProfilePage({super.key});

  @override
  State<ProfilePage> createState() => _ProfilePageState();
}

class _ProfilePageState extends State<ProfilePage> {
  PageController _pageController = PageController(initialPage: 0);
  int _selectedIndex = 0;
  final String _name = "Antonio Neto";

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
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _buildTabButton("ESTATÍSTICAS", 0),
                  _buildTabButton("CONQUISTAS", 1),
                ],
              ),
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

  Widget _buildTabButton(String title, int index) {
    return GestureDetector(
      onTap: () => _onTabTapped(index),
      child: Container(
        padding: EdgeInsets.symmetric(vertical: 8, horizontal: 16),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          color: _selectedIndex == index ? Colors.white : Colors.transparent,
        ),
        child: Text(
          title,
          style: TextStyle(
            color: _selectedIndex == index ? Colors.red : Colors.white,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  _profileCard() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Card(
        child: ListTile(
          title: Text(
            _name,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          leading: Icon(
            Icons.account_circle,
            color: Colors.red,
            size: 50,
          ),
        ),
      ),
    );
  }
}
