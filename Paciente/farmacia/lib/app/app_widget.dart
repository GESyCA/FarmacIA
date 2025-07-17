import 'package:farmacia/app/bindings/init_bindings.dart';
import 'package:farmacia/app/routes/app_page.dart';
import 'package:farmacia/app/routes/app_routes.dart';
import 'package:flutter/material.dart';
import 'package:get/get_navigation/src/root/get_material_app.dart';

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return GetMaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Farmacia',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      initialRoute: Routes.login,
      initialBinding: InitBindings(),
      getPages: AppPage().pages,
    );
  }
}